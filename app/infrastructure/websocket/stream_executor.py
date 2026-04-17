"""WebSocket Stream Executor - Infrastructure Component

Reusable async process executor that streams output via WebSocket.
Follows Clean Architecture principles - this is an Infrastructure component
that can be injected into any use case requiring real-time script execution.

Usage:
    from app.infrastructure.websocket.stream_executor import WebSocketStreamExecutor
    
    executor = WebSocketStreamExecutor(websocket)
    result = await executor.execute_script(
        script_path="/path/to/script.sh",
        working_dir="/working/directory",
        on_start=lambda: print("Started"),
        on_complete=lambda rc: print(f"Completed with code {rc}")
    )
"""

import asyncio
import os
import signal
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect


class ExecutionResult:
    """Result of script execution."""
    
    def __init__(
        self,
        return_code: int,
        stopped_by_user: bool = False,
        error: Optional[str] = None
    ):
        self.return_code = return_code
        self.stopped_by_user = stopped_by_user
        self.error = error
        self.success = return_code == 0 and not error


class WebSocketStreamExecutor:
    """Execute scripts and stream output via WebSocket in real-time.
    
    This infrastructure component handles:
    - Subprocess management with async I/O
    - Real-time output streaming to WebSocket client
    - Bidirectional communication (receive stop signals)
    - Proper cleanup and error handling
    - ANSI color preservation
    """
    
    def __init__(self, websocket: WebSocket):
        """Initialize executor with WebSocket connection.
        
        Args:
            websocket: Active WebSocket connection (must be accepted already)
        """
        self.websocket = websocket
        self.process: Optional[asyncio.subprocess.Process] = None
        
    async def execute_script(
        self,
        script_path: Path | str,
        working_dir: Optional[Path | str] = None,
        shell: str = "/bin/csh",
        env: Optional[Dict[str, str]] = None,
        on_start: Optional[Callable[[], Any]] = None,
        on_complete: Optional[Callable[[int], Any]] = None,
        setup_messages: Optional[list[str]] = None
    ) -> ExecutionResult:
        """Execute a script and stream output via WebSocket.
        
        Args:
            script_path: Path to script file to execute
            working_dir: Working directory for execution (defaults to script directory)
            shell: Shell to use (default: /bin/csh)
            env: Environment variables (defaults to current process env)
            on_start: Optional callback when process starts
            on_complete: Optional callback when process completes (receives return code)
            setup_messages: Optional list of setup messages to send before execution
            
        Returns:
            ExecutionResult with return code, success status, and metadata
        """
        script_path = Path(script_path)
        
        if not script_path.exists():
            error_msg = f"Script not found: {script_path}"
            await self._send_error(error_msg)
            return ExecutionResult(return_code=-1, error=error_msg)
        
        if working_dir is None:
            working_dir = script_path.parent
        else:
            working_dir = Path(working_dir)
            
        # Send setup messages if provided
        if setup_messages:
            for msg in setup_messages:
                await self._send_output(msg)
        
        # Prepare environment
        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)
        # Force unbuffered output for Python scripts
        exec_env.setdefault("PYTHONUNBUFFERED", "1")
        
        # Start process
        try:
            # start_new_session=True places the subprocess in its own process group
            # so we can reliably terminate all children, not just the shell.
            self.process = await asyncio.create_subprocess_exec(
                shell, script_path.name,
                cwd=str(working_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,  # Merge stderr into stdout
                env=exec_env,
                start_new_session=True,
            )
        except FileNotFoundError:
            error_msg = f"Shell not found: {shell}"
            await self._send_error(error_msg)
            return ExecutionResult(return_code=-1, error=error_msg)
        except Exception as e:
            error_msg = f"Failed to start process: {e}"
            await self._send_error(error_msg)
            return ExecutionResult(return_code=-1, error=str(e))
        
        # Notify start
        if on_start:
            on_start()
        
        # Stream output and handle stop signals
        stopped = False
        try:
            stopped = await self._stream_output_loop()
        except Exception as e:
            # Ensure process is terminated on error
            await self._terminate_process()
            error_msg = f"Streaming error: {e}"
            await self._send_error(error_msg)
            return ExecutionResult(return_code=-1, error=str(e))
        
        # Wait for process completion
        if self.process and self.process.returncode is None:
            return_code = await self.process.wait()
        else:
            return_code = self.process.returncode if self.process else -1
        
        # Send completion event
        try:
            await self.websocket.send_json({
                "event": "end",
                "return_code": return_code,
                "stopped": stopped
            })
        except Exception:
            pass  # Client may have disconnected
        
        # Notify completion
        if on_complete:
            on_complete(return_code)
        
        return ExecutionResult(
            return_code=return_code,
            stopped_by_user=stopped
        )
    
    async def execute_command(
        self,
        command: list[str],
        working_dir: Path | str,
        env: Optional[Dict[str, str]] = None,
        on_start: Optional[Callable[[], Any]] = None,
        on_complete: Optional[Callable[[int], Any]] = None,
        setup_messages: Optional[list[str]] = None
    ) -> ExecutionResult:
        """Execute a command directly (not a script file).
        
        Args:
            command: Command and arguments as list (e.g., ['python', 'script.py'])
            working_dir: Working directory for execution
            env: Environment variables
            on_start: Optional callback when process starts
            on_complete: Optional callback when process completes
            setup_messages: Optional list of setup messages to send before execution
            
        Returns:
            ExecutionResult with return code and metadata
        """
        working_dir = Path(working_dir)
        
        # Send setup messages
        if setup_messages:
            for msg in setup_messages:
                await self._send_output(msg)
        
        # Prepare environment
        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)
        exec_env.setdefault("PYTHONUNBUFFERED", "1")
        
        # Start process
        try:
            self.process = await asyncio.create_subprocess_exec(
                *command,
                cwd=str(working_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=exec_env,
                start_new_session=True,
            )
        except Exception as e:
            error_msg = f"Failed to start command: {e}"
            await self._send_error(error_msg)
            return ExecutionResult(return_code=-1, error=str(e))
        
        if on_start:
            on_start()
        
        # Stream output
        stopped = False
        try:
            stopped = await self._stream_output_loop()
        except Exception as e:
            await self._terminate_process()
            error_msg = f"Streaming error: {e}"
            await self._send_error(error_msg)
            return ExecutionResult(return_code=-1, error=str(e))
        
        # Wait for completion
        if self.process and self.process.returncode is None:
            return_code = await self.process.wait()
        else:
            return_code = self.process.returncode if self.process else -1
        
        # Send completion event
        try:
            await self.websocket.send_json({
                "event": "end",
                "return_code": return_code,
                "stopped": stopped
            })
        except Exception:
            pass
        
        if on_complete:
            on_complete(return_code)
        
        return ExecutionResult(
            return_code=return_code,
            stopped_by_user=stopped
        )
    
    async def execute_shell_command(
        self,
        command: str,
        working_dir: Path | str,
        shell: str = "/bin/bash",
        env: Optional[Dict[str, str]] = None,
        on_start: Optional[Callable[[], Any]] = None,
        on_complete: Optional[Callable[[int], Any]] = None,
        setup_messages: Optional[list[str]] = None
    ) -> ExecutionResult:
        """Execute a shell command string (supports operators like &&, ||, |, etc.).
        
        Args:
            command: Command string with shell operators (e.g., 'cmd1 && cmd2 || cmd3')
            working_dir: Working directory for execution
            shell: Shell to use (default: /bin/bash)
            env: Environment variables
            on_start: Optional callback when process starts
            on_complete: Optional callback when process completes
            setup_messages: Optional list of setup messages to send before execution
            
        Returns:
            ExecutionResult with return code and metadata
        """
        working_dir = Path(working_dir)
        
        # Send setup messages
        if setup_messages:
            for msg in setup_messages:
                await self._send_output(msg)
        
        # Prepare environment
        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)
        exec_env.setdefault("PYTHONUNBUFFERED", "1")
        
        # Start process using shell
        try:
            self.process = await asyncio.create_subprocess_exec(
                shell, "-c", command,
                cwd=str(working_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=exec_env,
                start_new_session=True,
            )
        except Exception as e:
            error_msg = f"Failed to start shell command: {e}"
            await self._send_error(error_msg)
            return ExecutionResult(return_code=-1, error=str(e))
        
        if on_start:
            on_start()
        
        # Stream output
        stopped = False
        try:
            stopped = await self._stream_output_loop()
        except Exception as e:
            await self._terminate_process()
            error_msg = f"Streaming error: {e}"
            await self._send_error(error_msg)
            return ExecutionResult(return_code=-1, error=str(e))
        
        # Wait for completion
        if self.process and self.process.returncode is None:
            return_code = await self.process.wait()
        else:
            return_code = self.process.returncode if self.process else -1
        
        # Send completion event
        try:
            await self.websocket.send_json({
                "event": "end",
                "return_code": return_code,
                "stopped": stopped
            })
        except Exception:
            pass
        
        if on_complete:
            on_complete(return_code)
        
        return ExecutionResult(
            return_code=return_code,
            stopped_by_user=stopped
        )
    
    # ==================== Private Methods ====================
    
    async def _stream_output_loop(self) -> bool:
        """Stream output and listen for stop signals.
        
        Returns:
            bool: True if stopped by user, False otherwise
        """
        stopped_by_user = False
        
        while True:
            # Check for incoming messages (stop signal)
            try:
                msg = await asyncio.wait_for(
                    self.websocket.receive_json(),
                    timeout=0.1
                )
                if msg.get('action') == 'stop':
                    await self._terminate_process()
                    stopped_by_user = True
                    break
            except asyncio.TimeoutError:
                pass  # No message, continue reading output
            except (WebSocketDisconnect, Exception):
                # Client disconnected or other error
                await self._terminate_process()
                break
            
            # Read process output
            try:
                line = await asyncio.wait_for(
                    self.process.stdout.readline(),
                    timeout=0.1
                )
                if not line:
                    break  # EOF - process finished
                await self._send_output(line.decode(errors="ignore"))
            except asyncio.TimeoutError:
                continue  # No output yet, loop back
            except WebSocketDisconnect:
                await self._terminate_process()
                break
        
        return stopped_by_user
    
    async def _terminate_process(self):
        """Terminate the entire process group (children included) with escalation.

        Order:
        1. SIGINT (graceful interrupt) / terminate() fallback on Windows
        2. SIGTERM (polite termination)
        3. SIGKILL (force) if still alive after timeout
        """
        if not (self.process and self.process.returncode is None):
            return

        pid = self.process.pid
        # On POSIX we can signal the process group; on Windows fall back to terminate
        posix = os.name == 'posix'

        async def _wait(timeout: float):
            try:
                await asyncio.wait_for(self.process.wait(), timeout=timeout)
                return True
            except asyncio.TimeoutError:
                return False

        try:
            if posix:
                # Send SIGINT first (Ctrl-C equivalent)
                os.killpg(pid, signal.SIGINT)
                if await _wait(2.0):
                    return
                # Escalate to SIGTERM
                os.killpg(pid, signal.SIGTERM)
                if await _wait(2.0):
                    return
                # Final resort SIGKILL
                os.killpg(pid, signal.SIGKILL)
                await self.process.wait()
            else:
                # Windows: terminate() is forceful enough; attempt once then kill()
                self.process.terminate()
                if not await _wait(3.0):
                    self.process.kill()
                    await self.process.wait()
        except ProcessLookupError:
            # Process group already gone
            pass
        except Exception:
            # Fall back to direct terminate/kill in case of any failure
            try:
                self.process.terminate()
                if not await _wait(2.0):
                    self.process.kill()
                    await self.process.wait()
            except Exception:
                pass
    
    async def _send_output(self, text: str):
        """Send output text to WebSocket client."""
        try:
            await self.websocket.send_json({
                "stream": "stdout",
                "data": text
            })
        except Exception:
            pass  # Client may have disconnected
    
    async def _send_error(self, error: str):
        """Send error message to WebSocket client."""
        try:
            await self.websocket.send_json({
                "event": "error",
                "detail": error
            })
            await self.websocket.close()
        except Exception:
            pass


# ==================== Helper Functions ====================

async def stream_script_execution(
    websocket: WebSocket,
    script_path: Path | str,
    working_dir: Optional[Path | str] = None,
    **kwargs
) -> ExecutionResult:
    """Convenience function to execute script with WebSocket streaming.
    
    Args:
        websocket: Active WebSocket connection
        script_path: Path to script to execute
        working_dir: Working directory
        **kwargs: Additional arguments for WebSocketStreamExecutor.execute_script()
        
    Returns:
        ExecutionResult
    """
    executor = WebSocketStreamExecutor(websocket)
    return await executor.execute_script(script_path, working_dir, **kwargs)


async def stream_command_execution(
    websocket: WebSocket,
    command: list[str],
    working_dir: Path | str,
    **kwargs
) -> ExecutionResult:
    """Convenience function to execute command with WebSocket streaming.
    
    Args:
        websocket: Active WebSocket connection
        command: Command and arguments as list
        working_dir: Working directory
        **kwargs: Additional arguments for WebSocketStreamExecutor.execute_command()
        
    Returns:
        ExecutionResult
    """
    executor = WebSocketStreamExecutor(websocket)
    return await executor.execute_command(command, working_dir, **kwargs)
