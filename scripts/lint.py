#!/usr/bin/env python3
"""
Code quality and linting script for vibe-worldbuilding.

This script runs various code quality checks including:
- Python linting with pylint
- Code formatting checks with black
- Frontend linting with prettier
- Type checking with mypy
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str = "") -> tuple[bool, str]:
    """Run a shell command and return (success, output)."""
    print(f"🔍 {description or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def check_python_formatting():
    """Check Python code formatting with black."""
    print("\n📝 Checking Python code formatting...")
    
    # Check if black would make changes
    success, output = run_command("black --check --diff vibe_worldbuilding/ tests/", "Running black formatter check")
    
    if not success:
        print("❌ Code formatting issues found:")
        print(output)
        print("\n💡 Fix with: black vibe_worldbuilding/ tests/")
        return False
    
    print("✅ Python code formatting is correct")
    return True


def check_python_linting():
    """Run Python linting with pylint."""
    print("\n🔍 Running Python linting...")
    
    success, output = run_command("pylint vibe_worldbuilding/", "Running pylint")
    
    if not success:
        print("❌ Linting issues found:")
        print(output)
        return False
    
    print("✅ Python linting passed")
    return True


def check_type_hints():
    """Check Python type hints with mypy."""
    print("\n🔬 Checking Python type hints...")
    
    success, output = run_command("mypy vibe_worldbuilding/ --ignore-missing-imports", "Running mypy type checker")
    
    if not success:
        print("❌ Type checking issues found:")
        print(output)
        return False
    
    print("✅ Type checking passed")
    return True


def check_frontend_formatting():
    """Check frontend code formatting with prettier."""
    print("\n🎨 Checking frontend code formatting...")
    
    # Check TypeScript, Astro, and JSON files
    patterns = ["src/**/*.{ts,astro,json}", "*.{json,mjs}"]
    
    for pattern in patterns:
        success, output = run_command(f"npx prettier --check '{pattern}'", f"Checking {pattern}")
        
        if not success:
            print(f"❌ Frontend formatting issues found in {pattern}:")
            print(output)
            print(f"\n💡 Fix with: npx prettier --write '{pattern}'")
            return False
    
    print("✅ Frontend code formatting is correct")
    return True


def check_imports():
    """Check for unused imports and import order."""
    print("\n📦 Checking Python imports...")
    
    success, output = run_command("isort --check-only --diff vibe_worldbuilding/ tests/", "Checking import order")
    
    if not success:
        print("❌ Import order issues found:")
        print(output)
        print("\n💡 Fix with: isort vibe_worldbuilding/ tests/")
        return False
    
    print("✅ Import order is correct")
    return True


def run_security_checks():
    """Run security checks with bandit."""
    print("\n🔒 Running security checks...")
    
    success, output = run_command("bandit -r vibe_worldbuilding/ -f json", "Running security analysis")
    
    if not success:
        print("❌ Security issues found:")
        print(output)
        return False
    
    print("✅ No security issues found")
    return True


def main():
    """Main linting routine."""
    print("🧹 Vibe Worldbuilding Code Quality Check")
    print("=" * 50)
    
    checks = [
        ("Python Formatting", check_python_formatting),
        ("Python Linting", check_python_linting),
        ("Type Hints", check_type_hints),
        ("Frontend Formatting", check_frontend_formatting),
        ("Import Order", check_imports),
        ("Security", run_security_checks),
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                failed_checks.append(check_name)
        except Exception as e:
            print(f"❌ {check_name} check failed with exception: {e}")
            failed_checks.append(check_name)
    
    print("\n" + "=" * 50)
    
    if failed_checks:
        print(f"❌ {len(failed_checks)} checks failed:")
        for check in failed_checks:
            print(f"   - {check}")
        print("\n💡 Fix issues and run again")
        return 1
    else:
        print("🎉 All code quality checks passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())