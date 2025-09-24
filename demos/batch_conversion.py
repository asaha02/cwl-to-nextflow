#!/usr/bin/env python3
"""
Batch CWL to Nextflow Conversion Demo

This script demonstrates batch conversion of multiple CWL workflows.
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import Dict, List, Any
import concurrent.futures
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cwl_parser import CWLParser
from nextflow_generator import NextflowGenerator
from resource_mapper import ResourceMapper
from container_handler import ContainerHandler
from validation import WorkflowValidator

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BatchConverter:
    """Handles batch conversion of CWL workflows."""
    
    def __init__(self, max_workers: int = 4):
        """Initialize batch converter."""
        self.max_workers = max_workers
        self.cwl_parser = CWLParser()
        self.nextflow_generator = NextflowGenerator()
        self.resource_mapper = ResourceMapper()
        self.container_handler = ContainerHandler()
        self.validator = WorkflowValidator()
        
        self.conversion_results = []
        self.errors = []
    
    def convert_workflow(self, cwl_path: str, output_dir: str, aws_healthomics: bool = True) -> Dict[str, Any]:
        """Convert a single CWL workflow."""
        
        workflow_name = Path(cwl_path).stem
        start_time = datetime.now()
        
        try:
            logger.info(f"Converting workflow: {workflow_name}")
            
            # Parse CWL workflow
            cwl_data = self.cwl_parser.parse_cwl_file(cwl_path)
            components = self.cwl_parser.extract_components(cwl_data)
            
            # Map resources
            resource_mapping = self.resource_mapper.optimize_for_aws(components)
            
            # Process containers
            container_specs = self.container_handler.process_containers(components)
            
            # Generate Nextflow pipeline
            nextflow_pipeline = self.nextflow_generator.generate_pipeline(
                components, resource_mapping, container_specs, aws_healthomics=aws_healthomics
            )
            
            # Validate workflow
            validation_results = self.validator.validate_nextflow(nextflow_pipeline)
            
            # Save output
            output_path = Path(output_dir) / workflow_name
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save Nextflow pipeline
            nextflow_file = output_path / f"{workflow_name}.nf"
            with open(nextflow_file, 'w') as f:
                f.write(nextflow_pipeline)
            
            # Save configuration
            config_file = output_path / f"{workflow_name}_config.nf"
            config_content = self.nextflow_generator.generate_config_file(
                components, resource_mapping, aws_healthomics=aws_healthomics
            )
            with open(config_file, 'w') as f:
                f.write(config_content)
            
            # Save validation report
            report_file = output_path / f"{workflow_name}_validation.txt"
            report_content = self.validator.generate_validation_report(validation_results)
            with open(report_file, 'w') as f:
                f.write(report_content)
            
            # Save metadata
            metadata_file = output_path / f"{workflow_name}_metadata.json"
            metadata = {
                "original_cwl": cwl_path,
                "conversion_timestamp": datetime.now().isoformat(),
                "nextflow_version": "23.10.0",
                "aws_healthomics_enabled": aws_healthomics,
                "validation_results": validation_results,
                "workflow_info": components["workflow_info"],
                "resource_mapping": resource_mapping,
                "container_specs": container_specs
            }
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                "workflow_name": workflow_name,
                "input_file": cwl_path,
                "output_directory": str(output_path),
                "conversion_successful": validation_results.get("valid", False),
                "validation_score": validation_results.get("overall_score", 0),
                "duration_seconds": duration,
                "output_files": {
                    "nextflow_pipeline": str(nextflow_file),
                    "config_file": str(config_file),
                    "validation_report": str(report_file),
                    "metadata": str(metadata_file)
                },
                "workflow_stats": {
                    "processes": len(components.get("processes", {})),
                    "inputs": len(components.get("inputs", {})),
                    "outputs": len(components.get("outputs", {})),
                    "requirements": len(components.get("requirements", {}).get("docker", []))
                }
            }
            
            logger.info(f"Successfully converted {workflow_name} in {duration:.2f}s")
            return result
            
        except Exception as e:
            error_msg = f"Failed to convert {workflow_name}: {str(e)}"
            logger.error(error_msg)
            
            return {
                "workflow_name": workflow_name,
                "input_file": cwl_path,
                "conversion_successful": False,
                "error": str(e),
                "duration_seconds": (datetime.now() - start_time).total_seconds()
            }
    
    def convert_batch(self, cwl_files: List[str], output_dir: str, aws_healthomics: bool = True) -> Dict[str, Any]:
        """Convert multiple CWL workflows in parallel."""
        
        logger.info(f"Starting batch conversion of {len(cwl_files)} workflows")
        logger.info(f"Using {self.max_workers} parallel workers")
        
        start_time = datetime.now()
        
        # Convert workflows in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all conversion tasks
            future_to_workflow = {
                executor.submit(self.convert_workflow, cwl_file, output_dir, aws_healthomics): cwl_file
                for cwl_file in cwl_files
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_workflow):
                cwl_file = future_to_workflow[future]
                try:
                    result = future.result()
                    self.conversion_results.append(result)
                except Exception as e:
                    error_result = {
                        "workflow_name": Path(cwl_file).stem,
                        "input_file": cwl_file,
                        "conversion_successful": False,
                        "error": str(e)
                    }
                    self.conversion_results.append(error_result)
                    self.errors.append(str(e))
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # Generate batch summary
        successful_conversions = [r for r in self.conversion_results if r.get("conversion_successful", False)]
        failed_conversions = [r for r in self.conversion_results if not r.get("conversion_successful", False)]
        
        batch_summary = {
            "total_workflows": len(cwl_files),
            "successful_conversions": len(successful_conversions),
            "failed_conversions": len(failed_conversions),
            "success_rate": len(successful_conversions) / len(cwl_files) * 100 if cwl_files else 0,
            "total_duration_seconds": total_duration,
            "average_duration_seconds": sum(r.get("duration_seconds", 0) for r in self.conversion_results) / len(self.conversion_results) if self.conversion_results else 0,
            "aws_healthomics_enabled": aws_healthomics,
            "conversion_timestamp": start_time.isoformat(),
            "results": self.conversion_results
        }
        
        logger.info(f"Batch conversion completed in {total_duration:.2f}s")
        logger.info(f"Success rate: {batch_summary['success_rate']:.1f}%")
        
        return batch_summary
    
    def generate_batch_report(self, batch_summary: Dict[str, Any]) -> str:
        """Generate a comprehensive batch conversion report."""
        
        report_lines = [
            "CWL to Nextflow Batch Conversion Report",
            "=" * 60,
            "",
            f"Conversion Date: {batch_summary['conversion_timestamp']}",
            f"Total Workflows: {batch_summary['total_workflows']}",
            f"Successful Conversions: {batch_summary['successful_conversions']}",
            f"Failed Conversions: {batch_summary['failed_conversions']}",
            f"Success Rate: {batch_summary['success_rate']:.1f}%",
            f"Total Duration: {batch_summary['total_duration_seconds']:.2f} seconds",
            f"Average Duration: {batch_summary['average_duration_seconds']:.2f} seconds",
            f"AWS HealthOmics Enabled: {batch_summary['aws_healthomics_enabled']}",
            ""
        ]
        
        # Successful conversions
        if batch_summary['successful_conversions'] > 0:
            report_lines.extend([
                "Successful Conversions:",
                "-" * 30
            ])
            
            for result in batch_summary['results']:
                if result.get("conversion_successful", False):
                    report_lines.extend([
                        f"  Workflow: {result['workflow_name']}",
                        f"    Input: {result['input_file']}",
                        f"    Output: {result['output_directory']}",
                        f"    Validation Score: {result.get('validation_score', 0):.1f}/100",
                        f"    Duration: {result.get('duration_seconds', 0):.2f}s",
                        f"    Processes: {result.get('workflow_stats', {}).get('processes', 'N/A')}",
                        f"    Inputs: {result.get('workflow_stats', {}).get('inputs', 'N/A')}",
                        f"    Outputs: {result.get('workflow_stats', {}).get('outputs', 'N/A')}",
                        ""
                    ])
        
        # Failed conversions
        if batch_summary['failed_conversions'] > 0:
            report_lines.extend([
                "Failed Conversions:",
                "-" * 30
            ])
            
            for result in batch_summary['results']:
                if not result.get("conversion_successful", False):
                    report_lines.extend([
                        f"  Workflow: {result['workflow_name']}",
                        f"    Input: {result['input_file']}",
                        f"    Error: {result.get('error', 'Unknown error')}",
                        ""
                    ])
        
        # Summary statistics
        if batch_summary['successful_conversions'] > 0:
            successful_results = [r for r in batch_summary['results'] if r.get("conversion_successful", False)]
            
            report_lines.extend([
                "Summary Statistics:",
                "-" * 30,
                f"Average Validation Score: {sum(r.get('validation_score', 0) for r in successful_results) / len(successful_results):.1f}/100",
                f"Total Processes: {sum(r.get('workflow_stats', {}).get('processes', 0) for r in successful_results)}",
                f"Total Inputs: {sum(r.get('workflow_stats', {}).get('inputs', 0) for r in successful_results)}",
                f"Total Outputs: {sum(r.get('workflow_stats', {}).get('outputs', 0) for r in successful_results)}",
                ""
            ])
        
        # Recommendations
        report_lines.extend([
            "Recommendations:",
            "-" * 30
        ])
        
        if batch_summary['failed_conversions'] > 0:
            report_lines.append("  - Review failed conversions and fix CWL syntax issues")
        
        if batch_summary['success_rate'] < 100:
            report_lines.append("  - Consider running individual conversions to debug issues")
        
        if batch_summary['average_duration_seconds'] > 30:
            report_lines.append("  - Consider optimizing CWL workflows for faster conversion")
        
        report_lines.extend([
            "  - Test converted workflows with Nextflow before deployment",
            "  - Review validation reports for quality improvements",
            "  - Consider AWS HealthOmics optimization for production use"
        ])
        
        return "\n".join(report_lines)


def demo_batch_conversion():
    """Demonstrate batch conversion functionality."""
    
    print("=" * 60)
    print("Batch CWL to Nextflow Conversion Demo")
    print("=" * 60)
    
    # Create example CWL workflows for demo
    demo_workflows = create_demo_workflows()
    
    # Initialize batch converter
    converter = BatchConverter(max_workers=2)
    
    print(f"\n1. Created {len(demo_workflows)} demo CWL workflows")
    
    # Convert workflows
    output_dir = "batch_demo_output"
    batch_summary = converter.convert_batch(demo_workflows, output_dir, aws_healthomics=True)
    
    print(f"\n2. Batch conversion completed:")
    print(f"   Total workflows: {batch_summary['total_workflows']}")
    print(f"   Successful: {batch_summary['successful_conversions']}")
    print(f"   Failed: {batch_summary['failed_conversions']}")
    print(f"   Success rate: {batch_summary['success_rate']:.1f}%")
    print(f"   Total duration: {batch_summary['total_duration_seconds']:.2f}s")
    
    # Generate and save report
    report = converter.generate_batch_report(batch_summary)
    report_file = Path(output_dir) / "batch_conversion_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n3. Generated batch report: {report_file}")
    
    # Save JSON summary
    json_file = Path(output_dir) / "batch_summary.json"
    with open(json_file, 'w') as f:
        json.dump(batch_summary, f, indent=2)
    
    print(f"   Generated JSON summary: {json_file}")
    
    # Display individual results
    print(f"\n4. Individual conversion results:")
    for result in batch_summary['results']:
        status = "✓" if result.get("conversion_successful", False) else "❌"
        score = result.get("validation_score", 0)
        duration = result.get("duration_seconds", 0)
        print(f"   {status} {result['workflow_name']}: {score:.1f}/100 score, {duration:.2f}s")
    
    return batch_summary


def create_demo_workflows() -> List[str]:
    """Create demo CWL workflows for batch conversion."""
    
    demo_dir = Path("demo_workflows")
    demo_dir.mkdir(exist_ok=True)
    
    # Simple workflow
    simple_workflow = {
        "cwlVersion": "v1.2",
        "class": "Workflow",
        "id": "simple_workflow",
        "inputs": {
            "input_file": {"type": "File"}
        },
        "outputs": {
            "output_file": {"type": "File", "outputSource": "process/output"}
        },
        "steps": {
            "process": {
                "run": "tools/simple_tool.cwl",
                "in": {"input": "input_file"},
                "out": ["output"]
            }
        },
        "requirements": [
            {"class": "DockerRequirement", "dockerPull": "public.ecr.aws/healthomics/simple:latest"}
        ]
    }
    
    # Complex workflow
    complex_workflow = {
        "cwlVersion": "v1.2",
        "class": "Workflow",
        "id": "complex_workflow",
        "inputs": {
            "input1": {"type": "File"},
            "input2": {"type": "File"},
            "threads": {"type": "int", "default": 4}
        },
        "outputs": {
            "output1": {"type": "File", "outputSource": "step2/output1"},
            "output2": {"type": "File", "outputSource": "step2/output2"}
        },
        "steps": {
            "step1": {
                "run": "tools/step1_tool.cwl",
                "in": {"input": "input1", "threads": "threads"},
                "out": ["intermediate"]
            },
            "step2": {
                "run": "tools/step2_tool.cwl",
                "in": {"input1": "step1/intermediate", "input2": "input2"},
                "out": ["output1", "output2"]
            }
        },
        "requirements": [
            {"class": "DockerRequirement", "dockerPull": "public.ecr.aws/healthomics/complex:latest"},
            {"class": "ResourceRequirement", "coresMin": 4, "ramMin": 8000000000}
        ]
    }
    
    # Workflow with errors (for demo)
    error_workflow = {
        "cwlVersion": "v1.2",
        "class": "Workflow",
        "id": "error_workflow",
        "inputs": {
            "input_file": {"type": "File"}
        },
        "outputs": {
            "output_file": {"type": "File", "outputSource": "nonexistent_step/output"}
        },
        "steps": {
            "process": {
                "run": "tools/nonexistent_tool.cwl",
                "in": {"input": "input_file"},
                "out": ["output"]
            }
        }
    }
    
    workflows = [
        ("simple_workflow.cwl", simple_workflow),
        ("complex_workflow.cwl", complex_workflow),
        ("error_workflow.cwl", error_workflow)
    ]
    
    workflow_files = []
    for filename, workflow_data in workflows:
        workflow_file = demo_dir / filename
        with open(workflow_file, 'w') as f:
            import yaml
            yaml.dump(workflow_data, f, default_flow_style=False)
        workflow_files.append(str(workflow_file))
    
    return workflow_files


def main():
    """Main demo function."""
    
    print("Batch CWL to Nextflow Conversion Demo")
    print("This demo shows batch conversion of multiple CWL workflows.")
    
    try:
        # Run batch conversion demo
        batch_summary = demo_batch_conversion()
        
        print("\n" + "=" * 60)
        print("Batch conversion demo completed!")
        print("=" * 60)
        
        if batch_summary['success_rate'] > 0:
            print(f"\nSuccessfully converted {batch_summary['successful_conversions']} workflows")
            print("Generated files:")
            print("  - batch_demo_output/batch_conversion_report.txt")
            print("  - batch_demo_output/batch_summary.json")
            print("  - Individual workflow outputs in subdirectories")
        
        if batch_summary['failed_conversions'] > 0:
            print(f"\n{batch_summary['failed_conversions']} workflows failed conversion")
            print("Check the batch report for details on failures")
        
        print("\nTo run your own batch conversion:")
        print("  python batch_converter.py --input-dir ./cwl_workflows/ --output-dir ./nextflow_workflows/")
        
    except Exception as e:
        print(f"\nDemo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

