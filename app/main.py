"""Application entry point.

Refactored to use an application factory for easier testing & future
configuration of logging or dependency overrides.
"""
import os
import sys
from pathlib import Path as _PathForSys, Path


def _configure_pycache_prefix() -> None:
    configured_prefix = os.environ.get("PYTHONPYCACHEPREFIX")
    if not configured_prefix:
        configured_prefix = str(Path.home() / ".cache" / "signara-platform" / "pycache")
        os.environ["PYTHONPYCACHEPREFIX"] = configured_prefix

    try:
        Path(configured_prefix).mkdir(parents=True, exist_ok=True)
        sys.pycache_prefix = configured_prefix
    except OSError:
        pass


_configure_pycache_prefix()

# Ensure the parent directory (which contains the 'app' package) is on sys.path.
# This is defensive when launching from nested working directories.
_parent = _PathForSys(__file__).resolve().parent.parent
_parent_str = str(_parent)
if _parent_str not in sys.path:
    sys.path.insert(0, _parent_str)

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Use stable absolute imports (avoid try/except that hid real errors)
from app.infrastructure.settings.settings import get_settings
from app.infrastructure.logging.logging_config import configure_logging, get_logger
from app.interface.http.routers import discover_routers
import threading
import webbrowser
import platform
from contextlib import asynccontextmanager
import time
import subprocess

# Simple in‑process guard so we don't try to open multiple tabs
_browser_opened = False

# Unique server instance ID to detect restarts (used by frontend to clear storage)
_server_instance_id = str(int(time.time() * 1000))


def _save_network_config():
    """Run ifconfig/ipconfig and save output to ~/.timecraft_ifconfig"""
    try:
        # Determine which command to use based on OS
        if platform.system() == "Windows":
            cmd = ["ipconfig"]
        else:
            cmd = ["ifconfig"]
        
        # Run the command and capture output
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        output = result.stdout
        
        # Save to home directory
        home = Path.home()
        output_file = home / ".timecraft_ifconfig"
        output_file.write_text(output, encoding="utf-8")
        
        # log = get_logger("startup")
        # log.info(f"Network config saved to {output_file}")
    except Exception as e:
        log = get_logger("startup")
        log.warning(f"Failed to save network config: {e}")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    log = get_logger("startup")

    @asynccontextmanager
    async def lifespan(app: FastAPI):  # Modern lifespan hook replacing deprecated on_event
        global _browser_opened
        # Startup phase
        # Save network configuration to home directory
        _save_network_config()
        
        if (
            not _browser_opened
            and settings.auto_open_browser
            and os.environ.get("TIMING_RUNNING_IN_APP_MODE") != "1"  # suppress in embedded app_mode launcher
        ):
            if not os.environ.get("CI"):
                if not (platform.system() == "Linux" and not os.environ.get("DISPLAY")):
                    def _resolve_launch_url() -> str:
                        """Figure out which URL the dev server will be on.

                        Precedence:
                        1. Explicit TIMING_BASE_URL environment variable
                        2. Parse host/port from current process args (uvicorn invocation)
                        3. Fallback to 127.0.0.1:8000
                        """
                        env_url = os.environ.get("TIMING_BASE_URL")
                        if env_url:
                            return env_url.rstrip("/") + "/"

                        # Defaults
                        host = "127.0.0.1"
                        port = "8000"

                        # Try to parse from argv when launched as: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
                        # or uvicorn app.main:app --host 0.0.0.0 --port 8001
                        try:
                            argv = sys.argv
                            # If run with -m uvicorn, actual uvicorn args come after the module spec
                            # We'll just scan the whole list for flags.
                            for i, a in enumerate(argv):
                                if a in {"--host", "-h"} and i + 1 < len(argv):
                                    host = argv[i + 1]
                                elif a in {"--port", "-p"} and i + 1 < len(argv):
                                    port = argv[i + 1]
                        except Exception:
                            pass

                        # If host is 0.0.0.0 we can't open that in browser; map to localhost.
                        if host in ("0.0.0.0", "::"):
                            host_for_browser = "127.0.0.1"
                        else:
                            host_for_browser = host
                        return f"http://{host_for_browser}:{port}/"

                    def _open():
                        url = _resolve_launch_url()
                        try:
                            # Try Chrome with password-store=basic flag first
                            import subprocess
                            chrome_commands = [
                                ["google-chrome", "--password-store=basic", url],  # Linux
                                ["chrome", "--password-store=basic", url],  # Linux alternative
                                [r"C:\Program Files\Google\Chrome\Application\chrome.exe", "--password-store=basic", url],  # Windows
                                [r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", "--password-store=basic", url],  # Windows 32-bit
                            ]
                            opened = False
                            for cmd in chrome_commands:
                                try:
                                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                    opened = True
                                    break
                                except (FileNotFoundError, OSError):
                                    continue
                            
                            # Fallback to default browser if Chrome not found
                            if not opened:
                                webbrowser.open(url)
                        except Exception:
                            pass
                    threading.Timer(0.7, _open).start()
                    _browser_opened = True
        yield  # Application running
        # (No shutdown logic needed currently)

    app = FastAPI(title="TimeCraft Platform", version="0.1.0", docs_url="/docs", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def _static_cache_control(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = settings.static_cache_control
            cache_control_lower = settings.static_cache_control.lower()
            if any(token in cache_control_lower for token in ("no-cache", "no-store", "max-age=0")):
                # Extra compatibility for older caching behavior
                response.headers.setdefault("Pragma", "no-cache")
                response.headers.setdefault("Expires", "0")
        return response

    # Resolve presentation/static irrespective of current working directory.
    # This allows launching from project root or from inside the app package.
    app_root = Path(__file__).resolve().parent
    static_dir = app_root / "presentation" / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    # Expose the .cache folder relative to current working directory (same as backend logic)
    cache_dir = Path(".cache")
    cache_dir.mkdir(parents=True, exist_ok=True)  # Ensure .cache exists before mounting
    app.mount("/cache", StaticFiles(directory=str(cache_dir)), name="cache")
    # Serve theme images for background customization
    theme_dir = app_root / "theme"
    if theme_dir.exists():
        app.mount("/theme", StaticFiles(directory=str(theme_dir)), name="theme")

    # Auto-discover and register all routers
    # Order is controlled by ROUTER_PRIORITY in interface/http/routers/__init__.py
    for router in discover_routers():
        app.include_router(router)

    # Store pages for backwards compatibility (if needed by legacy code)
    from app.application.dashboard.use_cases import GetNavigationMenu
    menu = GetNavigationMenu().execute()
    app.state.pages = [(p.page_id, p.title) for p in menu.pages]

    @app.get("/health")
    async def health():  # simple ping
        from app import __version__
        return {"status": "ok", "version": __version__}

    @app.get("/api/server-instance")
    async def get_server_instance():
        """Return unique server instance ID for detecting restarts."""
        return {"instance_id": _server_instance_id}

    @app.get("/api/config/base-path")
    async def get_base_path():
        """Return the PROJECTS_BASE path for frontend use."""
        # Use absolute import so this works whether uvicorn is launched as 'app.main:app'
        # or the working directory is inside the 'app' folder. Relative import fails
        # when invoked as 'python -m uvicorn main:app' because 'main' isn't part of a package then.
        from app.infrastructure.fs.project_root import PROJECTS_BASE
        return {"base_path": str(PROJECTS_BASE)}

    log.info("App created (environment=%s, cors=%s)", settings.environment, settings.cors_origins)
    return app


# Instance used by uvicorn import style (uvicorn app.main:app --reload)
app = create_app()

