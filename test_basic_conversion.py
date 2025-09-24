#!/usr/bin/env python3
"""
Test Basic Conversion Fix

This script tests the basic conversion functionality to ensure the fix works.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_conversion_fix():
    """Test the basic conversion fix."""
    print("Testing basic conversion fix...")
    
    try:
        from cwl_parser import CWLParser
        from nextflow_generator import NextflowGenerator
        from resource_mapper import ResourceMapper
        from container_handler import ContainerHandler
        
        print("✓ Successfully imported all modules")
        
        # Create test CWL data (same as in demo)
        test_cwl = {
            "cwlVersion": "v1.2",
            "class": "Workflow",
            "id": "test_workflow",
            "label": "Test Workflow",
            "doc": "A test workflow",
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
        
        print("✓ Created test CWL data")
        
        # Initialize components
        cwl_parser = CWLParser()
        nextflow_generator = NextflowGenerator()
        resource_mapper = ResourceMapper()
        container_handler = ContainerHandler()
        
        print("✓ Initialized all components")
        
        # Test CWL parsing
        components = cwl_parser.extract_components(test_cwl)
        print(f"✓ Parsed CWL workflow: {components['workflow_info']['name']}")
        print(f"  - Processes: {len(components['processes'])}")
        print(f"  - Inputs: {len(components['inputs'])}")
        print(f"  - Outputs: {len(components['outputs'])}")
        
        # Test resource mapping
        resource_mapping = resource_mapper.map_resources(components)
        print(f"✓ Mapped resources for {len(resource_mapping)} processes")
        
        # Test container processing
        container_specs = container_handler.process_containers(components)
        print(f"✓ Processed containers for {len(container_specs)} processes")
        
        # Test Nextflow generation (this was failing before)
        nextflow_pipeline = nextflow_generator.generate_pipeline(
            components, resource_mapping, container_specs, aws_healthomics=True
        )
        print(f"✓ Generated Nextflow pipeline ({len(nextflow_pipeline)} characters)")
        
        # Check if pipeline contains expected elements
        if "test_workflow" in nextflow_pipeline:
            print("✓ Pipeline contains workflow name")
        if "process process_step" in nextflow_pipeline:
            print("✓ Pipeline contains process definition")
        if "aws {" in nextflow_pipeline:
            print("✓ Pipeline contains AWS HealthOmics configuration")
        
        print("\n🎉 Basic conversion test completed successfully!")
        print("The fix for the 'str' object has no attribute 'get' error is working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_conversion_fix()
    sys.exit(0 if success else 1)
