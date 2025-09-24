#!/usr/bin/env python3
"""
Tests for Nextflow Generator Module
"""

import unittest
import tempfile
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.nextflow_generator import NextflowGenerator


class TestNextflowGenerator(unittest.TestCase):
    """Test cases for Nextflow generator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = NextflowGenerator()
        
        # Sample components for testing
        self.sample_components = {
            "workflow_info": {
                "name": "test_workflow",
                "version": "v1.2",
                "description": "A test workflow",
                "label": "Test Workflow"
            },
            "inputs": {
                "input_file": {
                    "name": "input_file",
                    "type": "File",
                    "description": "Input file to process",
                    "default": None,
                    "required": True
                },
                "threads": {
                    "name": "threads",
                    "type": "int",
                    "description": "Number of threads",
                    "default": 4,
                    "required": False
                }
            },
            "outputs": {
                "output_file": {
                    "name": "output_file",
                    "type": "File",
                    "description": "Output file"
                }
            },
            "processes": {
                "process_step": {
                    "name": "process_step",
                    "tool": "tools/test_tool.cwl",
                    "inputs": {
                        "input": {
                            "name": "input",
                            "source": "input_file"
                        },
                        "threads": {
                            "name": "threads",
                            "source": "threads"
                        }
                    },
                    "outputs": ["output"],
                    "requirements": [],
                    "hints": []
                }
            },
            "requirements": {
                "docker": [
                    {
                        "class": "DockerRequirement",
                        "dockerPull": "public.ecr.aws/healthomics/test:latest"
                    }
                ],
                "resource": [
                    {
                        "class": "ResourceRequirement",
                        "coresMin": 4,
                        "ramMin": 8000000000
                    }
                ],
                "software": [],
                "other": []
            },
            "hints": {
                "docker": [],
                "resource": [],
                "other": []
            },
            "dependencies": ["tools/test_tool.cwl"]
        }
        
        self.sample_resource_mapping = {
            "process_step": {
                "cpus": 4,
                "memory": "8 GB",
                "time": "2h",
                "instance_type": "t3.large"
            }
        }
        
        self.sample_container_specs = {
            "process_step": {
                "image": "public.ecr.aws/healthomics/test:latest",
                "registry": "public.ecr.aws/healthomics",
                "tag": "latest",
                "type": "docker",
                "aws_optimized": True
            }
        }
    
    def test_generate_pipeline_basic(self):
        """Test basic pipeline generation."""
        pipeline = self.generator.generate_pipeline(
            self.sample_components,
            self.sample_resource_mapping,
            self.sample_container_specs,
            aws_healthomics=False
        )
        
        # Check that pipeline contains expected elements
        self.assertIn("test_workflow", pipeline)
        self.assertIn("params.input_file", pipeline)
        self.assertIn("params.threads", pipeline)
        self.assertIn("process process_step", pipeline)
        self.assertIn("workflow", pipeline)
    
    def test_generate_pipeline_aws_healthomics(self):
        """Test AWS HealthOmics pipeline generation."""
        pipeline = self.generator.generate_pipeline(
            self.sample_components,
            self.sample_resource_mapping,
            self.sample_container_specs,
            aws_healthomics=True
        )
        
        # Check for AWS HealthOmics specific elements
        self.assertIn("aws {", pipeline)
        self.assertIn("healthomics", pipeline)
        self.assertIn("awsbatch", pipeline)
        self.assertIn("AWS_DEFAULT_REGION", pipeline)
        self.assertIn("AWS_HEALTHOMICS_WORKGROUP", pipeline)
    
    def test_process_inputs_for_nextflow(self):
        """Test processing inputs for Nextflow."""
        nextflow_inputs = self.generator._process_inputs_for_nextflow(self.sample_components["inputs"])
        
        self.assertEqual(len(nextflow_inputs), 2)
        
        # Test input_file
        input_file = nextflow_inputs[0]
        self.assertEqual(input_file["name"], "input_file")
        self.assertEqual(input_file["type"], "file")
        self.assertEqual(input_file["description"], "Input file to process")
        self.assertTrue(input_file["required"])
        
        # Test threads
        threads = nextflow_inputs[1]
        self.assertEqual(threads["name"], "threads")
        self.assertEqual(threads["type"], "integer")
        self.assertEqual(threads["default"], 4)
        self.assertFalse(threads["required"])
    
    def test_process_outputs_for_nextflow(self):
        """Test processing outputs for Nextflow."""
        nextflow_outputs = self.generator._process_outputs_for_nextflow(self.sample_components["outputs"])
        
        self.assertEqual(len(nextflow_outputs), 1)
        
        output_file = nextflow_outputs[0]
        self.assertEqual(output_file["name"], "output_file")
        self.assertEqual(output_file["type"], "file")
        self.assertEqual(output_file["description"], "Output file")
    
    def test_process_steps_for_nextflow(self):
        """Test processing steps for Nextflow."""
        nextflow_processes = self.generator._process_steps_for_nextflow(
            self.sample_components["processes"],
            self.sample_resource_mapping,
            self.sample_container_specs
        )
        
        self.assertEqual(len(nextflow_processes), 1)
        
        process = nextflow_processes[0]
        self.assertEqual(process["name"], "process_step")
        self.assertEqual(process["container"], "public.ecr.aws/healthomics/test:latest")
        self.assertEqual(process["resources"]["cpus"], 4)
        self.assertEqual(process["resources"]["memory"], "8 GB")
    
    def test_generate_workflow_logic(self):
        """Test generating workflow logic."""
        workflow_logic = self.generator._generate_workflow_logic(self.sample_components["processes"])
        
        self.assertEqual(len(workflow_logic), 1)
        
        step = workflow_logic[0]
        self.assertEqual(step["name"], "process_step")
        self.assertEqual(len(step["inputs"]), 2)
        self.assertEqual(len(step["outputs"]), 1)
        self.assertEqual(len(step["dependencies"]), 0)
    
    def test_map_cwl_type_to_nextflow(self):
        """Test mapping CWL types to Nextflow types."""
        # Test basic types
        self.assertEqual(self.generator._map_cwl_type_to_nextflow("string"), "string")
        self.assertEqual(self.generator._map_cwl_type_to_nextflow("int"), "integer")
        self.assertEqual(self.generator._map_cwl_type_to_nextflow("float"), "float")
        self.assertEqual(self.generator._map_cwl_type_to_nextflow("boolean"), "boolean")
        self.assertEqual(self.generator._map_cwl_type_to_nextflow("File"), "file")
        self.assertEqual(self.generator._map_cwl_type_to_nextflow("Directory"), "directory")
        
        # Test complex types
        self.assertEqual(self.generator._map_cwl_type_to_nextflow("array"), "array")
        self.assertEqual(self.generator._map_cwl_type_to_nextflow("record"), "object")
        
        # Test array types
        self.assertEqual(self.generator._map_cwl_type_to_nextflow("array<string>"), "array")
        self.assertEqual(self.generator._map_cwl_type_to_nextflow("array<File>"), "array")
    
    def test_generate_config_file(self):
        """Test generating configuration file."""
        config = self.generator.generate_config_file(
            self.sample_components,
            self.sample_resource_mapping,
            aws_healthomics=True
        )
        
        # Check for configuration elements
        self.assertIn("process", config)
        self.assertIn("executor", config)
        self.assertIn("aws", config)
        self.assertIn("healthomics", config)
    
    def test_generate_dockerfile(self):
        """Test generating Dockerfile."""
        dockerfile = self.generator.generate_dockerfile(self.sample_container_specs)
        
        # Check for Dockerfile elements
        self.assertIn("FROM", dockerfile)
        self.assertIn("RUN", dockerfile)
        self.assertIn("WORKDIR", dockerfile)
        self.assertIn("COPY", dockerfile)
    
    def test_custom_template(self):
        """Test using custom template."""
        # Create a custom template
        custom_template = '''
// Custom template for {{ workflow_info.name }}
params.custom_param = "default_value"

process custom_process {
    container '{{ processes[0].container }}'
    
    input:
    val input_data
    
    output:
    val output_data
    
    script:
    """
    echo "Custom process"
    """
}

workflow {
    custom_process()
}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.nf', delete=False) as f:
            f.write(custom_template)
            temp_file = f.name
        
        try:
            pipeline = self.generator.generate_pipeline(
                self.sample_components,
                self.sample_resource_mapping,
                self.sample_container_specs,
                aws_healthomics=False,
                custom_template=temp_file
            )
            
            # Check that custom template was used
            self.assertIn("Custom template", pipeline)
            self.assertIn("custom_process", pipeline)
            self.assertIn("params.custom_param", pipeline)
            
        finally:
            Path(temp_file).unlink(missing_ok=True)
    
    def test_empty_components(self):
        """Test generating pipeline with empty components."""
        empty_components = {
            "workflow_info": {"name": "empty_workflow", "version": "v1.0", "description": ""},
            "inputs": {},
            "outputs": {},
            "processes": {},
            "requirements": {"docker": [], "resource": [], "software": [], "other": []},
            "hints": {"docker": [], "resource": [], "other": []},
            "dependencies": []
        }
        
        pipeline = self.generator.generate_pipeline(
            empty_components,
            {},
            {},
            aws_healthomics=False
        )
        
        # Should still generate a valid pipeline
        self.assertIn("empty_workflow", pipeline)
        self.assertIn("workflow", pipeline)
    
    def test_complex_workflow(self):
        """Test generating pipeline for complex workflow."""
        complex_components = {
            "workflow_info": {"name": "complex_workflow", "version": "v1.2", "description": "Complex workflow"},
            "inputs": {
                "input1": {"name": "input1", "type": "File", "description": "Input 1", "required": True},
                "input2": {"name": "input2", "type": "File", "description": "Input 2", "required": True},
                "param1": {"name": "param1", "type": "string", "description": "Parameter 1", "default": "default", "required": False}
            },
            "outputs": {
                "output1": {"name": "output1", "type": "File", "description": "Output 1"},
                "output2": {"name": "output2", "type": "File", "description": "Output 2"}
            },
            "processes": {
                "step1": {
                    "name": "step1",
                    "tool": "tools/step1.cwl",
                    "inputs": {"input": {"name": "input", "source": "input1"}},
                    "outputs": ["intermediate"],
                    "requirements": [],
                    "hints": []
                },
                "step2": {
                    "name": "step2",
                    "tool": "tools/step2.cwl",
                    "inputs": {
                        "input1": {"name": "input1", "source": "step1/intermediate"},
                        "input2": {"name": "input2", "source": "input2"}
                    },
                    "outputs": ["output1", "output2"],
                    "requirements": [],
                    "hints": []
                }
            },
            "requirements": {"docker": [], "resource": [], "software": [], "other": []},
            "hints": {"docker": [], "resource": [], "other": []},
            "dependencies": ["tools/step1.cwl", "tools/step2.cwl"]
        }
        
        complex_resource_mapping = {
            "step1": {"cpus": 2, "memory": "4 GB", "time": "1h"},
            "step2": {"cpus": 4, "memory": "8 GB", "time": "2h"}
        }
        
        complex_container_specs = {
            "step1": {"image": "public.ecr.aws/healthomics/step1:latest", "aws_optimized": True},
            "step2": {"image": "public.ecr.aws/healthomics/step2:latest", "aws_optimized": True}
        }
        
        pipeline = self.generator.generate_pipeline(
            complex_components,
            complex_resource_mapping,
            complex_container_specs,
            aws_healthomics=True
        )
        
        # Check for multiple processes
        self.assertIn("process step1", pipeline)
        self.assertIn("process step2", pipeline)
        
        # Check for multiple inputs
        self.assertIn("params.input1", pipeline)
        self.assertIn("params.input2", pipeline)
        self.assertIn("params.param1", pipeline)
        
        # Check for workflow logic
        self.assertIn("step1", pipeline)
        self.assertIn("step2", pipeline)


if __name__ == "__main__":
    unittest.main()

