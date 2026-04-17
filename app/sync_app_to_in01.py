"""
Script to sync the local app folder to the in01 SSH server.
Removes the remote app folder first, then copies the local folder.
"""

import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

# Configuration
# Resolve local app folder dynamically (override via TIMING_LOCAL_APP_PATH)
LOCAL_PATH = os.getenv("TIMING_LOCAL_APP_PATH", str(Path(__file__).resolve().parent))
REMOTE_USER = "trankiet"
REMOTE_HOST = "in01"  # Short hostname for SSH
REMOTE_BASE_PATH = "/remote/in01home14/trankiet/projects/signara-platform"
REMOTE_APP_PATH = f"{REMOTE_BASE_PATH}/app"

# Files/folders to exclude from copying
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    "node_modules",
    ".git",
    "*.log",
    ".env",
    "venv",
    ".venv",
    ".cache",
    "sync_app_to_in01.py",
    ".github",
    "tests",
    "test_output",
    "utils",
    "useful_commands.md",
    "CleanArchitecture.md",
    "docs",
    "ARCHITECTURE.md",
    "README.md",
    "Synopsys.md",
    "OPENCODE.md",
    ".vscode",
    "beta_feature"
]


def run_command(cmd: list[str], description: str) -> bool:
    """Execute a shell command and return success status."""
    print(f"\n{'='*60}")
    print(f"[{description}]")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        print(f"[OK] {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error during {description}:", file=sys.stderr)
        print(f"  Return code: {e.returncode}", file=sys.stderr)
        if e.stdout:
            print(f"  STDOUT: {e.stdout}", file=sys.stderr)
        if e.stderr:
            print(f"  STDERR: {e.stderr}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print(f"[ERROR] Command not found. Please ensure SSH is installed.", file=sys.stderr)
        return False


def main():
    """Main function to sync folder to remote server."""
    print("\n" + "="*60)
    print("SYNC APP FOLDER TO in01 SERVER")
    print("="*60)
    print(f"Local:  {LOCAL_PATH}")
    print(f"Remote: {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_APP_PATH}")
    print("="*60)
    
    # Verify local path exists
    local_path = Path(LOCAL_PATH)
    if not local_path.exists():
        print(f"[ERROR] Local path does not exist: {LOCAL_PATH}", file=sys.stderr)
        return 1
    
    # Step 1: Remove existing remote app folder
    print("\n[Step 1/2] Removing existing remote app folder...")
    ssh_remove_cmd = [
        "ssh",
        f"{REMOTE_USER}@{REMOTE_HOST}",
        f"rm -rf {REMOTE_APP_PATH}"
    ]
    
    if not run_command(ssh_remove_cmd, "Remove remote app folder"):
        print("\n[WARNING] Failed to remove remote folder (it may not exist)")
        # Continue anyway - folder might not exist
    
    # Step 2: Copy local folder to remote using tar over SSH
    print("\n[Step 2/2] Copying local app folder to remote server...")
    print("[INFO] Using tar over SSH for file transfer...")
    
    # Create a temporary tar file
    temp_dir = tempfile.gettempdir()
    tar_file = os.path.join(temp_dir, "app_sync.tar.gz")
    
    print(f"\n[INFO] Creating compressed archive: {tar_file}")
    
    # Use Python's tarfile module for better cross-platform exclude handling
    print("[INFO] Using Python to create archive...")
    
    def should_exclude(path_parts):
        """Check if file/folder should be excluded based on path components."""
        # Convert Path to string with forward slashes for consistent matching
        path_str = "/".join(path_parts)
        
        for pattern in EXCLUDE_PATTERNS:
            if pattern.startswith("*."):
                # Handle wildcard patterns like *.pyc
                ext = pattern[1:]  # Remove * to get .pyc
                if path_str.endswith(ext):
                    return True

            # Match named paths by component so .git does not exclude
            # .gitignore or .gitattributes.
            if "/" in pattern:
                if path_str == pattern or path_str.startswith(f"{pattern}/"):
                    return True
                continue

            if pattern in path_parts:
                return True
        return False
    
    with tarfile.open(tar_file, "w:gz") as tar:
        for item in local_path.rglob("*"):
            # Avoid adding directories recursively because that bypasses
            # per-path exclude checks for nested files.
            if not item.is_file():
                continue

            rel_path = item.relative_to(local_path)
            path_parts = rel_path.parts

            if should_exclude(path_parts):
                continue

            arcname = Path(local_path.name) / rel_path
            tar.add(item, arcname=arcname, recursive=False)
    
    print("[OK] Archive created with Python")
    
    # Step 2a: Create parent directory on remote
    print("\n[INFO] Ensuring remote directory exists...")
    ssh_mkdir_cmd = [
        "ssh",
        f"{REMOTE_USER}@{REMOTE_HOST}",
        f"mkdir -p {REMOTE_BASE_PATH}"
    ]
    run_command(ssh_mkdir_cmd, "Create remote directory")
    
    # Step 2b: Transfer tar file using Python through SSH stdin
    print("\n[INFO] Transferring archive to remote server...")
    
    remote_tar_path = "/tmp/app_sync.tar.gz"
    
    # Read tar file and pipe to SSH
    try:
        with open(tar_file, 'rb') as f:
            tar_data = f.read()
        
        # Upload tar file
        upload_process = subprocess.Popen(
            ["ssh", f"{REMOTE_USER}@{REMOTE_HOST}", f"cat > {remote_tar_path}"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = upload_process.communicate(input=tar_data)
        
        if upload_process.returncode != 0:
            print(f"[ERROR] Failed to upload archive", file=sys.stderr)
            if stderr:
                print(f"  STDERR: {stderr.decode()}", file=sys.stderr)
            return 1
        
        print("[OK] Archive uploaded to remote server")
        
        # Step 2c: Extract on remote
        print("\n[INFO] Extracting archive on remote server...")
        extract_cmd = [
            "ssh",
            f"{REMOTE_USER}@{REMOTE_HOST}",
            f"tar -xzf {remote_tar_path} -C {REMOTE_BASE_PATH} && rm {remote_tar_path}"
        ]
        
        if not run_command(extract_cmd, "Extract archive on remote"):
            print(f"[ERROR] Failed to extract archive on remote", file=sys.stderr)
            return 1

        # Step 2d: Remove any stale Python bytecode cache files on remote
        print("\n[INFO] Removing stale __pycache__ and .pyc files on remote...")
        cleanup_cache_cmd = [
            "ssh",
            f"{REMOTE_USER}@{REMOTE_HOST}",
            f"find {REMOTE_APP_PATH} -type d -name '__pycache__' -prune -exec rm -rf {{}} +; find {REMOTE_APP_PATH} -type f -name '*.pyc' -delete"
        ]

        if not run_command(cleanup_cache_cmd, "Clean Python cache files"):
            print("[WARNING] Failed to clean Python cache files (non-critical)")
        
        # Step 2e: Fix permissions on remote (make scripts executable)
        print("\n[INFO] Setting executable permissions on shell scripts...")
        chmod_cmd = [
            "ssh",
            f"{REMOTE_USER}@{REMOTE_HOST}",
            f"find {REMOTE_APP_PATH} -type f \\( -name '*.sh' -o -name '*.csh' \\) -exec chmod +x {{}} \\;"
        ]
        
        if not run_command(chmod_cmd, "Set executable permissions"):
            print("[WARNING] Failed to set executable permissions (non-critical)")
            # Continue anyway - this is not critical
            
    except Exception as e:
        print(f"[ERROR] Transfer failed: {e}", file=sys.stderr)
        return 1
    finally:
        # Clean up local tar file
        try:
            os.remove(tar_file)
            print(f"\n[INFO] Cleaned up temporary file: {tar_file}")
        except:
            pass
    
    print("\n" + "="*60)
    print("[SUCCESS] SYNC COMPLETED SUCCESSFULLY!")
    print("="*60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
