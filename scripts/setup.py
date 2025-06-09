#!/usr/bin/env python3
"""
Setup script for vibe-worldbuilding development environment.

This script automates the setup of a development environment including:
- Virtual environment creation
- Dependency installation
- Configuration file setup
- Development tool installation
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str = "") -> bool:
    """Run a shell command and return success status."""
    print(f"🔧 {description or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False


def setup_python_environment():
    """Set up Python virtual environment and dependencies."""
    print("🐍 Setting up Python environment...")
    
    # Check if virtual environment exists
    if not Path("venv").exists():
        if not run_command("python3 -m venv venv", "Creating virtual environment"):
            return False
    
    # Install Python dependencies
    pip_cmd = "./venv/bin/pip" if os.name != "nt" else ".\\venv\\Scripts\\pip"
    if not run_command(f"{pip_cmd} install -e .", "Installing Python dependencies"):
        return False
    
    return True


def setup_node_environment():
    """Set up Node.js dependencies."""
    print("📦 Setting up Node.js environment...")
    
    if not run_command("npm install", "Installing Node.js dependencies"):
        return False
    
    return True


def setup_configuration():
    """Set up configuration files."""
    print("⚙️ Setting up configuration...")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# Vibe Worldbuilding Environment Variables
# Add your FAL API key below (get one from https://fal.ai/)
FAL_KEY=your_fal_api_key_here
"""
        env_file.write_text(env_content)
        print("   Created .env file (add your FAL API key)")
    
    return True


def verify_setup():
    """Verify the setup by running basic tests."""
    print("✅ Verifying setup...")
    
    # Test Python imports
    if not run_command("python -c 'import vibe_worldbuilding; print(\"✅ Python package imports successfully\")'", "Testing Python imports"):
        return False
    
    # Test basic MCP functionality
    if not run_command("python tests/run_tests.py unit --verbose", "Running unit tests"):
        return False
    
    return True


def main():
    """Main setup routine."""
    print("🚀 Vibe Worldbuilding Development Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return 1
    
    steps = [
        ("Python Environment", setup_python_environment),
        ("Node.js Environment", setup_node_environment),
        ("Configuration", setup_configuration),
        ("Verification", verify_setup),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            return 1
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Add your FAL API key to .env file")
    print("2. Configure Claude Desktop with config/claude-desktop.json")
    print("3. Run: python tests/test_e2e_comprehensive.py --verbose")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())