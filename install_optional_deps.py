#!/usr/bin/env python3
"""
Install Optional Dependencies

This script installs optional dependencies for the CWL to Nextflow migration toolkit.
"""

import subprocess
import sys
from pathlib import Path


def install_package(package_name, description=""):
    """Install a Python package."""
    print(f"Installing {package_name}...")
    if description:
        print(f"  {description}")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package_name], 
                      check=True, capture_output=True, text=True)
        print(f"  ✓ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed to install {package_name}: {e}")
        return False


def main():
    """Install optional dependencies."""
    print("CWL to Nextflow Migration Toolkit - Optional Dependencies Installer")
    print("=" * 70)
    
    # Core optional dependencies
    optional_packages = [
        ("cwltool", "CWL reference implementation for full CWL parsing"),
        ("cwl-utils", "CWL utilities for advanced CWL processing"),
        ("schema-salad", "Schema validation for CWL files"),
    ]
    
    print("\nInstalling optional dependencies for enhanced CWL support...")
    print("These packages are not required for basic functionality but provide")
    print("better CWL parsing and validation capabilities.\n")
    
    installed_count = 0
    total_count = len(optional_packages)
    
    for package, description in optional_packages:
        if install_package(package, description):
            installed_count += 1
        print()
    
    print("=" * 70)
    print(f"Installation Summary: {installed_count}/{total_count} packages installed")
    
    if installed_count == total_count:
        print("\n🎉 All optional dependencies installed successfully!")
        print("\nYou now have full CWL parsing capabilities.")
    elif installed_count > 0:
        print(f"\n⚠️  {total_count - installed_count} packages failed to install.")
        print("The toolkit will still work with basic functionality.")
    else:
        print("\n❌ No optional dependencies were installed.")
        print("The toolkit will work with basic YAML parsing only.")
    
    print("\nTo test the installation, run:")
    print("  python test_cwl_parser.py")
    print("  python test_installation.py")


if __name__ == "__main__":
    main()
