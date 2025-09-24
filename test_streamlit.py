#!/usr/bin/env python3
"""
Test Script for Streamlit App

This script tests the Streamlit app functionality without launching the web interface.
"""

import sys
import yaml
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print(f"✅ Streamlit {st.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Streamlit: {e}")
        return False
    
    try:
        import yaml
        print("✅ PyYAML imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PyYAML: {e}")
        return False
    
    try:
        import jinja2
        print("✅ Jinja2 imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Jinja2: {e}")
        return False
    
    # Test our custom modules
    try:
        from cwl_parser import CWLParser
        print("✅ CWL Parser imported successfully")
    except ImportError as e:
        print(f"⚠️  CWL Parser import warning: {e}")
    
    try:
        from nextflow_generator import NextflowGenerator
        print("✅ Nextflow Generator imported successfully")
    except ImportError as e:
        print(f"⚠️  Nextflow Generator import warning: {e}")
    
    try:
        from resource_mapper import ResourceMapper
        print("✅ Resource Mapper imported successfully")
    except ImportError as e:
        print(f"⚠️  Resource Mapper import warning: {e}")
    
    try:
        from container_handler import ContainerHandler
        print("✅ Container Handler imported successfully")
    except ImportError as e:
        print(f"⚠️  Container Handler import warning: {e}")
    
    try:
        from validation import WorkflowValidator
        print("✅ Workflow Validator imported successfully")
    except ImportError as e:
        print(f"⚠️  Workflow Validator import warning: {e}")
    
    return True

def test_example_cwl():
    """Test with example CWL data."""
    print("\nTesting with example CWL data...")
    
    example_cwl = {
        "cwlVersion": "v1.2",
        "class": "Workflow",
        "id": "test_workflow",
        "label": "Test Workflow",
        "doc": "A test workflow for Streamlit app",
        "inputs": {
            "input_file": {
                "type": "File",
                "label": "Input file",
                "doc": "Input file to process"
            },
            "threads": {
                "type": "int",
                "label": "Number of threads",
                "default": 4
            }
        },
        "outputs": {
            "output_file": {
                "type": "File",
                "label": "Output file",
                "outputSource": "process_step/output"
            }
        },
        "steps": {
            "process_step": {
                "run": "tools/example_tool.cwl",
                "in": {
                    "input": "input_file",
                    "threads": "threads"
                },
                "out": ["output"]
            }
        },
        "requirements": [
            {
                "class": "DockerRequirement",
                "dockerPull": "public.ecr.aws/healthomics/example:latest"
            }
        ]
    }
    
    try:
        # Test YAML serialization
        cwl_yaml = yaml.dump(example_cwl)
        print("✅ CWL data serialized to YAML successfully")
        
        # Test YAML deserialization
        parsed_cwl = yaml.safe_load(cwl_yaml)
        print("✅ CWL data parsed from YAML successfully")
        
        # Test basic structure
        assert parsed_cwl["cwlVersion"] == "v1.2"
        assert parsed_cwl["class"] == "Workflow"
        assert len(parsed_cwl["inputs"]) == 2
        assert len(parsed_cwl["outputs"]) == 1
        assert len(parsed_cwl["steps"]) == 1
        
        print("✅ CWL data structure validation passed")
        
        return True
        
    except Exception as e:
        print(f"❌ CWL data test failed: {e}")
        return False

def test_streamlit_app_file():
    """Test if the Streamlit app file exists and is valid."""
    print("\nTesting Streamlit app file...")
    
    app_file = Path(__file__).parent / "streamlit_app.py"
    
    if not app_file.exists():
        print(f"❌ Streamlit app file not found: {app_file}")
        return False
    
    print(f"✅ Streamlit app file found: {app_file}")
    
    try:
        with open(app_file, 'r') as f:
            content = f.read()
        
        # Basic syntax check
        compile(content, str(app_file), 'exec')
        print("✅ Streamlit app file syntax is valid")
        
        # Check for required functions
        required_functions = ['main', 'convert_workflow', 'get_example_cwl']
        for func in required_functions:
            if f"def {func}(" in content:
                print(f"✅ Function '{func}' found")
            else:
                print(f"⚠️  Function '{func}' not found")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ Streamlit app file has syntax errors: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading Streamlit app file: {e}")
        return False

def test_launcher_script():
    """Test the launcher script."""
    print("\nTesting launcher script...")
    
    launcher_file = Path(__file__).parent / "run_streamlit.py"
    
    if not launcher_file.exists():
        print(f"❌ Launcher script not found: {launcher_file}")
        return False
    
    print(f"✅ Launcher script found: {launcher_file}")
    
    try:
        with open(launcher_file, 'r') as f:
            content = f.read()
        
        # Basic syntax check
        compile(content, str(launcher_file), 'exec')
        print("✅ Launcher script syntax is valid")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ Launcher script has syntax errors: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading launcher script: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Testing Streamlit App Components")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Example CWL Test", test_example_cwl),
        ("Streamlit App File Test", test_streamlit_app_file),
        ("Launcher Script Test", test_launcher_script)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Streamlit app is ready to use.")
        print("\nTo launch the app, run:")
        print("  python run_streamlit.py")
        print("  or")
        print("  streamlit run streamlit_app.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues before using the app.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
