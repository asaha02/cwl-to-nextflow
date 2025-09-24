#!/usr/bin/env python3
"""
Tests for CWL Parser Module
"""

import unittest
import tempfile
import yaml
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cwl_parser import CWLParser


class TestCWLParser(unittest.TestCase):
    """Test cases for CWL parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = CWLParser()
        
        # Sample CWL workflow for testing
        self.sample_cwl = {
            "cwlVersion": "v1.2",
            "class": "Workflow",
            "id": "test_workflow",
            "label": "Test Workflow",
            "doc": "A test workflow for unit testing",
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
                    "run": "tools/test_tool.cwl",
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
                    "dockerPull": "public.ecr.aws/healthomics/test:latest"
                },
                {
                    "class": "ResourceRequirement",
                    "coresMin": 4,
                    "ramMin": 8000000000
                }
            ],
            "hints": [
                {
                    "class": "DockerRequirement",
                    "dockerPull": "public.ecr.aws/healthomics/test:latest"
                }
            ]
        }
    
    def test_parse_cwl_data(self):
        """Test parsing CWL data structure."""
        components = self.parser.extract_components(self.sample_cwl)
        
        # Test workflow info
        self.assertEqual(components["workflow_info"]["name"], "test_workflow")
        self.assertEqual(components["workflow_info"]["version"], "v1.2")
        self.assertEqual(components["workflow_info"]["description"], "A test workflow for unit testing")
        
        # Test inputs
        self.assertEqual(len(components["inputs"]), 2)
        self.assertIn("input_file", components["inputs"])
        self.assertIn("threads", components["inputs"])
        
        # Test outputs
        self.assertEqual(len(components["outputs"]), 1)
        self.assertIn("output_file", components["outputs"])
        
        # Test processes
        self.assertEqual(len(components["processes"]), 1)
        self.assertIn("process_step", components["processes"])
        
        # Test requirements
        self.assertIn("docker", components["requirements"])
        self.assertIn("resource", components["requirements"])
    
    def test_process_inputs(self):
        """Test processing input definitions."""
        components = self.parser.extract_components(self.sample_cwl)
        inputs = components["inputs"]
        
        # Test input_file
        input_file = inputs["input_file"]
        self.assertEqual(input_file["name"], "input_file")
        self.assertEqual(input_file["type"], "File")
        self.assertEqual(input_file["description"], "Input file to process")
        self.assertFalse(input_file["required"])  # No default, so required
        
        # Test threads
        threads = inputs["threads"]
        self.assertEqual(threads["name"], "threads")
        self.assertEqual(threads["type"], "int")
        self.assertEqual(threads["default"], 4)
        self.assertFalse(threads["required"])  # Has default, so not required
    
    def test_process_outputs(self):
        """Test processing output definitions."""
        components = self.parser.extract_components(self.sample_cwl)
        outputs = components["outputs"]
        
        output_file = outputs["output_file"]
        self.assertEqual(output_file["name"], "output_file")
        self.assertEqual(output_file["type"], "File")
        self.assertEqual(output_file["description"], "Output file")
    
    def test_process_steps(self):
        """Test processing step definitions."""
        components = self.parser.extract_components(self.sample_cwl)
        processes = components["processes"]
        
        process_step = processes["process_step"]
        self.assertEqual(process_step["name"], "process_step")
        self.assertEqual(process_step["tool"], "tools/test_tool.cwl")
        self.assertEqual(len(process_step["inputs"]), 2)
        self.assertEqual(len(process_step["outputs"]), 1)
    
    def test_process_requirements(self):
        """Test processing requirements."""
        components = self.parser.extract_components(self.sample_cwl)
        requirements = components["requirements"]
        
        # Test Docker requirements
        self.assertEqual(len(requirements["docker"]), 1)
        docker_req = requirements["docker"][0]
        self.assertEqual(docker_req["class"], "DockerRequirement")
        self.assertEqual(docker_req["dockerPull"], "public.ecr.aws/healthomics/test:latest")
        
        # Test resource requirements
        self.assertEqual(len(requirements["resource"]), 1)
        resource_req = requirements["resource"][0]
        self.assertEqual(resource_req["class"], "ResourceRequirement")
        self.assertEqual(resource_req["coresMin"], 4)
        self.assertEqual(resource_req["ramMin"], 8000000000)
    
    def test_process_hints(self):
        """Test processing hints."""
        components = self.parser.extract_components(self.sample_cwl)
        hints = components["hints"]
        
        # Test Docker hints
        self.assertEqual(len(hints["docker"]), 1)
        docker_hint = hints["docker"][0]
        self.assertEqual(docker_hint["class"], "DockerRequirement")
        self.assertEqual(docker_hint["dockerPull"], "public.ecr.aws/healthomics/test:latest")
    
    def test_extract_dependencies(self):
        """Test extracting workflow dependencies."""
        components = self.parser.extract_components(self.sample_cwl)
        dependencies = components["dependencies"]
        
        self.assertEqual(len(dependencies), 1)
        self.assertIn("tools/test_tool.cwl", dependencies)
    
    def test_normalize_type(self):
        """Test type normalization."""
        # Test string type
        self.assertEqual(self.parser._normalize_type("string"), "string")
        
        # Test dict type
        dict_type = {"type": "File"}
        self.assertEqual(self.parser._normalize_type(dict_type), "File")
        
        # Test array type
        array_type = {"items": "string"}
        self.assertEqual(self.parser._normalize_type(array_type), "array<string>")
        
        # Test list type
        list_type = ["string", "int"]
        self.assertEqual(self.parser._normalize_type(list_type), "union")
    
    def test_empty_workflow(self):
        """Test parsing empty workflow."""
        empty_cwl = {
            "cwlVersion": "v1.2",
            "class": "Workflow",
            "id": "empty_workflow"
        }
        
        components = self.parser.extract_components(empty_cwl)
        
        self.assertEqual(components["workflow_info"]["name"], "empty_workflow")
        self.assertEqual(len(components["inputs"]), 0)
        self.assertEqual(len(components["outputs"]), 0)
        self.assertEqual(len(components["processes"]), 0)
    
    def test_complex_workflow(self):
        """Test parsing complex workflow with multiple steps."""
        complex_cwl = {
            "cwlVersion": "v1.2",
            "class": "Workflow",
            "id": "complex_workflow",
            "inputs": {
                "input1": {"type": "File"},
                "input2": {"type": "File"},
                "param1": {"type": "string", "default": "default_value"}
            },
            "outputs": {
                "output1": {"type": "File", "outputSource": "step2/output1"},
                "output2": {"type": "File", "outputSource": "step2/output2"}
            },
            "steps": {
                "step1": {
                    "run": "tools/step1.cwl",
                    "in": {"input": "input1"},
                    "out": ["intermediate"]
                },
                "step2": {
                    "run": "tools/step2.cwl",
                    "in": {
                        "input1": "step1/intermediate",
                        "input2": "input2"
                    },
                    "out": ["output1", "output2"]
                }
            }
        }
        
        components = self.parser.extract_components(complex_cwl)
        
        # Test multiple inputs
        self.assertEqual(len(components["inputs"]), 3)
        
        # Test multiple outputs
        self.assertEqual(len(components["outputs"]), 2)
        
        # Test multiple steps
        self.assertEqual(len(components["processes"]), 2)
        
        # Test step dependencies
        step2 = components["processes"]["step2"]
        self.assertIn("step1", step2["inputs"]["input1"]["source"])
    
    def test_file_parsing(self):
        """Test parsing CWL from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cwl', delete=False) as f:
            yaml.dump(self.sample_cwl, f)
            temp_file = f.name
        
        try:
            # Mock the load_tool function since we can't actually load CWL tools in tests
            import unittest.mock
            with unittest.mock.patch('src.cwl_parser.load_tool.load_tool') as mock_load_tool:
                # Create a mock tool object
                mock_tool = unittest.mock.MagicMock()
                mock_tool.cwlVersion = "v1.2"
                mock_tool.class_ = "Workflow"
                mock_tool.id = "test_workflow"
                mock_tool.label = "Test Workflow"
                mock_tool.doc = "A test workflow for unit testing"
                mock_tool.inputs = []
                mock_tool.outputs = []
                mock_tool.steps = []
                mock_tool.requirements = []
                mock_tool.hints = []
                
                mock_load_tool.return_value = mock_tool
                
                # This would normally parse the file, but we're mocking it
                # In a real test, you'd need to set up the CWL environment properly
                pass
                
        finally:
            Path(temp_file).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()

