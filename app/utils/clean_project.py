"""
Project Cleanup Utility for TimeCraft Platform

This script removes all cache, temporary, and build files from the project.
Run this before releasing or committing to ensure a clean state.

Usage:
    python utils/clean_project.py
    python utils/clean_project.py --dry-run  # Preview what will be deleted
    python utils/clean_project.py --verbose  # Show detailed output
"""

import os
import shutil
import argparse
from pathlib import Path
from typing import List, Set


# Directories to completely remove
CACHE_DIRECTORIES = {
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache',
    '.cache',
    'htmlcov',
    '.tox',
    '.nox',
    '.hypothesis',
    '.eggs',
    '*.egg-info',
    'dist',
    'build',
    '.pybuilder',
    'node_modules',  # Frontend dependencies (should be installed fresh)
}

# File patterns to remove
CACHE_FILE_PATTERNS = {
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '*$py.class',
    '*.so',
    '*.dll',
    '*.dylib',
    '*.log',
    '*.tmp',
    '*.temp',
    '*.swp',
    '*.swo',
    '*~',
    '.DS_Store',
    'Thumbs.db',
    'desktop.ini',
    '*.cover',
    '*.py.cover',
    '.coverage',
    '.coverage.*',
    'coverage.xml',
    '*.mo',  # Compiled translations
    '*.pot',  # Translation templates
}

# Directories to exclude from cleaning (never touch these)
PROTECTED_DIRECTORIES = {
    '.git',
    '.venv',
    'venv',
    'env',
    '.idea',
    '.vscode',
}

# Specific files to keep (even if they match patterns)
PROTECTED_FILES = {
    'requirements.txt',
    'package.json',
    'package-lock.json',
}


class ProjectCleaner:
    """Clean cache and temporary files from the project."""
    
    def __init__(self, project_root: Path, dry_run: bool = False, verbose: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.verbose = verbose
        self.deleted_dirs: List[str] = []
        self.deleted_files: List[str] = []
        self.freed_space = 0
    
    def is_protected(self, path: Path) -> bool:
        """Check if a path should never be deleted."""
        # Check if any parent directory is protected
        for parent in path.parents:
            if parent.name in PROTECTED_DIRECTORIES:
                return True
        
        # Check if the path itself is protected
        if path.name in PROTECTED_DIRECTORIES:
            return True
        
        # Check if file is protected
        if path.is_file() and path.name in PROTECTED_FILES:
            return True
        
        return False
    
    def matches_pattern(self, path: Path, patterns: Set[str]) -> bool:
        """Check if path matches any of the given patterns."""
        for pattern in patterns:
            if pattern.startswith('*'):
                # Wildcard pattern
                if path.name.endswith(pattern[1:]):
                    return True
            else:
                # Exact match
                if path.name == pattern:
                    return True
        return False
    
    def get_dir_size(self, path: Path) -> int:
        """Calculate total size of directory in bytes."""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except (OSError, PermissionError):
            pass
        return total
    
    def format_size(self, size_bytes: int) -> str:
        """Format bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def remove_directory(self, dir_path: Path):
        """Remove a directory and track statistics."""
        if self.is_protected(dir_path):
            if self.verbose:
                print(f"  ⚠️  Protected: {dir_path.relative_to(self.project_root)}")
            return
        
        size = self.get_dir_size(dir_path)
        rel_path = dir_path.relative_to(self.project_root)
        
        if self.dry_run:
            print(f"  🗑️  Would delete: {rel_path} ({self.format_size(size)})")
        else:
            try:
                shutil.rmtree(dir_path)
                self.deleted_dirs.append(str(rel_path))
                self.freed_space += size
                if self.verbose:
                    print(f"  ✅ Deleted: {rel_path} ({self.format_size(size)})")
            except (OSError, PermissionError) as e:
                print(f"  ❌ Error deleting {rel_path}: {e}")
    
    def remove_file(self, file_path: Path):
        """Remove a file and track statistics."""
        if self.is_protected(file_path):
            if self.verbose:
                print(f"  ⚠️  Protected: {file_path.relative_to(self.project_root)}")
            return
        
        size = file_path.stat().st_size
        rel_path = file_path.relative_to(self.project_root)
        
        if self.dry_run:
            print(f"  🗑️  Would delete: {rel_path} ({self.format_size(size)})")
        else:
            try:
                file_path.unlink()
                self.deleted_files.append(str(rel_path))
                self.freed_space += size
                if self.verbose:
                    print(f"  ✅ Deleted: {rel_path} ({self.format_size(size)})")
            except (OSError, PermissionError) as e:
                print(f"  ❌ Error deleting {rel_path}: {e}")
    
    def clean_cache_directories(self):
        """Remove all cache directories."""
        print("\n🔍 Scanning for cache directories...")
        found = []
        
        for root, dirs, _ in os.walk(self.project_root):
            root_path = Path(root)
            
            # Skip protected directories
            if self.is_protected(root_path):
                dirs[:] = []  # Don't descend into this directory
                continue
            
            # Check each subdirectory
            for dir_name in list(dirs):
                dir_path = root_path / dir_name
                
                if self.matches_pattern(dir_path, CACHE_DIRECTORIES):
                    found.append(dir_path)
                    dirs.remove(dir_name)  # Don't descend into cache dirs
        
        print(f"Found {len(found)} cache directories")
        for dir_path in found:
            self.remove_directory(dir_path)
    
    def clean_cache_files(self):
        """Remove all cache files."""
        print("\n🔍 Scanning for cache files...")
        found = []
        
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            
            # Skip protected directories
            if self.is_protected(root_path):
                dirs[:] = []
                continue
            
            # Check each file
            for file_name in files:
                file_path = root_path / file_name
                
                if self.matches_pattern(file_path, CACHE_FILE_PATTERNS):
                    found.append(file_path)
        
        print(f"Found {len(found)} cache files")
        for file_path in found:
            self.remove_file(file_path)
    
    def clean_test_outputs(self):
        """Remove test output directory if present."""
        print("\n🔍 Checking test outputs...")
        test_output = self.project_root / 'test_output'
        
        if test_output.exists() and test_output.is_dir():
            # Only remove generated files, keep the runall.csh script
            for item in test_output.iterdir():
                if item.name != 'runall.csh':
                    if item.is_dir():
                        self.remove_directory(item)
                    else:
                        self.remove_file(item)
        else:
            print("  No test output directory found")
    
    def print_summary(self):
        """Print cleanup summary."""
        print("\n" + "="*60)
        print("🎯 CLEANUP SUMMARY")
        print("="*60)
        print(f"Directories removed: {len(self.deleted_dirs)}")
        print(f"Files removed: {len(self.deleted_files)}")
        print(f"Space freed: {self.format_size(self.freed_space)}")
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - Nothing was actually deleted")
            print("Run without --dry-run to perform actual cleanup")
        else:
            print("\n✅ Cleanup completed successfully!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Clean cache and temporary files from TimeCraft Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python utils/clean_project.py                    # Clean the project
  python utils/clean_project.py --dry-run         # Preview what will be deleted
  python utils/clean_project.py --verbose         # Show detailed output
  python utils/clean_project.py -n -v             # Dry run with verbose output
        """
    )
    parser.add_argument(
        '-n', '--dry-run',
        action='store_true',
        help='Preview what will be deleted without actually deleting'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed output for each file/directory'
    )
    
    args = parser.parse_args()
    
    # Get project root (parent of utils directory)
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    
    print("="*60)
    print("🧹 TimeCraft Platform - Project Cleanup Utility")
    print("="*60)
    print(f"Project root: {project_root}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'CLEANUP'}")
    print(f"Verbose: {args.verbose}")
    
    cleaner = ProjectCleaner(project_root, dry_run=args.dry_run, verbose=args.verbose)
    
    # Run cleanup steps
    cleaner.clean_cache_directories()
    cleaner.clean_cache_files()
    cleaner.clean_test_outputs()
    
    # Print summary
    cleaner.print_summary()
    
    return 0


if __name__ == '__main__':
    exit(main())
