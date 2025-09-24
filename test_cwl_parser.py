#!/usr/bin/env python3
"""
Simple test for cwl_parser module
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_cwl_parser():
    """Test cwl_parser module import and basic functionality."""
    print("Testing cwl_parser module...")
    
    try:
        # Try to import the module
        from cwl_parser import CWLParser
        print("✓ Successfully imported CWLParser")
        
        # Try to create an instance
        parser = CWLParser()
        print("✓ Successfully created CWLParser instance")
        
        # Test basic functionality with a simple CWL structure
        test_cwl = {
            "cwlVersion": "v1.2",
            "class": "Workflow",
            "id": "test_workflow",
            "inputs": {},
            "outputs": {},
            "steps": {}
        }
        
        # Test extract_components method
        components = parser.extract_components(test_cwl)
        print("✓ Successfully extracted components from test CWL")
        
        # Check if components have expected structure
        expected_keys = ["workflow_info", "inputs", "outputs", "processes", "requirements", "hints", "dependencies"]
        for key in expected_keys:
            if key in components:
                print(f"✓ Component has {key}")
            else:
                print(f"❌ Component missing {key}")
        
        print("\n🎉 cwl_parser module test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nThis might be due to missing dependencies. Try installing:")
        print("  pip install cwltool ruamel.yaml")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_cwl_parser()
    sys.exit(0 if success else 1)
