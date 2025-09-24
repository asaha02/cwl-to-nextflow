#!/usr/bin/env python3
"""
Installation Test Script

Tests the CWL to Nextflow migration toolkit installation.
"""

import sys
import subprocess
import importlib
from pathlib import Path


def test_python_imports():
    """Test Python package imports."""
    print("Testing Python package imports...")
    
    required_packages = [
        'cwltool',
        'ruamel.yaml',
        'requests',
        'boto3',
        'jinja2',
        'click',
        'tqdm',
        'colorama',
        'rich'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\nFailed to import: {', '.join(failed_imports)}")
        print("Please install missing packages: pip install -r requirements.txt")
        return False
    
    return True


def test_custom_modules():
    """Test custom module imports."""
    print("\nTesting custom module imports...")
    
    # Add src to path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    custom_modules = [
        'cwl_parser',
        'nextflow_generator',
        'aws_integration',
        'resource_mapper',
        'container_handler',
        'validation'
    ]
    
    failed_imports = []
    
    for module in custom_modules:
        try:
            importlib.import_module(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\nFailed to import custom modules: {', '.join(failed_imports)}")
        return False
    
    return True


def test_command_line_tools():
    """Test command line tools."""
    print("\nTesting command line tools...")
    
    tools = [
        ('python', '--version'),
        ('node', '--version'),
        ('npm', '--version'),
        ('docker', '--version'),
        ('nextflow', '--version'),
        ('aws', '--version')
    ]
    
    failed_tools = []
    
    for tool, version_flag in tools:
        try:
            result = subprocess.run([tool, version_flag], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print(f"  ✓ {tool}: {version}")
            else:
                print(f"  ❌ {tool}: Not found")
                failed_tools.append(tool)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"  ❌ {tool}: Not found")
            failed_tools.append(tool)
    
    if failed_tools:
        print(f"\nMissing tools: {', '.join(failed_tools)}")
        print("Please install missing tools:")
        for tool in failed_tools:
            if tool == 'python':
                print("  - Python 3.8+: https://python.org")
            elif tool == 'node':
                print("  - Node.js 16+: https://nodejs.org")
            elif tool == 'docker':
                print("  - Docker: https://docker.com")
            elif tool == 'nextflow':
                print("  - Nextflow: https://nextflow.io")
            elif tool == 'aws':
                print("  - AWS CLI: https://aws.amazon.com/cli")
        return False
    
    return True


def test_cwl_tool():
    """Test CWL tool installation."""
    print("\nTesting CWL tool...")
    
    try:
        result = subprocess.run(['cwltool', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"  ✓ cwltool: {version}")
            return True
        else:
            print("  ❌ cwltool: Not found")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ❌ cwltool: Not found")
        print("  Please install: npm install -g cwltool")
        return False


def test_aws_credentials():
    """Test AWS credentials configuration."""
    print("\nTesting AWS credentials...")
    
    try:
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("  ✓ AWS credentials configured")
            return True
        else:
            print("  ❌ AWS credentials not configured")
            print("  Please run: aws configure")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ❌ AWS CLI not found")
        return False


def test_docker_daemon():
    """Test Docker daemon."""
    print("\nTesting Docker daemon...")
    
    try:
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("  ✓ Docker daemon running")
            return True
        else:
            print("  ❌ Docker daemon not running")
            print("  Please start Docker daemon")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ❌ Docker not found")
        return False


def test_file_structure():
    """Test file structure."""
    print("\nTesting file structure...")
    
    required_files = [
        'README.md',
        'requirements.txt',
        'package.json',
        'cwl_to_nextflow.py',
        'validate_nextflow.py',
        'batch_converter.py',
        'src/__init__.py',
        'src/cwl_parser.py',
        'src/nextflow_generator.py',
        'src/aws_integration.py',
        'src/resource_mapper.py',
        'src/container_handler.py',
        'src/validation.py',
        'templates/base_template.nf',
        'templates/aws_healthomics_template.nf',
        'setup/configure_aws_healthomics.sh',
        'setup/install_dependencies.sh',
        'setup/setup_environment.py',
        'examples/cwl/rnaseq_analysis.cwl',
        'examples/cwl/variant_calling.cwl',
        'examples/nextflow/rnaseq_analysis.nf',
        'demos/basic_conversion.py',
        'demos/aws_healthomics_demo.py',
        'demos/batch_conversion.py',
        'tests/test_cwl_parser.py',
        'tests/test_nextflow_generator.py',
        'tests/test_aws_integration.py',
        'docs/migration_guide.md',
        'docs/aws_healthomics_setup.md'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\nMissing files: {len(missing_files)}")
        return False
    
    return True


def main():
    """Main test function."""
    print("CWL to Nextflow Migration Toolkit - Installation Test")
    print("=" * 60)
    
    tests = [
        ("Python Package Imports", test_python_imports),
        ("Custom Module Imports", test_custom_modules),
        ("Command Line Tools", test_command_line_tools),
        ("CWL Tool", test_cwl_tool),
        ("File Structure", test_file_structure),
        ("AWS Credentials", test_aws_credentials),
        ("Docker Daemon", test_docker_daemon)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Installation Test Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Installation is complete.")
        print("\nNext steps:")
        print("1. Run demos: python demos/basic_conversion.py")
        print("2. Configure AWS: ./setup/configure_aws_healthomics.sh")
        print("3. Start converting workflows!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please fix the issues above.")
        print("\nFor help:")
        print("1. Check the README.md for installation instructions")
        print("2. Run: ./setup/install_dependencies.sh")
        print("3. Check the troubleshooting guide")
        return 1


if __name__ == "__main__":
    sys.exit(main())

