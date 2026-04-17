from fastapi import APIRouter, HTTPException
import subprocess
import os
import logging

router = APIRouter(prefix="/api/code-server", tags=["code-server"])
logger = logging.getLogger(__name__)

# Track if code-server is already running
_code_server_process = None


@router.post("/start")
async def start_code_server():
    """Start code-server and return the URL to access it."""
    global _code_server_process
    
    try:
        # Check if already running
        if _code_server_process is not None and _code_server_process.poll() is None:
            logger.info("Code-server is already running")
            return {
                "status": "already_running",
                "url": "http://0.0.0.0:8080",
                "message": "Code-server is already running"
            }
        
        # Path to code-server binary
        code_server_path = "./code-server-4.106.2-linux-amd64/bin/code-server"
        
        # Check if code-server binary exists
        if not os.path.exists(code_server_path):
            logger.error(f"Code-server binary not found at {code_server_path}")
            raise HTTPException(
                status_code=404,
                detail=f"Code-server binary not found at {code_server_path}"
            )
        
        # Start code-server in background
        logger.info("Starting code-server...")
        _code_server_process = subprocess.Popen(
            [code_server_path, "--auth", "none", "--bind-addr", "0.0.0.0:8080"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True  # Detach from parent process
        )
        
        logger.info(f"Code-server started with PID {_code_server_process.pid}")
        
        return {
            "status": "started",
            "url": "http://0.0.0.0:8080",
            "pid": _code_server_process.pid,
            "message": "Code-server started successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to start code-server: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start code-server: {str(e)}")


@router.get("/status")
async def get_status():
    """Check if code-server is running."""
    global _code_server_process
    
    if _code_server_process is None:
        return {"status": "not_started", "running": False}
    
    if _code_server_process.poll() is None:
        return {
            "status": "running",
            "running": True,
            "pid": _code_server_process.pid,
            "url": "http://0.0.0.0:8080"
        }
    else:
        return {
            "status": "stopped",
            "running": False,
            "exit_code": _code_server_process.returncode
        }
