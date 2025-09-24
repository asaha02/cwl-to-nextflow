#!/usr/bin/env python3
"""
Basic CWL to Nextflow Conversion Demo

This script demonstrates the basic conversion of a CWL workflow to Nextflow.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.cwl_parser import CWLParser
from src.nextflow_generator import NextflowGenerator
from src.resource_mapper import ResourceMapper
from src.container_handler import ContainerHandler
from src.validation import WorkflowValidator

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_basic_conversion():
    """Demonstrate basic CWL to Nextflow conversion."""
    
    print("=" * 60)
    print("CWL to Nextflow Migration - Basic Conversion Demo")
    print("=" * 60)
    
    # Initialize components
    cwl_parser = CWLParser()
    nextflow_generator = NextflowGenerator()
    resource_mapper = ResourceMapper()
    container_handler = ContainerHandler()
    validator = WorkflowValidator()
    
    # Example CWL workflow (simplified)
    example_cwl = {
        "cwlVersion": "v1.2",
        "class": "Workflow",
        "id": "example_workflow",
        "label": "Example Workflow",
        "doc": "A simple example workflow",
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
            },
            {
                "class": "ResourceRequirement",
                "coresMin": 4,
                "ramMin": 8000000000
            }
        ]
    }
    
    print("\n1. Parsing CWL workflow...")
    try:
        # Extract components
        components = cwl_parser.extract_components(example_cwl)
        print(f"   ✓ Parsed workflow: {components['workflow_info']['name']}")
        print(f"   ✓ Found {len(components['processes'])} processes")
        print(f"   ✓ Found {len(components['inputs'])} inputs")
        print(f"   ✓ Found {len(components['outputs'])} outputs")
    except Exception as e:
        print(f"   ❌ Error parsing CWL: {e}")
        return False
    
    print("\n2. Mapping resources...")
    try:
        resource_mapping = resource_mapper.map_resources(components)
        print(f"   ✓ Mapped resources for {len(resource_mapping)} processes")
        
        # Show resource mapping
        for process_name, resources in resource_mapping.items():
            print(f"     - {process_name}: {resources.get('cpus', 'N/A')} CPUs, {resources.get('memory', 'N/A')} memory")
    except Exception as e:
        print(f"   ❌ Error mapping resources: {e}")
        return False
    
    print("\n3. Processing containers...")
    try:
        container_specs = container_handler.process_containers(components)
        print(f"   ✓ Processed containers for {len(container_specs)} processes")
        
        # Show container specs
        for process_name, spec in container_specs.items():
            print(f"     - {process_name}: {spec.get('image', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error processing containers: {e}")
        return False
    
    print("\n4. Generating Nextflow pipeline...")
    try:
        nextflow_pipeline = nextflow_generator.generate_pipeline(
            components, resource_mapping, container_specs, aws_healthomics=True
        )
        print(f"   ✓ Generated Nextflow pipeline ({len(nextflow_pipeline)} characters)")
    except Exception as e:
        print(f"   ❌ Error generating Nextflow: {e}")
        return False
    
    print("\n5. Validating generated workflow...")
    try:
        validation_results = validator.validate_nextflow(nextflow_pipeline)
        print(f"   ✓ Validation completed")
        print(f"   ✓ Overall score: {validation_results.get('overall_score', 0):.1f}/100")
        
        if validation_results.get('valid', False):
            print("   ✓ Workflow is valid")
        else:
            print("   ⚠️  Workflow has issues:")
            for issue in validation_results.get('issues', []):
                print(f"     - {issue}")
    except Exception as e:
        print(f"   ❌ Error validating workflow: {e}")
        return False
    
    print("\n6. Saving output...")
    try:
        output_dir = Path("demo_output")
        output_dir.mkdir(exist_ok=True)
        
        # Save Nextflow pipeline
        nextflow_file = output_dir / "example_workflow.nf"
        with open(nextflow_file, 'w') as f:
            f.write(nextflow_pipeline)
        print(f"   ✓ Saved Nextflow pipeline: {nextflow_file}")
        
        # Save configuration
        config_file = output_dir / "example_workflow_config.nf"
        config_content = nextflow_generator.generate_config_file(
            components, resource_mapping, aws_healthomics=True
        )
        with open(config_file, 'w') as f:
            f.write(config_content)
        print(f"   ✓ Saved configuration: {config_file}")
        
        # Save validation report
        report_file = output_dir / "validation_report.txt"
        report_content = validator.generate_validation_report(validation_results)
        with open(report_file, 'w') as f:
            f.write(report_content)
        print(f"   ✓ Saved validation report: {report_file}")
        
    except Exception as e:
        print(f"   ❌ Error saving output: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    print("\nGenerated files:")
    print(f"  - {nextflow_file}")
    print(f"  - {config_file}")
    print(f"  - {report_file}")
    print("\nNext steps:")
    print("  1. Review the generated Nextflow pipeline")
    print("  2. Test with: nextflow run example_workflow.nf")
    print("  3. Deploy to AWS HealthOmics")
    
    return True


def demo_advanced_features():
    """Demonstrate advanced conversion features."""
    
    print("\n" + "=" * 60)
    print("Advanced Features Demo")
    print("=" * 60)
    
    # Initialize components
    resource_mapper = ResourceMapper()
    container_handler = ContainerHandler()
    
    print("\n1. Resource optimization demo...")
    
    # Example with different instance types
    instance_types = ["t3.small", "t3.large", "m5.xlarge", "c5.2xlarge"]
    
    for instance_type in instance_types:
        print(f"\n   Optimizing for {instance_type}:")
        
        # Mock components
        mock_components = {
            "processes": {
                "example_process": {
                    "requirements": [
                        {"class": "ResourceRequirement", "coresMin": 8, "ramMin": 16000000000}
                    ]
                }
            }
        }
        
        try:
            optimized = resource_mapper.optimize_for_aws(mock_components, instance_type)
            process_resources = optimized.get("example_process", {})
            print(f"     - CPUs: {process_resources.get('cpus', 'N/A')}")
            print(f"     - Memory: {process_resources.get('memory', 'N/A')}")
            print(f"     - Instance: {process_resources.get('instance_type', 'N/A')}")
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    print("\n2. Container optimization demo...")
    
    # Example containers
    example_containers = [
        "docker.io/bwa:latest",
        "quay.io/biocontainers/samtools:1.15",
        "gcr.io/google-containers/busybox:1.0"
    ]
    
    for container in example_containers:
        print(f"\n   Optimizing container: {container}")
        
        try:
            # Mock container spec
            mock_spec = {"image": container}
            optimized = container_handler._optimize_for_aws(mock_spec)
            print(f"     - Original: {container}")
            print(f"     - Optimized: {optimized.get('image', 'N/A')}")
            print(f"     - AWS optimized: {optimized.get('aws_optimized', False)}")
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    print("\n3. Resource report generation...")
    
    try:
        # Mock resource mapping
        mock_mapping = {
            "process1": {"cpus": 4, "memory": "8 GB", "time": "2h"},
            "process2": {"cpus": 2, "memory": "4 GB", "time": "1h"},
            "process3": {"cpus": 8, "memory": "16 GB", "time": "4h"}
        }
        
        report = resource_mapper.generate_resource_report(mock_mapping)
        print("   ✓ Generated resource report:")
        print(report)
        
    except Exception as e:
        print(f"   ❌ Error generating report: {e}")


def main():
    """Main demo function."""
    
    print("CWL to Nextflow Migration Toolkit - Demo")
    print("This demo shows the basic conversion process and advanced features.")
    
    # Run basic conversion demo
    success = demo_basic_conversion()
    
    if success:
        # Run advanced features demo
        demo_advanced_features()
        
        print("\n" + "=" * 60)
        print("All demos completed successfully!")
        print("=" * 60)
        print("\nTo run your own conversions:")
        print("  python cwl_to_nextflow.py --input your_workflow.cwl --output ./output/")
        print("\nTo validate workflows:")
        print("  python validate_nextflow.py --workflow your_workflow.nf")
    else:
        print("\n" + "=" * 60)
        print("Demo failed. Please check the errors above.")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()

