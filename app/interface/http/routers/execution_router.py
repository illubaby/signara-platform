"""Generic Execution Router - Reusable WebSocket Script Execution

This router provides a generic WebSocket endpoint for executing scripts/commands
with real-time output streaming. It can be used by any feature that needs to
run scripts and display output.

Clean Architecture: Interface Layer (HTTP adapters)
"""

from pathlib import Path
from typing import Optional
from fastapi import APIRouter, WebSocket, Query, HTTPException
from fastapi.websockets import WebSocketDisconnect
from app.infrastructure.websocket.stream_executor import WebSocketStreamExecutor
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/execute", tags=["execution"])


@router.websocket("/stream")
async def execute_script_stream(
    websocket: WebSocket,
    script_path: str = Query(..., description="Absolute path to script file"),
    working_dir: str = Query(..., description="Working directory for execution"),
    shell: str = Query(default="/bin/bash", description="Shell to use (bash, csh, sh, python, etc.)")
):
    """Generic WebSocket endpoint for script execution with real-time output streaming.
    
    This is a reusable endpoint that can be called from any feature needing
    script execution with live output feedback.
    
    **Usage Examples:**
    ```
    ws://host/api/execute/stream?script_path=/path/to/script.sh&working_dir=/work/dir&shell=/bin/bash
    ```
    
    **WebSocket Protocol:**
    - Client → Server: `{"action": "stop"}` to terminate execution
    - Server → Client: 
        - `{"stream": "stdout", "data": "output text"}` for output lines
        - `{"event": "error", "detail": "error message"}` on error
        - `{"event": "end", "return_code": 0, "stopped": false}` on completion
    
    **Security Note:**
    This endpoint executes arbitrary scripts. In production, implement:
    - Path validation (whitelist allowed directories)
    - User authentication/authorization
    - Resource limits (timeout, memory)
    """
    await websocket.accept()
    
    try:
        # Validate paths
        script_path_obj = Path(script_path)
        working_dir_obj = Path(working_dir)
        
        if not script_path_obj.exists():
            await websocket.send_json({
                "event": "error",
                "detail": f"Script not found: {script_path}"
            })
            await websocket.close()
            return
        
        if not working_dir_obj.exists():
            await websocket.send_json({
                "event": "error",
                "detail": f"Working directory not found: {working_dir}"
            })
            await websocket.close()
            return
        
        # Security: Validate shell path (basic check)
        allowed_shells = ["/bin/bash", "/bin/sh", "/bin/csh", "/bin/tcsh", "/bin/zsh", "python", "python3"]
        if shell not in allowed_shells and not Path(shell).exists():
            await websocket.send_json({
                "event": "error",
                "detail": f"Invalid or unsupported shell: {shell}"
            })
            await websocket.close()
            return
        
        logger.info(f"[ExecutionRouter] Starting script: {script_path} in {working_dir} with {shell}")
        
        # Use reusable WebSocketStreamExecutor
        executor = WebSocketStreamExecutor(websocket)
        result = await executor.execute_script(
            script_path=script_path_obj,
            working_dir=working_dir_obj,
            shell=shell
        )
        
        logger.info(f"[ExecutionRouter] Completed with return code: {result.return_code}")
        
        # Close WebSocket
        try:
            await websocket.close()
        except Exception:
            pass
            
    except WebSocketDisconnect:
        logger.info("[ExecutionRouter] Client disconnected")
    except Exception as e:
        logger.error(f"[ExecutionRouter] Unexpected error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "event": "error",
                "detail": f"Unexpected error: {e}"
            })
            await websocket.close()
        except Exception:
            pass


@router.websocket("/command")
async def execute_command_stream(
    websocket: WebSocket,
    command: str = Query(..., description="Command to execute (e.g., 'ls -la')"),
    working_dir: str = Query(..., description="Working directory for execution")
):
    """Execute a shell command (not a script file) with real-time output streaming.
    
    **Example:**
    ```
    ws://host/api/execute/command?command=ls%20-la&working_dir=/tmp
    ```
    
    **Note:** This is more flexible but also more dangerous. Consider authentication.
    """
    await websocket.accept()
    
    try:
        working_dir_obj = Path(working_dir)
        
        if not working_dir_obj.exists():
            await websocket.send_json({
                "event": "error",
                "detail": f"Working directory not found: {working_dir}"
            })
            await websocket.close()
            return
        
        # Send execution info with absolute path before starting
        absolute_working_dir = str(working_dir_obj.absolute())
        await websocket.send_json({
            "event": "info",
            "working_dir_absolute": absolute_working_dir,
            "command": command
        })
        
        logger.info(f"[ExecutionRouter] Running command: {command} in {working_dir}")
        logger.info(f"[ExecutionRouter] Absolute path: {absolute_working_dir}")
        
        # Detect if command contains shell operators
        shell_operators = ['&&', '||', '|', ';', '>', '<', '>>', '<<', '&']
        needs_shell = any(op in command for op in shell_operators)
        
        # Use WebSocketStreamExecutor
        executor = WebSocketStreamExecutor(websocket)
        
        if needs_shell:
            # Execute through shell to handle operators like &&, ||, etc.
            logger.info(f"[ExecutionRouter] Detected shell operators, using shell mode")
            result = await executor.execute_shell_command(
                command=command,
                working_dir=working_dir_obj,
                shell="/bin/bash"
            )
        else:
            # Parse command into list for direct execution
            import shlex
            try:
                cmd_list = shlex.split(command)
            except ValueError as e:
                await websocket.send_json({
                    "event": "error",
                    "detail": f"Invalid command syntax: {e}"
                })
                await websocket.close()
                return
            
            result = await executor.execute_command(
                command=cmd_list,
                working_dir=working_dir_obj
            )
        
        logger.info(f"[ExecutionRouter] Command completed with return code: {result.return_code}")
        
        try:
            await websocket.close()
        except Exception:
            pass
            
    except WebSocketDisconnect:
        logger.info("[ExecutionRouter] Client disconnected")
    except Exception as e:
        logger.error(f"[ExecutionRouter] Unexpected error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "event": "error",
                "detail": f"Unexpected error: {e}"
            })
            await websocket.close()
        except Exception:
            pass
