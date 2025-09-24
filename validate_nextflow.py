#!/usr/bin/env python3
"""
Nextflow Workflow Validation Script

Validates generated Nextflow workflows and provides quality checks.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.validation import WorkflowValidator

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

console = Console()


class NextflowValidator:
    """Validates Nextflow workflows."""
    
    def __init__(self):
        """Initialize the validator."""
        self.validator = WorkflowValidator()
    
    def validate_workflow_file(self, workflow_path: str) -> Dict[str, Any]:
        """
        Validate a Nextflow workflow file.
        
        Args:
            workflow_path: Path to the Nextflow workflow file
            
        Returns:
            Dictionary with validation results
        """
        console.print(f"[bold blue]Validating Nextflow workflow: {workflow_path}[/bold blue]")
        
        # Read workflow content
        try:
            with open(workflow_path, 'r') as f:
                workflow_content = f.read()
        except FileNotFoundError:
            console.print(f"[bold red]Error: Workflow file '{workflow_path}' not found[/bold red]")
            return {"valid": False, "error": "File not found"}
        except Exception as e:
            console.print(f"[bold red]Error reading workflow file: {e}[/bold red]")
            return {"valid": False, "error": str(e)}
        
        # Validate workflow
        validation_results = self.validator.validate_nextflow(workflow_content)
        
        # Add file information
        validation_results["file_path"] = workflow_path
        validation_results["file_size"] = len(workflow_content)
        validation_results["line_count"] = len(workflow_content.split('\n'))
        
        return validation_results
    
    def validate_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Validate all Nextflow workflows in a directory.
        
        Args:
            directory_path: Path to directory containing workflows
            
        Returns:
            Dictionary with validation results for all workflows
        """
        console.print(f"[bold blue]Validating Nextflow workflows in: {directory_path}[/bold blue]")
        
        directory = Path(directory_path)
        if not directory.exists():
            console.print(f"[bold red]Error: Directory '{directory_path}' not found[/bold red]")
            return {"valid": False, "error": "Directory not found"}
        
        # Find all .nf files
        nf_files = list(directory.glob("*.nf"))
        
        if not nf_files:
            console.print(f"[bold yellow]Warning: No .nf files found in '{directory_path}'[/bold yellow]")
            return {"valid": False, "error": "No .nf files found"}
        
        # Validate each workflow
        results = {
            "directory": directory_path,
            "total_workflows": len(nf_files),
            "valid_workflows": 0,
            "invalid_workflows": 0,
            "workflows": {},
            "summary": {}
        }
        
        for nf_file in nf_files:
            console.print(f"[blue]Validating: {nf_file.name}[/blue]")
            workflow_results = self.validate_workflow_file(str(nf_file))
            results["workflows"][nf_file.name] = workflow_results
            
            if workflow_results.get("valid", False):
                results["valid_workflows"] += 1
            else:
                results["invalid_workflows"] += 1
        
        # Calculate summary statistics
        if results["total_workflows"] > 0:
            results["summary"] = {
                "success_rate": results["valid_workflows"] / results["total_workflows"] * 100,
                "average_score": sum(
                    w.get("overall_score", 0) for w in results["workflows"].values()
                ) / results["total_workflows"]
            }
        
        return results
    
    def display_validation_results(self, results: Dict[str, Any]):
        """Display validation results in a formatted way."""
        
        if "workflows" in results:
            # Directory validation results
            self._display_directory_results(results)
        else:
            # Single workflow validation results
            self._display_workflow_results(results)
    
    def _display_workflow_results(self, results: Dict[str, Any]):
        """Display results for a single workflow."""
        
        # Overall status
        status = "✅ VALID" if results.get("valid", False) else "❌ INVALID"
        score = results.get("overall_score", 0)
        
        console.print(f"\n[bold]Validation Results[/bold]")
        console.print(f"Status: {status}")
        console.print(f"Overall Score: {score:.1f}/100")
        
        if "file_path" in results:
            console.print(f"File: {results['file_path']}")
            console.print(f"Size: {results['file_size']} bytes, {results['line_count']} lines")
        
        # Issues
        if results.get("issues"):
            console.print(f"\n[bold red]Issues ({len(results['issues'])}):[/bold red]")
            for issue in results["issues"]:
                console.print(f"  ❌ {issue}")
        
        # Warnings
        if results.get("warnings"):
            console.print(f"\n[bold yellow]Warnings ({len(results['warnings'])}):[/bold yellow]")
            for warning in results["warnings"]:
                console.print(f"  ⚠️  {warning}")
        
        # Recommendations
        if results.get("recommendations"):
            console.print(f"\n[bold blue]Recommendations ({len(results['recommendations'])}):[/bold blue]")
            for rec in results["recommendations"]:
                console.print(f"  💡 {rec}")
        
        # Detailed scores
        if results.get("scores"):
            table = Table(title="Detailed Validation Scores")
            table.add_column("Category", style="cyan")
            table.add_column("Score", style="green")
            
            for category, score in results["scores"].items():
                table.add_row(category.replace("_", " ").title(), f"{score:.1f}/100")
            
            console.print(f"\n{table}")
    
    def _display_directory_results(self, results: Dict[str, Any]):
        """Display results for directory validation."""
        
        console.print(f"\n[bold]Directory Validation Results[/bold]")
        console.print(f"Directory: {results['directory']}")
        console.print(f"Total Workflows: {results['total_workflows']}")
        console.print(f"Valid: {results['valid_workflows']}")
        console.print(f"Invalid: {results['invalid_workflows']}")
        
        if results.get("summary"):
            console.print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
            console.print(f"Average Score: {results['summary']['average_score']:.1f}/100")
        
        # Workflow summary table
        if results.get("workflows"):
            table = Table(title="Workflow Validation Summary")
            table.add_column("Workflow", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Score", style="yellow")
            table.add_column("Issues", style="red")
            table.add_column("Warnings", style="yellow")
            
            for workflow_name, workflow_results in results["workflows"].items():
                status = "✅" if workflow_results.get("valid", False) else "❌"
                score = f"{workflow_results.get('overall_score', 0):.1f}"
                issues = len(workflow_results.get("issues", []))
                warnings = len(workflow_results.get("warnings", []))
                
                table.add_row(workflow_name, status, score, str(issues), str(warnings))
            
            console.print(f"\n{table}")
    
    def save_validation_report(self, results: Dict[str, Any], output_file: str):
        """Save validation results to a file."""
        
        # Generate text report
        if "workflows" in results:
            report = self._generate_directory_report(results)
        else:
            report = self._generate_workflow_report(results)
        
        # Save to file
        with open(output_file, 'w') as f:
            f.write(report)
        
        console.print(f"[green]Validation report saved to: {output_file}[/green]")
    
    def _generate_workflow_report(self, results: Dict[str, Any]) -> str:
        """Generate text report for a single workflow."""
        return self.validator.generate_validation_report(results)
    
    def _generate_directory_report(self, results: Dict[str, Any]) -> str:
        """Generate text report for directory validation."""
        
        report_lines = [
            "Nextflow Workflow Directory Validation Report",
            "=" * 60,
            "",
            f"Directory: {results['directory']}",
            f"Total Workflows: {results['total_workflows']}",
            f"Valid Workflows: {results['valid_workflows']}",
            f"Invalid Workflows: {results['invalid_workflows']}",
            ""
        ]
        
        if results.get("summary"):
            report_lines.extend([
                f"Success Rate: {results['summary']['success_rate']:.1f}%",
                f"Average Score: {results['summary']['average_score']:.1f}/100",
                ""
            ])
        
        # Individual workflow reports
        for workflow_name, workflow_results in results.get("workflows", {}).items():
            report_lines.extend([
                f"Workflow: {workflow_name}",
                "-" * 40,
                self.validator.generate_validation_report(workflow_results),
                ""
            ])
        
        return "\n".join(report_lines)


@click.command()
@click.option('--workflow', '-w', help='Path to Nextflow workflow file')
@click.option('--directory', '-d', help='Path to directory containing workflows')
@click.option('--output', '-o', help='Output file for validation report')
@click.option('--format', 'output_format', default='text', 
              type=click.Choice(['text', 'json']), help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(workflow, directory, output, output_format, verbose):
    """Validate Nextflow workflows."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    validator = NextflowValidator()
    
    try:
        if workflow:
            # Validate single workflow
            results = validator.validate_workflow_file(workflow)
            validator.display_validation_results(results)
            
        elif directory:
            # Validate directory
            results = validator.validate_directory(directory)
            validator.display_validation_results(results)
            
        else:
            console.print("[bold red]Error: Please specify either --workflow or --directory[/bold red]")
            sys.exit(1)
        
        # Save report if requested
        if output:
            if output_format == 'json':
                with open(output, 'w') as f:
                    json.dump(results, f, indent=2)
                console.print(f"[green]JSON report saved to: {output}[/green]")
            else:
                validator.save_validation_report(results, output)
        
        # Exit with appropriate code
        if "workflows" in results:
            # Directory validation
            success = results.get("valid_workflows", 0) > 0
        else:
            # Single workflow validation
            success = results.get("valid", False)
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        console.print(f"[bold red]Validation failed: {e}[/bold red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()

