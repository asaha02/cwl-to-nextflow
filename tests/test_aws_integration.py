#!/usr/bin/env python3
"""
Tests for AWS HealthOmics Integration Module
"""

import unittest
import unittest.mock
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.aws_integration import AWSHealthOmicsIntegration


class TestAWSHealthOmicsIntegration(unittest.TestCase):
    """Test cases for AWS HealthOmics integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock boto3 clients to avoid actual AWS calls
        with unittest.mock.patch('boto3.client') as mock_client:
            self.aws_integration = AWSHealthOmicsIntegration()
        
        # Sample components for testing
        self.sample_components = {
            "workflow_info": {
                "name": "test_workflow",
                "version": "v1.2",
                "description": "A test workflow"
            },
            "processes": {
                "test_process": {
                    "name": "test_process",
                    "requirements": [],
                    "hints": []
                }
            }
        }
    
    @unittest.mock.patch('boto3.client')
    def test_init_with_mock(self, mock_client):
        """Test initialization with mocked boto3."""
        integration = AWSHealthOmicsIntegration()
        
        # Should not raise any exceptions
        self.assertIsNotNone(integration)
    
    def test_generate_healthomics_config(self):
        """Test generating HealthOmics configuration."""
        config = self.aws_integration._generate_healthomics_config(self.sample_components)
        
        # Check for AWS HealthOmics specific configuration
        self.assertIn("aws {", config)
        self.assertIn("healthomics", config)
        self.assertIn("batch", config)
        self.assertIn("AWS_DEFAULT_REGION", config)
        self.assertIn("AWS_HEALTHOMICS_WORKGROUP", config)
        self.assertIn("AWS_HEALTHOMICS_ROLE", config)
        self.assertIn("executor 'awsbatch'", config)
        self.assertIn("profiles", config)
    
    def test_generate_monitoring_code(self):
        """Test generating monitoring code."""
        monitoring_code = self.aws_integration._generate_monitoring_code()
        
        # Check for monitoring functions
        self.assertIn("healthomics_log", monitoring_code)
        self.assertIn("healthomics_metrics", monitoring_code)
        self.assertIn("healthomics_error_handler", monitoring_code)
        self.assertIn("CloudWatch", monitoring_code)
    
    def test_generate_error_handling(self):
        """Test generating error handling code."""
        error_handling = self.aws_integration._generate_error_handling()
        
        # Check for error handling elements
        self.assertIn("errorStrategy", error_handling)
        self.assertIn("maxRetries", error_handling)
        self.assertIn("onError", error_handling)
        self.assertIn("afterScript", error_handling)
    
    def test_combine_pipeline_components(self):
        """Test combining pipeline components."""
        base_pipeline = "// Base pipeline\nworkflow { }"
        config = "// Config\naws { }"
        monitoring = "// Monitoring\nfunction healthomics_log() { }"
        error_handling = "// Error handling\nprocess { }"
        
        combined = self.aws_integration._combine_pipeline_components(
            base_pipeline, config, monitoring, error_handling
        )
        
        # Check that all components are included
        self.assertIn("// Monitoring", combined)
        self.assertIn("// Base pipeline", combined)
        self.assertIn("// Config", combined)
        self.assertIn("// Error handling", combined)
        
        # Check order (monitoring first, then base, then config, then error handling)
        monitoring_pos = combined.find("// Monitoring")
        base_pos = combined.find("// Base pipeline")
        config_pos = combined.find("// Config")
        error_pos = combined.find("// Error handling")
        
        self.assertLess(monitoring_pos, base_pos)
        self.assertLess(base_pos, config_pos)
        self.assertLess(config_pos, error_pos)
    
    def test_extract_workflow_parameters(self):
        """Test extracting workflow parameters."""
        workflow_definition = """
workflow test_workflow {
    input:
    val input_file
    val threads = 4
    val output_dir = "results"
    
    output:
    val output_file
    
    script:
    '''
    echo "Processing"
    '''
}
"""
        
        parameters = self.aws_integration._extract_workflow_parameters(workflow_definition)
        
        # Should extract parameters from workflow definition
        self.assertIsInstance(parameters, list)
        # Note: This is a simplified test - in practice, parameter extraction would be more sophisticated
    
    def test_parse_image_name(self):
        """Test parsing Docker image names."""
        # Test full registry path
        registry, tag = self.aws_integration._parse_image_name("registry.com/namespace/image:tag")
        self.assertEqual(registry, "registry.com/namespace/image")
        self.assertEqual(tag, "tag")
        
        # Test namespace/image format
        registry, tag = self.aws_integration._parse_image_name("namespace/image:tag")
        self.assertEqual(registry, "namespace/image")
        self.assertEqual(tag, "tag")
        
        # Test simple image:tag format
        registry, tag = self.aws_integration._parse_image_name("image:tag")
        self.assertEqual(registry, "docker.io/image")
        self.assertEqual(tag, "tag")
        
        # Test image without tag
        registry, tag = self.aws_integration._parse_image_name("image")
        self.assertEqual(registry, "docker.io/image")
        self.assertEqual(tag, "latest")
    
    @unittest.mock.patch('boto3.client')
    def test_validate_healthomics_setup(self, mock_client):
        """Test validating HealthOmics setup."""
        # Mock successful responses
        mock_sts = unittest.mock.MagicMock()
        mock_omics = unittest.mock.MagicMock()
        mock_iam = unittest.mock.MagicMock()
        
        mock_sts.get_caller_identity.return_value = {"Account": "123456789012"}
        mock_omics.list_workgroups.return_value = {"workgroups": []}
        mock_iam.list_roles.return_value = {"Roles": []}
        
        mock_client.side_effect = lambda service, **kwargs: {
            'sts': mock_sts,
            'omics': mock_omics,
            'iam': mock_iam
        }[service]
        
        integration = AWSHealthOmicsIntegration()
        results = integration.validate_healthomics_setup()
        
        # Check validation results
        self.assertIn("credentials_valid", results)
        self.assertIn("workgroup_accessible", results)
        self.assertIn("role_accessible", results)
        self.assertIn("permissions_valid", results)
        self.assertIn("errors", results)
    
    @unittest.mock.patch('boto3.client')
    def test_setup_healthomics_environment(self, mock_client):
        """Test setting up HealthOmics environment."""
        # Mock successful responses
        mock_omics = unittest.mock.MagicMock()
        mock_iam = unittest.mock.MagicMock()
        
        # Mock workgroup already exists
        mock_omics.get_workgroup.return_value = {"workgroup": {"name": "default"}}
        
        # Mock role already exists
        mock_iam.get_role.return_value = {"Role": {"RoleName": "HealthOmicsExecutionRole"}}
        
        mock_client.side_effect = lambda service, **kwargs: {
            'omics': mock_omics,
            'iam': mock_iam
        }[service]
        
        integration = AWSHealthOmicsIntegration()
        results = integration.setup_healthomics_environment()
        
        # Check setup results
        self.assertIn("workgroup_created", results)
        self.assertIn("role_created", results)
        self.assertIn("bucket_created", results)
        self.assertIn("errors", results)
    
    def test_add_healthomics_features(self):
        """Test adding HealthOmics features to pipeline."""
        base_pipeline = "// Base pipeline\nworkflow { }"
        
        enhanced_pipeline = self.aws_integration.add_healthomics_features(
            base_pipeline, self.sample_components
        )
        
        # Check that HealthOmics features were added
        self.assertIn("healthomics_log", enhanced_pipeline)
        self.assertIn("aws {", enhanced_pipeline)
        self.assertIn("healthomics", enhanced_pipeline)
        self.assertIn("errorStrategy", enhanced_pipeline)
    
    def test_create_healthomics_workflow_mock(self):
        """Test creating HealthOmics workflow (mocked)."""
        workflow_name = "test_workflow"
        workflow_definition = "workflow test { }"
        description = "Test workflow"
        
        # Mock the client
        with unittest.mock.patch.object(self.aws_integration, 'healthomics_client') as mock_client:
            mock_client.create_workflow.return_value = {"id": "workflow-123"}
            
            workflow_id = self.aws_integration.create_healthomics_workflow(
                workflow_name, workflow_definition, description
            )
            
            self.assertEqual(workflow_id, "workflow-123")
            mock_client.create_workflow.assert_called_once()
    
    def test_create_healthomics_workflow_no_client(self):
        """Test creating HealthOmics workflow with no client."""
        # Set client to None
        self.aws_integration.healthomics_client = None
        
        workflow_id = self.aws_integration.create_healthomics_workflow(
            "test", "workflow { }", "test"
        )
        
        self.assertIsNone(workflow_id)
    
    def test_region_initialization(self):
        """Test initialization with custom region."""
        integration = AWSHealthOmicsIntegration(region="us-west-2")
        self.assertEqual(integration.region, "us-west-2")
    
    def test_empty_components(self):
        """Test with empty components."""
        empty_components = {
            "workflow_info": {"name": "empty", "version": "v1.0", "description": ""},
            "processes": {}
        }
        
        config = self.aws_integration._generate_healthomics_config(empty_components)
        
        # Should still generate valid configuration
        self.assertIn("aws {", config)
        self.assertIn("healthomics", config)
    
    def test_complex_workflow_definition(self):
        """Test with complex workflow definition."""
        complex_workflow = """
workflow complex_workflow {
    input:
    val input_file
    val threads = 4
    val output_dir = "results"
    val min_quality = 20
    val max_memory = "16GB"
    
    output:
    val output_file
    val log_file
    
    script:
    '''
    echo "Complex workflow"
    '''
}
"""
        
        parameters = self.aws_integration._extract_workflow_parameters(complex_workflow)
        
        # Should extract parameters (simplified test)
        self.assertIsInstance(parameters, list)


if __name__ == "__main__":
    unittest.main()

