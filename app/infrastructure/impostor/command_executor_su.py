"""Command executor implementation using su/expect mechanism.

Executes commands as different users using expect script for authentication.
"""

import os
import re
import subprocess
import tempfile
import shlex
from pathlib import Path


class CommandExecutorSU:
    """Execute commands as different users via su and expect script."""
    
    def __init__(self, su_script: Path | None = None):
        """Initialize with path to su expect script.
        
        Args:
            su_script: Path to su_somewhere.exp script (defaults to ./bin/cshell/su_somewhere.exp)
        """
        if su_script is None:
            su_script = Path("./bin/cshell/su_somewhere.exp").resolve()
        
        self.su_script = su_script
    
    def execute_script(
        self,
        username: str,
        password: str,
        script_path: Path,
        cwd: Path | None = None
    ) -> tuple[bool, str]:
        """Execute a script as a different user.
        
        Args:
            username: The user to execute as
            password: The password for authentication
            script_path: Path to the script to execute
            cwd: Working directory for execution
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.su_script.exists():
            return False, f"su_somewhere.exp not found: {self.su_script}"
        
        # Make sure the target script is executable
        try:
            os.chmod(script_path, 0o755)
        except Exception:
            pass
        
        # Build command: su_somewhere.exp <username> <password> <script>
        cmd = [str(self.su_script), username, password, str(script_path)]
        
        # Execute via expect script
        try:
            # Run in background, return process handle
            process = subprocess.Popen(
                cmd,
                cwd=str(cwd) if cwd else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            return True, f"Job submitted as {username}"
        except Exception as e:
            return False, f"Failed to execute script: {e}"
    
    def execute_command(
        self,
        username: str,
        password: str,
        command: list[str],
        cwd: Path | None = None
    ) -> tuple[bool, str, str | None, str | None]:
        """Execute a command as a different user.
        
        This creates a temporary script with the command and executes it
        via the impostor mechanism.
        
        Args:
            username: The user to execute as
            password: The password for authentication
            command: Command and arguments as list
            cwd: Working directory for execution
            
        Returns:
            Tuple of (success: bool, message: str, job_id: str|None, full_command: str|None)
        """
        # Build the command string for display
        cmd_str = " ".join(shlex.quote(str(arg)) for arg in command)
        full_command = f"[Running as {username}] {cmd_str}"
        
        # Create temporary script
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.csh',
                delete=False,
                dir=str(cwd) if cwd else None
            ) as f:
                f.write("#!/bin/csh\n")
                f.write(cmd_str)
                f.write("\n")
                temp_script = Path(f.name)
            
            os.chmod(temp_script, 0o755)
            
            # Execute via impostor
            if not self.su_script.exists():
                try:
                    temp_script.unlink()
                except Exception:
                    pass
                return False, f"su_somewhere.exp not found: {self.su_script}", None, full_command
            
            # Build command: su_somewhere.exp <username> <password> <script>
            cmd = [str(self.su_script), username, password, str(temp_script)]
            
            # Execute and wait for output
            process = subprocess.Popen(
                cmd,
                cwd=str(cwd) if cwd else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Wait for process and get output
            stdout, stderr = process.communicate(timeout=30)
            returncode = process.returncode
            
            # Clean up temp script
            try:
                temp_script.unlink()
            except Exception:
                pass
            
            if returncode != 0:
                return False, f"Command failed: {stderr or stdout}", None, full_command
            
            # Clean up output: remove expect script artifacts
            cleaned_output = stdout
            # Remove "spawn" line and "Password:" prompt from expect script
            cleaned_output = re.sub(r'spawn\s+su\s+-\s+\w+\s+-c\s+[^\n]+\n', '', cleaned_output)
            cleaned_output = re.sub(r'Password:\s*', '', cleaned_output)
            cleaned_output = cleaned_output.strip()
            
            # Parse job ID from bsub output if present
            job_id = None
            match = re.search(r'Job <(\d+)>', cleaned_output)
            if match:
                job_id = match.group(1)
            
            return True, cleaned_output or "Job submitted", job_id, full_command
            
        except Exception as e:
            return False, f"Failed to create/execute temporary script: {e}", None, full_command
