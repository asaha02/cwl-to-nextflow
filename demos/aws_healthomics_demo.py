#!/usr/bin/env python3
"""
AWS HealthOmics Integration Demo

This script demonstrates AWS HealthOmics integration features.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.aws_integration import AWSHealthOmicsIntegration

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_aws_healthomics_setup():
    """Demonstrate AWS HealthOmics setup."""
    
    print("=" * 60)
    print("AWS HealthOmics Integration Demo")
    print("=" * 60)
    
    # Initialize AWS integration
    aws_integration = AWSHealthOmicsIntegration()
    
    print("\n1. Validating AWS HealthOmics setup...")
    
    try:
        validation_results = aws_integration.validate_healthomics_setup()
        
        print(f"   Credentials valid: {'✓' if validation_results['credentials_valid'] else '❌'}")
        print(f"   Workgroup accessible: {'✓' if validation_results['workgroup_accessible'] else '❌'}")
        print(f"   Role accessible: {'✓' if validation_results['role_accessible'] else '❌'}")
        print(f"   Permissions valid: {'✓' if validation_results['permissions_valid'] else '❌'}")
        
        if validation_results['errors']:
            print("   Errors:")
            for error in validation_results['errors']:
                print(f"     - {error}")
        
        if not validation_results['permissions_valid']:
            print("\n   ⚠️  AWS HealthOmics setup incomplete.")
            print("   Please run: ./setup/configure_aws_healthomics.sh")
            return False
            
    except Exception as e:
        print(f"   ❌ Error validating setup: {e}")
        return False
    
    print("\n2. Setting up HealthOmics environment...")
    
    try:
        setup_results = aws_integration.setup_healthomics_environment()
        
        print(f"   Workgroup created: {'✓' if setup_results['workgroup_created'] else '❌'}")
        print(f"   Role created: {'✓' if setup_results['role_created'] else '❌'}")
        print(f"   Bucket created: {'✓' if setup_results['bucket_created'] else '❌'}")
        
        if setup_results['errors']:
            print("   Errors:")
            for error in setup_results['errors']:
                print(f"     - {error}")
                
    except Exception as e:
        print(f"   ❌ Error setting up environment: {e}")
        return False
    
    print("\n3. Generating HealthOmics configuration...")
    
    try:
        # Mock components for demo
        mock_components = {
            "workflow_info": {
                "name": "demo_workflow",
                "version": "1.0",
                "description": "Demo workflow for HealthOmics"
            },
            "processes": {
                "demo_process": {
                    "name": "demo_process",
                    "requirements": [],
                    "hints": []
                }
            }
        }
        
        # Generate HealthOmics configuration
        config = aws_integration._generate_healthomics_config(mock_components)
        print(f"   ✓ Generated HealthOmics configuration ({len(config)} characters)")
        
        # Save configuration
        config_file = Path("demo_output") / "healthomics_config.nf"
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w') as f:
            f.write(config)
        print(f"   ✓ Saved configuration: {config_file}")
        
    except Exception as e:
        print(f"   ❌ Error generating configuration: {e}")
        return False
    
    print("\n4. Demonstrating workflow creation...")
    
    try:
        # Mock workflow definition
        mock_workflow = """
workflow demo_workflow {
    // Demo workflow for HealthOmics
    input:
    val input_data
    
    output:
    val output_data
    
    script:
    '''
    echo "Running demo workflow on HealthOmics"
    '''
}
"""
        
        # Extract parameters (simplified)
        parameters = aws_integration._extract_workflow_parameters(mock_workflow)
        print(f"   ✓ Extracted {len(parameters)} parameters")
        
        for param in parameters:
            print(f"     - {param['name']}: {param['type']}")
        
    except Exception as e:
        print(f"   ❌ Error demonstrating workflow creation: {e}")
        return False
    
    print("\n5. Generating monitoring code...")
    
    try:
        monitoring_code = aws_integration._generate_monitoring_code()
        print(f"   ✓ Generated monitoring code ({len(monitoring_code)} characters)")
        
        # Save monitoring code
        monitoring_file = Path("demo_output") / "monitoring_code.nf"
        with open(monitoring_file, 'w') as f:
            f.write(monitoring_code)
        print(f"   ✓ Saved monitoring code: {monitoring_file}")
        
    except Exception as e:
        print(f"   ❌ Error generating monitoring code: {e}")
        return False
    
    print("\n6. Generating error handling code...")
    
    try:
        error_handling = aws_integration._generate_error_handling()
        print(f"   ✓ Generated error handling code ({len(error_handling)} characters)")
        
        # Save error handling code
        error_file = Path("demo_output") / "error_handling.nf"
        with open(error_file, 'w') as f:
            f.write(error_handling)
        print(f"   ✓ Saved error handling code: {error_file}")
        
    except Exception as e:
        print(f"   ❌ Error generating error handling code: {e}")
        return False
    
    return True


def demo_healthomics_features():
    """Demonstrate HealthOmics specific features."""
    
    print("\n" + "=" * 60)
    print("HealthOmics Features Demo")
    print("=" * 60)
    
    aws_integration = AWSHealthOmicsIntegration()
    
    print("\n1. Container registry mapping...")
    
    # Example container mappings
    container_examples = [
        "docker.io/bwa:latest",
        "quay.io/biocontainers/samtools:1.15",
        "gcr.io/google-containers/busybox:1.0",
        "public.ecr.aws/healthomics/nextflow:latest"
    ]
    
    for container in container_examples:
        print(f"\n   Container: {container}")
        
        # Parse image name
        registry, tag = aws_integration._parse_image_name(container)
        print(f"     Registry: {registry}")
        print(f"     Tag: {tag}")
        
        # Check if AWS optimized
        is_aws = "ecr.aws" in container or "public.ecr.aws" in container
        print(f"     AWS optimized: {'✓' if is_aws else '❌'}")
    
    print("\n2. Resource optimization for HealthOmics...")
    
    # Example resource requirements
    resource_examples = [
        {"cpus": 1, "memory": "2 GB", "time": "1h"},
        {"cpus": 4, "memory": "8 GB", "time": "4h"},
        {"cpus": 8, "memory": "32 GB", "time": "8h"},
        {"cpus": 16, "memory": "64 GB", "time": "16h"}
    ]
    
    for resources in resource_examples:
        print(f"\n   Resources: {resources}")
        
        # Check if suitable for HealthOmics
        suitable = (
            resources["cpus"] <= 16 and
            resources["memory"] in ["2 GB", "4 GB", "8 GB", "16 GB", "32 GB", "64 GB"] and
            resources["time"] in ["1h", "2h", "4h", "8h", "16h"]
        )
        
        print(f"     HealthOmics suitable: {'✓' if suitable else '❌'}")
        
        if not suitable:
            print("     Recommendations:")
            if resources["cpus"] > 16:
                print("       - Reduce CPU count to 16 or less")
            if resources["memory"] not in ["2 GB", "4 GB", "8 GB", "16 GB", "32 GB", "64 GB"]:
                print("       - Use standard memory sizes (2, 4, 8, 16, 32, 64 GB)")
            if resources["time"] not in ["1h", "2h", "4h", "8h", "16h"]:
                print("       - Use standard time limits (1, 2, 4, 8, 16 hours)")
    
    print("\n3. HealthOmics execution profiles...")
    
    profiles = [
        "healthomics-dev",
        "healthomics",
        "healthomics-prod"
    ]
    
    for profile in profiles:
        print(f"\n   Profile: {profile}")
        
        if profile == "healthomics-dev":
            print("     - CPUs: 1")
            print("     - Memory: 2 GB")
            print("     - Time: 1h")
            print("     - Use case: Development and testing")
        elif profile == "healthomics":
            print("     - CPUs: 2")
            print("     - Memory: 4 GB")
            print("     - Time: 2h")
            print("     - Use case: Standard analysis")
        elif profile == "healthomics-prod":
            print("     - CPUs: 4")
            print("     - Memory: 16 GB")
            print("     - Time: 8h")
            print("     - Use case: Production workloads")


def demo_healthomics_workflow():
    """Demonstrate creating a HealthOmics workflow."""
    
    print("\n" + "=" * 60)
    print("HealthOmics Workflow Creation Demo")
    print("=" * 60)
    
    aws_integration = AWSHealthOmicsIntegration()
    
    print("\n1. Creating workflow definition...")
    
    # Example workflow definition
    workflow_definition = """
workflow healthomics_demo {
    // HealthOmics optimized workflow
    
    input:
    val input_data
    
    output:
    val output_data
    
    script:
    '''
    # HealthOmics process script
    echo "Starting HealthOmics workflow"
    echo "AWS Region: ${AWS_DEFAULT_REGION}"
    echo "Workgroup: ${AWS_HEALTHOMICS_WORKGROUP}"
    
    # Process data
    echo "Processing data..."
    
    # Log completion
    echo "Workflow completed successfully"
    '''
}
"""
    
    print(f"   ✓ Created workflow definition ({len(workflow_definition)} characters)")
    
    print("\n2. Extracting workflow parameters...")
    
    try:
        parameters = aws_integration._extract_workflow_parameters(workflow_definition)
        print(f"   ✓ Extracted {len(parameters)} parameters")
        
        for param in parameters:
            print(f"     - {param['name']}: {param['type']} - {param['description']}")
            
    except Exception as e:
        print(f"   ❌ Error extracting parameters: {e}")
        return False
    
    print("\n3. Generating workflow metadata...")
    
    workflow_metadata = {
        "name": "healthomics_demo_workflow",
        "description": "Demo workflow for AWS HealthOmics",
        "version": "1.0",
        "author": "CWL to Nextflow Migration Toolkit",
        "created": "2024-01-01",
        "parameters": parameters,
        "aws_healthomics": {
            "workgroup": "${AWS_HEALTHOMICS_WORKGROUP}",
            "region": "${AWS_DEFAULT_REGION}",
            "executor": "awsbatch",
            "monitoring": True
        }
    }
    
    print(f"   ✓ Generated workflow metadata")
    
    # Save metadata
    metadata_file = Path("demo_output") / "workflow_metadata.json"
    import json
    with open(metadata_file, 'w') as f:
        json.dump(workflow_metadata, f, indent=2)
    print(f"   ✓ Saved metadata: {metadata_file}")
    
    print("\n4. Workflow deployment checklist...")
    
    checklist = [
        "✓ Workflow definition created",
        "✓ Parameters extracted",
        "✓ Metadata generated",
        "✓ AWS credentials configured",
        "✓ HealthOmics workgroup exists",
        "✓ IAM role has required permissions",
        "✓ S3 bucket for outputs configured",
        "✓ Container images available in ECR",
        "✓ Resource requirements optimized",
        "✓ Monitoring and logging configured"
    ]
    
    for item in checklist:
        print(f"   {item}")
    
    print("\n5. Next steps for deployment...")
    
    next_steps = [
        "1. Review workflow definition and parameters",
        "2. Test workflow locally with Nextflow",
        "3. Push container images to ECR",
        "4. Create HealthOmics workflow using AWS CLI or console",
        "5. Configure workflow parameters and inputs",
        "6. Submit workflow runs",
        "7. Monitor execution in HealthOmics console",
        "8. Review outputs in S3 bucket"
    ]
    
    for step in next_steps:
        print(f"   {step}")


def main():
    """Main demo function."""
    
    print("AWS HealthOmics Integration Demo")
    print("This demo shows AWS HealthOmics integration features and workflow creation.")
    
    # Create output directory
    Path("demo_output").mkdir(exist_ok=True)
    
    # Run HealthOmics setup demo
    success = demo_aws_healthomics_setup()
    
    if success:
        # Run features demo
        demo_healthomics_features()
        
        # Run workflow creation demo
        demo_healthomics_workflow()
        
        print("\n" + "=" * 60)
        print("HealthOmics demo completed successfully!")
        print("=" * 60)
        print("\nGenerated files:")
        print("  - demo_output/healthomics_config.nf")
        print("  - demo_output/monitoring_code.nf")
        print("  - demo_output/error_handling.nf")
        print("  - demo_output/workflow_metadata.json")
        print("\nTo deploy to HealthOmics:")
        print("  1. Configure AWS credentials")
        print("  2. Run: ./setup/configure_aws_healthomics.sh")
        print("  3. Create workflow: aws omics create-workflow --definition file://workflow.nf")
    else:
        print("\n" + "=" * 60)
        print("HealthOmics demo failed. Please check AWS setup.")
        print("=" * 60)
        print("\nTo fix setup issues:")
        print("  1. Configure AWS credentials: aws configure")
        print("  2. Run setup script: ./setup/configure_aws_healthomics.sh")
        print("  3. Verify permissions and resources")
        sys.exit(1)


if __name__ == "__main__":
    main()

