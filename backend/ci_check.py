#!/usr/bin/env python3
"""
CI Check Script for ReconVault Backend
Normalizes path handling to work from within backend directory.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Set, List, Optional


def get_git_project_root() -> str:
    """Get the git project root directory."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        raise RuntimeError("Not a git repository or failed to get git root")


def get_changed_files(from_project_root: bool = True) -> Set[str]:
    """
    Get changed Python files that need formatting/linting.
    
    Args:
        from_project_root: If True, changes to project root first for git operations
    
    Returns:
        Set of file paths (from git diff, relative to git root)
    """
    original_dir = os.getcwd()
    
    try:
        if from_project_root:
            git_root = get_git_project_root()
            os.chdir(git_root)
        else:
            git_root = original_dir
            
        # Get both staged and unstaged changes
        changed_files = set()
        
        # Get changed files from git diff
        for diff_type in ['--staged', 'HEAD', '--']:
            try:
                result = subprocess.run(
                    ['git', 'diff', '--name-only', '--diff-filter=AM', diff_type],
                    check=True,
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    changed_files.update(line.strip() 
                                       for line in result.stdout.split('\n') 
                                       if line.strip())
            except subprocess.CalledProcessError:
                continue
        
        return changed_files
        
    finally:
        # Always restore original directory
        os.chdir(original_dir)


def filter_backend_files(file_paths: Set[str]) -> List[str]:
    """
    Filter to only include Python files and normalize backend paths.
    
    Args:
        file_paths: Set of file paths from git diff (relative to git root)
    
    Returns:
        List of file paths suitable for linting from backend directory
    """
    backend_files = []
    
    for filepath in file_paths:
        # Only process Python files
        if not filepath.endswith('.py'):
            continue
            
        # Skip venv files
        if '/venv/' in filepath or '/__pycache__/' in filepath:
            continue
        
        # Skip vendored files  
        if 'node_modules' in filepath or 'site-packages' in filepath:
            continue
        
        # Handle backend files - strip "backend/" prefix
        if filepath.startswith('backend/'):
            normalized_path = filepath[8:]  # Strip "backend/" prefix
            if normalized_path:  # Ensure not empty
                backend_files.append(normalized_path)
                
    return sorted(backend_files)


def run_command(command: List[str], files: List[str]) -> bool:
    """
    Run a command on files and return success status.
    
    Args:
        command: Base command (e.g., ['python3', '-m', 'black'])
        files: List of files to process
    
    Returns:
        True if command succeeded, False otherwise
    """
    if not files:
        print("No files to process")
        return True
        
    cmd = command + files
    print(f"Running: {' '.join(cmd[:2])} [...{len(files)} files...]")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except FileNotFoundError as e:
        print(f"Error: Command not found: {e}")
        return False


def main():
    """Main execution function."""
    cmd_args = sys.argv[1:]
    check_all = '--all' in cmd_args
    
    # Validate we're in the right directory
    if not Path('app').exists() or not Path('requirements.txt').exists():
        print("Error: Must run this script from the backend/ directory")
        sys.exit(1)
    
    if check_all:
        print("Checking all backend Python files...")
        # Get all Python files excluding venv and caches
        all_files = []
        for py_file in Path('.').rglob('*.py'):
            if '/venv/' not in str(py_file) and '/__pycache__/' not in str(py_file):
                all_files.append(str(py_file))
        files = all_files
    else:
        # Get changed files and filter to backend
        print("Getting changed files from git...")
        changed_files = get_changed_files(from_project_root=True)
        files = filter_backend_files(changed_files)
        
        if not files:
            print("No changed backend Python files to check.")
            sys.exit(0)
    
    print(f"Files to check: {', '.join(files[:5])}{'...' if len(files) > 5 else ''}")
    
    # Run checks
    success = True
    
    # Run black formatter check
    print("\n=== Running Black formatter ===")
    success &= run_command(['python3', '-m', 'black', '--check'], files)
    
    # Run isort import sorter check
    print("\n=== Running isort import sorter ===")
    success &= run_command(['python3', '-m', 'isort', '--check-only'], files)
    
    # Run flake8 linter
    print("\n=== Running flake8 linter ===")
    success &= run_command(['python3', '-m', 'flake8'], files)
    
    # Exit with appropriate code
    if success:
        print("\n✅ All checks passed!")
        sys.exit(0)
    else:
        print("\n❌ Some checks failed")
        sys.exit(1)


if __name__ == '__main__':
    main()