"""
Fix Line Endings Utility

Converts files to Unix (LF) line endings, which is required for shell scripts
to work correctly on Linux systems.

Usage:
    python utils/fix_line_endings.py                    # Fix shell scripts
    python utils/fix_line_endings.py --all              # Fix all text files
    python utils/fix_line_endings.py --check            # Check only, don't fix
    python utils/fix_line_endings.py file1.sh file2.csh # Fix specific files
"""

import os
import argparse
from pathlib import Path
from typing import List, Set


# File extensions that must have LF line endings
SHELL_EXTENSIONS = {'.sh', '.csh', '.bash', '.zsh', '.ksh'}

# Additional text files that should have LF
TEXT_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.css', '.scss',
    '.html', '.htm', '.xml', '.json', '.yaml', '.yml',
    '.md', '.txt', '.cfg', '.conf', '.ini'
}

# Directories to skip
SKIP_DIRECTORIES = {
    '.git', '.venv', 'venv', 'env', 'node_modules',
    '__pycache__', '.pytest_cache', '.mypy_cache',
    'build', 'dist', '.cache'
}


class LineEndingFixer:
    """Fix line endings in files."""
    
    def __init__(self, check_only: bool = False, verbose: bool = False):
        self.check_only = check_only
        self.verbose = verbose
        self.checked_files = 0
        self.fixed_files = 0
        self.crlf_files: List[str] = []
    
    def should_skip_dir(self, dir_path: Path) -> bool:
        """Check if directory should be skipped."""
        return dir_path.name in SKIP_DIRECTORIES
    
    def has_crlf(self, file_path: Path) -> bool:
        """Check if file has CRLF line endings."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return b'\r\n' in content
        except (OSError, PermissionError):
            return False
    
    def fix_file(self, file_path: Path) -> bool:
        """Convert file to LF line endings. Returns True if fixed."""
        try:
            # Read in binary mode to preserve encoding
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Check if conversion needed
            if b'\r\n' not in content:
                return False
            
            # Convert CRLF to LF
            content = content.replace(b'\r\n', b'\n')
            
            if self.check_only:
                return True
            
            # Write back
            with open(file_path, 'wb') as f:
                f.write(content)
            
            return True
            
        except (OSError, PermissionError) as e:
            if self.verbose:
                print(f"  ❌ Error processing {file_path}: {e}")
            return False
    
    def fix_specific_files(self, file_paths: List[str]):
        """Fix specific files."""
        print(f"\n{'🔍 Checking' if self.check_only else '🔧 Fixing'} specific files...")
        
        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            
            if not file_path.exists():
                print(f"  ⚠️  File not found: {file_path}")
                continue
            
            if not file_path.is_file():
                print(f"  ⚠️  Not a file: {file_path}")
                continue
            
            self.checked_files += 1
            
            if self.has_crlf(file_path):
                self.crlf_files.append(str(file_path))
                
                if self.check_only:
                    print(f"  ⚠️  CRLF found: {file_path}")
                else:
                    if self.fix_file(file_path):
                        self.fixed_files += 1
                        print(f"  ✅ Fixed: {file_path}")
                    else:
                        print(f"  ❌ Failed to fix: {file_path}")
            else:
                if self.verbose:
                    print(f"  ✓ OK (LF): {file_path}")
    
    def fix_project_files(self, project_root: Path, extensions: Set[str]):
        """Fix all files with specified extensions in project."""
        print(f"\n{'🔍 Checking' if self.check_only else '🔧 Fixing'} files with extensions: {', '.join(sorted(extensions))}")
        
        for root, dirs, files in os.walk(project_root):
            # Skip protected directories
            dirs[:] = [d for d in dirs if d not in SKIP_DIRECTORIES]
            
            root_path = Path(root)
            
            for file_name in files:
                file_path = root_path / file_name
                file_ext = file_path.suffix.lower()
                
                # Check if extension matches
                if file_ext not in extensions:
                    continue
                
                self.checked_files += 1
                
                if self.has_crlf(file_path):
                    rel_path = file_path.relative_to(project_root)
                    self.crlf_files.append(str(rel_path))
                    
                    if self.check_only:
                        print(f"  ⚠️  CRLF: {rel_path}")
                    else:
                        if self.fix_file(file_path):
                            self.fixed_files += 1
                            print(f"  ✅ Fixed: {rel_path}")
                        else:
                            if self.verbose:
                                print(f"  ❌ Failed: {rel_path}")
                else:
                    if self.verbose:
                        print(f"  ✓ OK: {file_path.relative_to(project_root)}")
    
    def print_summary(self):
        """Print summary of operations."""
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        print(f"Files checked: {self.checked_files}")
        print(f"Files with CRLF: {len(self.crlf_files)}")
        
        if self.check_only:
            if self.crlf_files:
                print("\n⚠️  Files needing conversion:")
                for file_path in self.crlf_files:
                    print(f"  - {file_path}")
                print(f"\nRun without --check to fix these files")
            else:
                print("\n✅ All files have correct LF line endings!")
        else:
            print(f"Files fixed: {self.fixed_files}")
            if self.fixed_files > 0:
                print("\n✅ Line endings fixed successfully!")
            else:
                print("\n✅ All files already had correct LF line endings!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fix line endings in shell scripts and text files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python utils/fix_line_endings.py                # Fix shell scripts only
  python utils/fix_line_endings.py --all          # Fix all text files
  python utils/fix_line_endings.py --check        # Check without fixing
  python utils/fix_line_endings.py timing_app.csh # Fix specific file
  python utils/fix_line_endings.py -v             # Verbose output
        """
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Fix all text files (not just shell scripts)'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check for CRLF without fixing'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed output'
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='Specific files to fix (optional)'
    )
    
    args = parser.parse_args()
    
    # Get project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    
    print("="*60)
    print("🔧 Line Ending Fixer")
    print("="*60)
    print(f"Project root: {project_root}")
    print(f"Mode: {'CHECK ONLY' if args.check else 'FIX'}")
    
    fixer = LineEndingFixer(check_only=args.check, verbose=args.verbose)
    
    if args.files:
        # Fix specific files
        fixer.fix_specific_files(args.files)
    else:
        # Fix project files
        if args.all:
            # Fix all text files
            extensions = SHELL_EXTENSIONS | TEXT_EXTENSIONS
        else:
            # Fix shell scripts only
            extensions = SHELL_EXTENSIONS
        
        fixer.fix_project_files(project_root, extensions)
    
    fixer.print_summary()
    
    return 0 if not fixer.crlf_files else 1


if __name__ == '__main__':
    exit(main())
