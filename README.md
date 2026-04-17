# Signara Platform (Scaffold)

## Quick Start

```bash

pip install -r app/requirements.txt

export PYTHONPYCACHEPREFIX="$HOME/.cache/signara-platform/pycache"
python -m uvicorn app.main:app --reload

```
When you start with the default command the app will attempt to automatically open your default browser to the running server URL. The port is detected dynamically: if you pass --port 8001 it will open http://127.0.0.1:8001/. (Auto‑open can be disabled, see below.)

If you want to host the application and allow access from another device via SSH, use the following command:
```bash
export PYTHONPYCACHEPREFIX="$HOME/.cache/signara-platform/pycache"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

### Running From Inside the `app/` Directory

Because the code uses package-relative imports, the recommended invocation always references `app.main:app` and ensures the parent folder (containing the `app` package) is on `PYTHONPATH`.

From inside `app/` you have two options:

1. Use `--app-dir ..` (uvicorn adds parent to sys.path):
  ```powershell
  # PowerShell in app/ directory
  $env:PYTHONPYCACHEPREFIX = "$HOME/.cache/signara-platform/pycache"
  uvicorn --app-dir .. app.main:app --reload --host 0.0.0.0 --port 8003
  ```

2. Rely on added fallback imports in `main.py` and run module locally:
  ```powershell
  # PowerShell in app/ directory
  $env:PYTHONPYCACHEPREFIX = "$HOME/.cache/signara-platform/pycache"
  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8003
  ```
  (Fallback logic catches the relative import error and switches to direct imports.)

3. Explicitly set PYTHONPATH to parent (portable):
  ```powershell
  $env:PYTHONPYCACHEPREFIX = "$HOME/.cache/signara-platform/pycache"
  $env:PYTHONPATH = (Resolve-Path ..).Path
  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
  ```

If you encounter `ImportError: attempted relative import with no known parent package`, use option 1 or 3.
```
```


Open: http://127.0.0.1:<port>/ (defaults to 8000 if not specified)

Disable auto‑open (any method):

```bash
set TIMING_AUTO_OPEN_BROWSER=false   # Windows PowerShell: $env:TIMING_AUTO_OPEN_BROWSER='false'
```

Or add to a local .env file: `TIMING_AUTO_OPEN_BROWSER=false`.

### Desktop "App Mode" (Embedded Window)

If you'd prefer a desktop-style window instead of opening a browser:

```
pip install -r app/requirements.txt  # ensure pywebview + requests installed
$env:PYTHONPYCACHEPREFIX = "$HOME/.cache/signara-platform/pycache"
python app_mode.py
```

This launches uvicorn in the background and opens a native window (via pywebview or PyQt).

Backend priority (auto mode): pywebview -> PyQt -> browser fallback.

Force a backend:
```
$env:PYTHONPYCACHEPREFIX = "$HOME/.cache/signara-platform/pycache"
python app_mode.py --backend webview
$env:PYTHONPYCACHEPREFIX = "$HOME/.cache/signara-platform/pycache"
python app_mode.py --backend pyqt
$env:PYTHONPYCACHEPREFIX = "$HOME/.cache/signara-platform/pycache"
python app_mode.py --browser          # always use external browser
```

Remote / LAN access (serve to other machines):
```
# Bind on all interfaces, fixed port 8000
$env:PYTHONPYCACHEPREFIX = "$HOME/.cache/signara-platform/pycache"
python app_mode.py --host 0.0.0.0 --port 8000 --backend webview

# If port 8000 might be busy but you still want remote access, allow scanning:
python app_mode.py --host 0.0.0.0 --port 8000 --flex-port --backend pyqt
```
Then on another machine (having network route / SSH tunnel) open:
  http://<your_host_ip>:<port>/
If you used --flex-port, watch the console output for the chosen port and remote access URL hints.

Override launch URL explicitly (skips detection) by setting:
  Windows PowerShell: $env:TIMING_BASE_URL='http://127.0.0.1:9000/'
  bash: export TIMING_BASE_URL=http://127.0.0.1:9000/

Linux notes:
If you see a message about missing GTK/Qt bindings you can install either stack:
GTK (Ubuntu/Debian):
  sudo apt-get update && sudo apt-get install -y python3-gi gir1.2-webkit2-4.1 libwebkit2gtk-4.1-0
Qt (cross‑distro via pip):
  pip install PyQt5 PyQtWebEngine
Then re-run: python app_mode.py



## Structure (High-Level Excerpt)

```
app/
  main.py                      # FastAPI app entry (mounts /static from presentation)
  presentation/
    templates/                 # Jinja2 templates (base + feature pages)
    static/                    # Static assets (js/, css/, images/, fonts/)
  interface/
    http/routers/              # FastAPI routers (Explorer, Timing SAF, QC, etc.)
    http/schemas/              # Pydantic request/response models
    http/dependencies.py       # Dependency providers for use cases
  application/                 # Use case modules (orchestrating domain + ports)
  domain/                      # Entities, value objects, repository protocols
  infrastructure/              # FS, Perforce, processes, caching, logging implementations
  logging_config.py            # Logging setup
  settings.py                  # Pydantic Settings
  config.py                    # Path resolution utilities
```


## Front-End & Styling

Currently uses CDN TailwindCSS + DaisyUI for rapid iteration. To adopt a richer front-end pipeline later:

1. Introduce a lightweight build (npm + Tailwind CLI) under `presentation/static/` for purging + minification.
2. Add cache-busting via hashed filenames (adjust `/static` mount or template references).
3. Move larger JS features into ES modules with feature directories (already started for Explorer).
4. Optional: integrate Playwright tests under `tests/e2e/` once interactivity grows.

Until then the CDN approach keeps complexity low.

### Offline CSS (Short)
Run once after class/config changes:
```
npm install
npm run build:css
```
Serves `/static/css/tailwind-daisyui.css`. See `docs/STYLING_OFFLINE_BUILD.md`.

### Gantt Chart Integration
To build and copy the Gantt Timeline Creation (Community) tool into the presentation static assets, run the following PowerShell commands:
```
Push-Location "C:\github\app\utils\Gantt Timeline Creation (Community)"
npm run build
Copy-Item -Path "C:\github\app\utils\Gantt Timeline Creation (Community)\build\*" -Destination "C:\github\app\presentation\static\gantt" -Recurse -Force
```

## License

Internal / Proprietary

