#!/usr/bin/env python3
"""
CWL to AWS HealthOmics Nextflow Migration Tool

This script converts Common Workflow Language (CWL) workflows to Nextflow pipelines
optimized for AWS HealthOmics platform.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

import click
import yaml
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import our custom modules
from src.cwl_parser import CWLParser
from src.nextflow_generator import NextflowGenerator
from src.aws_integration import AWSHealthOmicsIntegration
from src.resource_mapper import ResourceMapper
from src.container_handler import ContainerHandler
from src.validation import WorkflowValidator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("cwl_to_nextflow")
console = Console()


class CWLToNextflowConverter:
    """Main converter class for CWL to Nextflow migration."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the converter with configuration."""
        self.config = config or {}
        self.cwl_parser = CWLParser()
        self.nextflow_generator = NextflowGenerator()
        self.aws_integration = AWSHealthOmicsIntegration()
        self.resource_mapper = ResourceMapper()
        self.container_handler = ContainerHandler()
        self.validator = WorkflowValidator()
        
    def convert_workflow(
        self,
        cwl_path: str,
        output_dir: str,
        aws_healthomics: bool = False,
        optimize_resources: bool = False,
        instance_type: Optional[str] = None,
        custom_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert a CWL workflow to Nextflow.
        
        Args:
            cwl_path: Path to the CWL workflow file
            output_dir: Directory to output the Nextflow workflow
            aws_healthomics: Enable AWS HealthOmics optimizations
            optimize_resources: Optimize resource requirements
            instance_type: Target AWS instance type
            custom_template: Path to custom Nextflow template
            
        Returns:
            Dictionary with conversion results and metadata
        """
        console.print(f"[bold blue]Converting CWL workflow: {cwl_path}[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Step 1: Parse CWL workflow
            task1 = progress.add_task("Parsing CWL workflow...", total=None)
            cwl_data = self.cwl_parser.parse_cwl_file(cwl_path)
            progress.update(task1, description="✅ CWL workflow parsed")
            
            # Step 2: Extract workflow components
            task2 = progress.add_task("Extracting workflow components...", total=None)
            workflow_components = self.cwl_parser.extract_components(cwl_data)
            progress.update(task2, description="✅ Workflow components extracted")
            
            # Step 3: Map resources
            task3 = progress.add_task("Mapping resource requirements...", total=None)
            if optimize_resources:
                resource_mapping = self.resource_mapper.optimize_for_aws(
                    workflow_components, instance_type
                )
            else:
                resource_mapping = self.resource_mapper.map_resources(workflow_components)
            progress.update(task3, description="✅ Resources mapped")
            
            # Step 4: Handle containers
            task4 = progress.add_task("Processing container specifications...", total=None)
            container_specs = self.container_handler.process_containers(workflow_components)
            progress.update(task4, description="✅ Containers processed")
            
            # Step 5: Generate Nextflow pipeline
            task5 = progress.add_task("Generating Nextflow pipeline...", total=None)
            nextflow_pipeline = self.nextflow_generator.generate_pipeline(
                workflow_components,
                resource_mapping,
                container_specs,
                aws_healthomics=aws_healthomics,
                custom_template=custom_template
            )
            progress.update(task5, description="✅ Nextflow pipeline generated")
            
            # Step 6: AWS HealthOmics integration
            if aws_healthomics:
                task6 = progress.add_task("Integrating AWS HealthOmics features...", total=None)
                nextflow_pipeline = self.aws_integration.add_healthomics_features(
                    nextflow_pipeline, workflow_components
                )
                progress.update(task6, description="✅ AWS HealthOmics integrated")
            
            # Step 7: Validate generated workflow
            task7 = progress.add_task("Validating Nextflow workflow...", total=None)
            validation_results = self.validator.validate_nextflow(nextflow_pipeline)
            progress.update(task7, description="✅ Workflow validated")
            
            # Step 8: Save output
            task8 = progress.add_task("Saving output files...", total=None)
            output_files = self._save_output(
                nextflow_pipeline, output_dir, cwl_path, validation_results
            )
            progress.update(task8, description="✅ Output saved")
        
        # Prepare results
        results = {
            "input_file": cwl_path,
            "output_directory": output_dir,
            "output_files": output_files,
            "validation_results": validation_results,
            "aws_healthomics_enabled": aws_healthomics,
            "resource_optimization": optimize_resources,
            "instance_type": instance_type,
            "conversion_successful": validation_results.get("valid", False)
        }
        
        console.print(f"[bold green]✅ Conversion completed successfully![/bold green]")
        console.print(f"[green]Output directory: {output_dir}[/green]")
        
        return results
    
    def _save_output(
        self,
        nextflow_pipeline: str,
        output_dir: str,
        cwl_path: str,
        validation_results: Dict[str, Any]
    ) -> Dict[str, str]:
        """Save the generated Nextflow pipeline and related files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename
        cwl_name = Path(cwl_path).stem
        nextflow_file = output_path / f"{cwl_name}.nf"
        
        # Save main Nextflow pipeline
        with open(nextflow_file, 'w') as f:
            f.write(nextflow_pipeline)
        
        # Save configuration file
        config_file = output_path / f"{cwl_name}_config.nf"
        config_content = self._generate_config_file(validation_results)
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        # Save metadata
        metadata_file = output_path / f"{cwl_name}_metadata.json"
        metadata = {
            "original_cwl": cwl_path,
            "conversion_timestamp": str(Path().cwd()),
            "nextflow_version": "23.10.0",
            "aws_healthomics_enabled": self.config.get("aws_healthomics", False),
            "validation_results": validation_results
        }
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "nextflow_pipeline": str(nextflow_file),
            "config_file": str(config_file),
            "metadata_file": str(metadata_file)
        }
    
    def _generate_config_file(self, validation_results: Dict[str, Any]) -> str:
        """Generate Nextflow configuration file."""
        config_template = """
// Nextflow configuration for AWS HealthOmics
process {
    executor = 'awsbatch'
    queue = 'default'
    container = 'your-container-registry/nextflow:latest'
    
    // Resource allocation
    cpus = 2
    memory = '4 GB'
    time = '1h'
    
    // Error handling
    errorStrategy = 'retry'
    maxRetries = 3
}

// AWS HealthOmics specific configuration
aws {
    region = 'us-east-1'
    batch {
        cliPath = '/usr/local/bin/aws'
        jobRole = 'arn:aws:iam::YOUR_ACCOUNT:role/HealthOmicsExecutionRole'
    }
}

// Execution profiles
profiles {
    local {
        process.executor = 'local'
    }
    
    aws {
        process.executor = 'awsbatch'
        aws.region = 'us-east-1'
    }
    
    healthomics {
        process.executor = 'awsbatch'
        aws.region = 'us-east-1'
        process.container = 'public.ecr.aws/healthomics/nextflow:latest'
    }
}
"""
        return config_template


@click.command()
@click.option('--input', '-i', required=True, help='Input CWL workflow file')
@click.option('--output', '-o', required=True, help='Output directory for Nextflow workflow')
@click.option('--aws-healthomics', is_flag=True, help='Enable AWS HealthOmics optimizations')
@click.option('--optimize-resources', is_flag=True, help='Optimize resource requirements for AWS')
@click.option('--instance-type', help='Target AWS instance type (e.g., m5.large)')
@click.option('--template', help='Path to custom Nextflow template')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--log-level', default='INFO', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']))
def main(input, output, aws_healthomics, optimize_resources, instance_type, template, debug, log_level):
    """Convert CWL workflow to Nextflow for AWS HealthOmics."""
    
    # Set logging level
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(getattr(logging, log_level))
    
    # Validate input file
    if not os.path.exists(input):
        console.print(f"[bold red]Error: Input file '{input}' does not exist[/bold red]")
        sys.exit(1)
    
    # Create converter
    config = {
        "aws_healthomics": aws_healthomics,
        "optimize_resources": optimize_resources,
        "instance_type": instance_type
    }
    
    converter = CWLToNextflowConverter(config)
    
    try:
        # Convert workflow
        results = converter.convert_workflow(
            cwl_path=input,
            output_dir=output,
            aws_healthomics=aws_healthomics,
            optimize_resources=optimize_resources,
            instance_type=instance_type,
            custom_template=template
        )
        
        # Print summary
        console.print("\n[bold]Conversion Summary:[/bold]")
        console.print(f"Input: {results['input_file']}")
        console.print(f"Output: {results['output_directory']}")
        console.print(f"AWS HealthOmics: {'Enabled' if results['aws_healthomics_enabled'] else 'Disabled'}")
        console.print(f"Resource Optimization: {'Enabled' if results['resource_optimization'] else 'Disabled'}")
        console.print(f"Success: {'✅' if results['conversion_successful'] else '❌'}")
        
        if not results['conversion_successful']:
            console.print("\n[bold red]Validation Issues:[/bold red]")
            for issue in results['validation_results'].get('issues', []):
                console.print(f"  - {issue}")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[bold red]Conversion failed: {str(e)}[/bold red]")
        if debug:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()

