#!/usr/bin/env python3
"""
Batch CWL to Nextflow Converter

Converts multiple CWL workflows to Nextflow in batch mode.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from cwl_to_nextflow import CWLToNextflowConverter

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

console = Console()


class BatchConverter:
    """Batch converter for multiple CWL workflows."""
    
    def __init__(self):
        """Initialize batch converter."""
        self.converter = CWLToNextflowConverter()
        self.results = []
        self.errors = []
    
    def find_cwl_files(self, input_dir: str) -> List[str]:
        """Find all CWL files in input directory."""
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory '{input_dir}' does not exist")
        
        # Find all .cwl files recursively
        cwl_files = list(input_path.rglob("*.cwl"))
        
        if not cwl_files:
            raise FileNotFoundError(f"No .cwl files found in '{input_dir}'")
        
        return [str(f) for f in cwl_files]
    
    def convert_batch(
        self,
        input_dir: str,
        output_dir: str,
        aws_healthomics: bool = False,
        optimize_resources: bool = False,
        instance_type: str = None
    ) -> Dict[str, Any]:
        """Convert all CWL files in batch."""
        
        # Find CWL files
        cwl_files = self.find_cwl_files(input_dir)
        
        console.print(f"[bold blue]Found {len(cwl_files)} CWL workflows to convert[/bold blue]")
        
        # Convert each workflow
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            
            task = progress.add_task("Converting workflows...", total=len(cwl_files))
            
            for cwl_file in cwl_files:
                try:
                    # Create output subdirectory for this workflow
                    workflow_name = Path(cwl_file).stem
                    workflow_output_dir = Path(output_dir) / workflow_name
                    
                    # Convert workflow
                    result = self.converter.convert_workflow(
                        cwl_path=cwl_file,
                        output_dir=str(workflow_output_dir),
                        aws_healthomics=aws_healthomics,
                        optimize_resources=optimize_resources,
                        instance_type=instance_type
                    )
                    
                    self.results.append(result)
                    progress.update(task, advance=1, description=f"Converted {workflow_name}")
                    
                except Exception as e:
                    error_result = {
                        "input_file": cwl_file,
                        "error": str(e),
                        "conversion_successful": False
                    }
                    self.results.append(error_result)
                    self.errors.append(f"{cwl_file}: {str(e)}")
                    progress.update(task, advance=1, description=f"Failed {Path(cwl_file).stem}")
        
        # Generate summary
        successful = [r for r in self.results if r.get("conversion_successful", False)]
        failed = [r for r in self.results if not r.get("conversion_successful", False)]
        
        summary = {
            "total_workflows": len(cwl_files),
            "successful_conversions": len(successful),
            "failed_conversions": len(failed),
            "success_rate": len(successful) / len(cwl_files) * 100 if cwl_files else 0,
            "aws_healthomics_enabled": aws_healthomics,
            "optimize_resources": optimize_resources,
            "instance_type": instance_type,
            "results": self.results,
            "errors": self.errors
        }
        
        return summary
    
    def generate_report(self, summary: Dict[str, Any]) -> str:
        """Generate batch conversion report."""
        
        report_lines = [
            "CWL to Nextflow Batch Conversion Report",
            "=" * 60,
            "",
            f"Total Workflows: {summary['total_workflows']}",
            f"Successful Conversions: {summary['successful_conversions']}",
            f"Failed Conversions: {summary['failed_conversions']}",
            f"Success Rate: {summary['success_rate']:.1f}%",
            f"AWS HealthOmics Enabled: {summary['aws_healthomics_enabled']}",
            f"Resource Optimization: {summary['optimize_resources']}",
            f"Instance Type: {summary['instance_type'] or 'Default'}",
            ""
        ]
        
        # Successful conversions
        if summary['successful_conversions'] > 0:
            report_lines.extend([
                "Successful Conversions:",
                "-" * 30
            ])
            
            for result in summary['results']:
                if result.get("conversion_successful", False):
                    report_lines.extend([
                        f"  Workflow: {Path(result['input_file']).stem}",
                        f"    Input: {result['input_file']}",
                        f"    Output: {result['output_directory']}",
                        f"    Valid: {result.get('validation_results', {}).get('valid', False)}",
                        f"    Score: {result.get('validation_results', {}).get('overall_score', 0):.1f}/100",
                        ""
                    ])
        
        # Failed conversions
        if summary['failed_conversions'] > 0:
            report_lines.extend([
                "Failed Conversions:",
                "-" * 30
            ])
            
            for result in summary['results']:
                if not result.get("conversion_successful", False):
                    report_lines.extend([
                        f"  Workflow: {Path(result['input_file']).stem}",
                        f"    Input: {result['input_file']}",
                        f"    Error: {result.get('error', 'Unknown error')}",
                        ""
                    ])
        
        # Recommendations
        report_lines.extend([
            "Recommendations:",
            "-" * 30
        ])
        
        if summary['failed_conversions'] > 0:
            report_lines.append("  - Review failed conversions and fix CWL syntax issues")
        
        if summary['success_rate'] < 100:
            report_lines.append("  - Consider running individual conversions to debug issues")
        
        report_lines.extend([
            "  - Test converted workflows with Nextflow before deployment",
            "  - Review validation reports for quality improvements",
            "  - Consider AWS HealthOmics optimization for production use"
        ])
        
        return "\n".join(report_lines)


@click.command()
@click.option('--input-dir', '-i', required=True, help='Input directory containing CWL workflows')
@click.option('--output-dir', '-o', required=True, help='Output directory for Nextflow workflows')
@click.option('--aws-healthomics', is_flag=True, help='Enable AWS HealthOmics optimizations')
@click.option('--optimize-resources', is_flag=True, help='Optimize resource requirements for AWS')
@click.option('--instance-type', help='Target AWS instance type (e.g., m5.large)')
@click.option('--report', help='Output file for batch conversion report')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def main(input_dir, output_dir, aws_healthomics, optimize_resources, instance_type, report, debug):
    """Convert multiple CWL workflows to Nextflow in batch mode."""
    
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Initialize batch converter
    batch_converter = BatchConverter()
    
    try:
        # Convert workflows
        console.print(f"[bold blue]Starting batch conversion...[/bold blue]")
        console.print(f"Input directory: {input_dir}")
        console.print(f"Output directory: {output_dir}")
        console.print(f"AWS HealthOmics: {'Enabled' if aws_healthomics else 'Disabled'}")
        console.print(f"Resource optimization: {'Enabled' if optimize_resources else 'Disabled'}")
        if instance_type:
            console.print(f"Instance type: {instance_type}")
        console.print("")
        
        summary = batch_converter.convert_batch(
            input_dir=input_dir,
            output_dir=output_dir,
            aws_healthomics=aws_healthomics,
            optimize_resources=optimize_resources,
            instance_type=instance_type
        )
        
        # Display summary
        console.print(f"\n[bold]Batch Conversion Summary:[/bold]")
        console.print(f"Total workflows: {summary['total_workflows']}")
        console.print(f"Successful: {summary['successful_conversions']}")
        console.print(f"Failed: {summary['failed_conversions']}")
        console.print(f"Success rate: {summary['success_rate']:.1f}%")
        
        # Generate and save report
        if report:
            report_content = batch_converter.generate_report(summary)
            with open(report, 'w') as f:
                f.write(report_content)
            console.print(f"\n[green]Batch report saved to: {report}[/green]")
        
        # Display errors if any
        if summary['errors']:
            console.print(f"\n[bold red]Errors encountered:[/bold red]")
            for error in summary['errors']:
                console.print(f"  - {error}")
        
        # Exit with appropriate code
        if summary['failed_conversions'] > 0:
            console.print(f"\n[bold yellow]Batch conversion completed with {summary['failed_conversions']} failures[/bold yellow]")
            sys.exit(1)
        else:
            console.print(f"\n[bold green]Batch conversion completed successfully![/bold green]")
            sys.exit(0)
            
    except Exception as e:
        console.print(f"[bold red]Batch conversion failed: {str(e)}[/bold red]")
        if debug:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()

