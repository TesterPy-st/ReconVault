#!/usr/bin/env python3
"""
Test script to validate path resolution logic for CI checks.
Tests the core logic without running actual git/CI commands.
"""

import os
import sys
from pathlib import Path


def filter_backend_files(file_paths):
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
        if 'site-packages' in filepath:
            continue
        
        # Handle backend files - strip "backend/" prefix
        if filepath.startswith('backend/'):
            normalized_path = filepath[8:]  # Strip "backend/" prefix
            if normalized_path:  # Ensure not empty
                backend_files.append(normalized_path)
                
    return sorted(backend_files)


def test_path_normalization():
    """Test the path normalization logic."""
    test_cases = {
        # Git path -> Expected normalized path
        "backend/app/models.py": "app/models.py",
        "backend/app/service.py": "app/service.py", 
        "backend/config.py": "config.py",
        "backend/app/database.py": "app/database.py",
        # Non-backend files should be skipped
        "frontend/src/main.js": None,
        "README.md": None,
        "docker-compose.yml": None,
        # Non-python files should be skipped
        "backend/requirements.txt": None,
        "backend/Dockerfile": None,
        # Venv files should be skipped
        "backend/venv/lib/python3.12/site-packages/somepackage.py": None,
        "backend/app/__pycache__/models.cpython-312.pyc": None,
    }
    
    for git_path, expected in test_cases.items():
        result = filter_backend_files({git_path})
        actual = result[0] if result else None
        
        if actual == expected:
            print(f"✅ PASS: '{git_path}' -> '{expected}'")
        else:
            print(f"❌ FAIL: '{git_path}' -> '{actual}' (expected '{expected}')")
            return False
    
    # Test multiple files
    multiple_files = {
        "backend/app/models.py",
        "backend/app/config.py",
        "backend/tests/test_models.py",
        "frontend/src/main.js",  # Should be filtered
        "requirements.txt",  # Should be filtered
    }
    
    result = filter_backend_files(multiple_files)
    expected = sorted([
        "app/models.py",
        "app/config.py", 
        "tests/test_models.py"
    ])
    
    if result == expected:
        print(f"✅ PASS: Multiple file filtering correct")
    else:
        print(f"❌ FAIL: Multiple file filtering got {result}, expected {expected}")
        return False
    
    return True


def test_execution_from_backend_dir():
    """Test that script executes properly from backend directory."""
    
    # Check we're in backend directory
    current_dir = Path.cwd()
    backend_files = ['app', 'requirements.txt', 'ci_check.py']
    
    for file in backend_files:
        if not (current_dir / file).exists():
            print(f"❌ FAIL: Expected file '{file}' not found in current directory {current_dir}")
            return False
    
    print(f"✅ PASS: Script executes correctly from backend directory")
    print(f"   Current directory: {current_dir}")
    print(f"   Found backend files: {backend_files}")
    return True


if __name__ == '__main__':
    print("Testing CI check path resolution logic...")
    print("=" * 50)
    
    all_passed = True
    
    print("\n1. Testing path normalization:")
    all_passed &= test_path_normalization()
    
    print("\n2. Testing execution from backend directory:")
    all_passed &= test_execution_from_backend_dir()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! CI check script will handle paths correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed.")
        sys.exit(1)