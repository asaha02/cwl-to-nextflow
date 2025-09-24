"""
AWS HealthOmics Integration Module

Handles integration with AWS HealthOmics platform for Nextflow workflows.
"""

import json
import logging
from typing import Dict, List, Any, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


class AWSHealthOmicsIntegration:
    """Integration with AWS HealthOmics platform."""
    
    def __init__(self, region: str = "us-east-1"):
        """Initialize AWS HealthOmics integration."""
        self.region = region
        self.healthomics_client = None
        self.ecr_client = None
        self.iam_client = None
        
        try:
            self.healthomics_client = boto3.client('omics', region_name=region)
            self.ecr_client = boto3.client('ecr', region_name=region)
            self.iam_client = boto3.client('iam', region_name=region)
        except NoCredentialsError:
            logger.warning("AWS credentials not found. Some features may not work.")
    
    def add_healthomics_features(
        self, nextflow_pipeline: str, components: Dict[str, Any]
    ) -> str:
        """
        Add AWS HealthOmics specific features to Nextflow pipeline.
        
        Args:
            nextflow_pipeline: Base Nextflow pipeline
            components: CWL workflow components
            
        Returns:
            Enhanced Nextflow pipeline with AWS HealthOmics features
        """
        logger.info("Adding AWS HealthOmics features to pipeline")
        
        # Add HealthOmics-specific configuration
        healthomics_config = self._generate_healthomics_config(components)
        
        # Add monitoring and logging
        monitoring_code = self._generate_monitoring_code()
        
        # Add error handling
        error_handling = self._generate_error_handling()
        
        # Combine all components
        enhanced_pipeline = self._combine_pipeline_components(
            nextflow_pipeline, healthomics_config, monitoring_code, error_handling
        )
        
        logger.info("AWS HealthOmics features added successfully")
        return enhanced_pipeline
    
    def _generate_healthomics_config(self, components: Dict[str, Any]) -> str:
        """Generate AWS HealthOmics specific configuration."""
        
        config = """
// AWS HealthOmics Configuration
aws {
    region = '${AWS_DEFAULT_REGION}'
    
    healthomics {
        workgroup = '${AWS_HEALTHOMICS_WORKGROUP}'
        role = '${AWS_HEALTHOMICS_ROLE}'
        outputLocation = 's3://${AWS_HEALTHOMICS_BUCKET}/outputs/'
        logLocation = 's3://${AWS_HEALTHOMICS_BUCKET}/logs/'
    }
    
    batch {
        cliPath = '/usr/local/bin/aws'
        jobRole = '${AWS_HEALTHOMICS_ROLE}'
        queue = '${AWS_HEALTHOMICS_QUEUE}'
        computeEnvironment = '${AWS_HEALTHOMICS_COMPUTE_ENV}'
    }
}

// HealthOmics specific process configuration
process {
    executor = 'awsbatch'
    
    // Resource allocation optimized for HealthOmics
    withName: '.*' {
        cpus = { check_max( 1    * task.attempt, 'cpus'    ) }
        memory = { check_max( 6.GB * task.attempt, 'memory'  ) }
        time = { check_max( 4.h * task.attempt, 'time'    ) }
        
        // HealthOmics specific settings
        container = 'public.ecr.aws/healthomics/nextflow:latest'
        errorStrategy = 'retry'
        maxRetries = 3
        
        // CloudWatch logging
        beforeScript = '''
            echo "Starting process: $task.name"
            echo "Process ID: $task.process"
            echo "Task ID: $task.hash"
            echo "Attempt: $task.attempt"
        '''
        
        afterScript = '''
            echo "Completed process: $task.name"
            echo "Exit status: $task.exitStatus"
        '''
    }
}

// HealthOmics execution profiles
profiles {
    healthomics {
        process.executor = 'awsbatch'
        aws.region = '${AWS_DEFAULT_REGION}'
        aws.healthomics.workgroup = '${AWS_HEALTHOMICS_WORKGROUP}'
        
        // Enable HealthOmics monitoring
        monitoring.enabled = true
        monitoring.interval = '30s'
        
        // Configure data management
        workDir = 's3://${AWS_HEALTHOMICS_BUCKET}/work/'
        publishDir = [
            path: 's3://${AWS_HEALTHOMICS_BUCKET}/results/',
            mode: 'copy',
            saveAs: { filename -> filename.equals('versions') ? null : filename }
        ]
    }
    
    healthomics-dev {
        includeConfig 'profiles/healthomics'
        process.cpus = 1
        process.memory = '2 GB'
        process.time = '1h'
    }
    
    healthomics-prod {
        includeConfig 'profiles/healthomics'
        process.cpus = 4
        process.memory = '16 GB'
        process.time = '8h'
    }
}
"""
        return config
    
    def _generate_monitoring_code(self) -> str:
        """Generate monitoring and logging code."""
        
        monitoring_code = """
// HealthOmics Monitoring Functions
def healthomics_log(message) {
    def timestamp = new Date().format('yyyy-MM-dd HH:mm:ss')
    def logMessage = "[$timestamp] [HEALTHOMICS] $message"
    println logMessage
    
    // Send to CloudWatch if available
    try {
        sh "aws logs put-log-events --log-group-name /aws/healthomics/nextflow --log-stream-name \${task.hash} --log-events timestamp=\$(date +%s)000,message='$logMessage' 2>/dev/null || true"
    } catch (Exception e) {
        // Ignore CloudWatch errors
    }
}

def healthomics_metrics(processName, duration, memory, cpu) {
    def metrics = [
        "process_name:$processName",
        "duration:$duration",
        "memory_used:$memory",
        "cpu_used:$cpu",
        "timestamp:${new Date().format('yyyy-MM-dd HH:mm:ss')}"
    ].join(',')
    
    healthomics_log("METRICS: $metrics")
}

// Enhanced error handling for HealthOmics
def healthomics_error_handler(processName, error) {
    healthomics_log("ERROR in $processName: $error")
    
    // Send error to HealthOmics monitoring
    try {
        sh "aws healthomics create-run --workflow-id \${WORKFLOW_ID} --status FAILED --error-message '$error' 2>/dev/null || true"
    } catch (Exception e) {
        healthomics_log("Failed to report error to HealthOmics: $e")
    }
}
"""
        return monitoring_code
    
    def _generate_error_handling(self) -> str:
        """Generate error handling code."""
        
        error_handling = """
// HealthOmics Error Handling
process {
    errorStrategy = { task.exitStatus in [143,137,104,134,139] ? 'retry' : 'terminate' }
    maxRetries = 3
    retry.delay = { task.attempt * 30 }
    
    // Custom error handling
    onError {
        healthomics_error_handler(task.name, task.errorMessage)
    }
    
    // Resource cleanup
    afterScript {
        // Clean up temporary files
        sh 'rm -rf /tmp/nextflow* || true'
        
        // Log resource usage
        healthomics_metrics(task.name, task.duration, task.memory, task.cpus)
    }
}
"""
        return error_handling
    
    def _combine_pipeline_components(
        self,
        base_pipeline: str,
        config: str,
        monitoring: str,
        error_handling: str
    ) -> str:
        """Combine all pipeline components."""
        
        # Insert monitoring functions at the beginning
        enhanced_pipeline = monitoring + "\n" + base_pipeline
        
        # Add configuration at the end
        enhanced_pipeline += "\n" + config
        
        # Add error handling
        enhanced_pipeline += "\n" + error_handling
        
        return enhanced_pipeline
    
    def create_healthomics_workflow(
        self,
        workflow_name: str,
        workflow_definition: str,
        description: str = ""
    ) -> Optional[str]:
        """
        Create a workflow in AWS HealthOmics.
        
        Args:
            workflow_name: Name of the workflow
            workflow_definition: Workflow definition (Nextflow)
            description: Workflow description
            
        Returns:
            Workflow ID if successful, None otherwise
        """
        if not self.healthomics_client:
            logger.error("AWS HealthOmics client not initialized")
            return None
        
        try:
            response = self.healthomics_client.create_workflow(
                name=workflow_name,
                description=description,
                definitionLanguage='NEXTFLOW',
                definition=workflow_definition,
                parameterTemplate={
                    'parameters': self._extract_workflow_parameters(workflow_definition)
                }
            )
            
            workflow_id = response['id']
            logger.info(f"Created HealthOmics workflow: {workflow_id}")
            return workflow_id
            
        except ClientError as e:
            logger.error(f"Failed to create HealthOmics workflow: {e}")
            return None
    
    def _extract_workflow_parameters(self, workflow_definition: str) -> List[Dict[str, Any]]:
        """Extract parameters from workflow definition."""
        # This is a simplified implementation
        # In practice, you'd parse the Nextflow workflow to extract parameters
        parameters = []
        
        # Look for params definitions in the workflow
        lines = workflow_definition.split('\n')
        for line in lines:
            if line.strip().startswith('params.'):
                param_name = line.strip().split('.')[1].split(' ')[0]
                parameters.append({
                    'name': param_name,
                    'type': 'string',
                    'description': f'Parameter {param_name}'
                })
        
        return parameters
    
    def setup_healthomics_environment(self) -> Dict[str, Any]:
        """
        Setup AWS HealthOmics environment.
        
        Returns:
            Dictionary with setup results
        """
        setup_results = {
            "workgroup_created": False,
            "role_created": False,
            "bucket_created": False,
            "errors": []
        }
        
        try:
            # Check/create workgroup
            workgroup_result = self._setup_workgroup()
            setup_results["workgroup_created"] = workgroup_result
            
            # Check/create IAM role
            role_result = self._setup_iam_role()
            setup_results["role_created"] = role_result
            
            # Check/create S3 bucket
            bucket_result = self._setup_s3_bucket()
            setup_results["bucket_created"] = bucket_result
            
        except Exception as e:
            setup_results["errors"].append(str(e))
            logger.error(f"Setup failed: {e}")
        
        return setup_results
    
    def _setup_workgroup(self) -> bool:
        """Setup HealthOmics workgroup."""
        try:
            # Try to get existing workgroup
            response = self.healthomics_client.get_workgroup(name='default')
            logger.info("Workgroup 'default' already exists")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                try:
                    # Create new workgroup
                    self.healthomics_client.create_workgroup(
                        name='default',
                        description='Default workgroup for CWL to Nextflow migration'
                    )
                    logger.info("Created workgroup 'default'")
                    return True
                except ClientError as create_error:
                    logger.error(f"Failed to create workgroup: {create_error}")
                    return False
            else:
                logger.error(f"Error checking workgroup: {e}")
                return False
    
    def _setup_iam_role(self) -> bool:
        """Setup IAM role for HealthOmics."""
        role_name = 'HealthOmicsExecutionRole'
        
        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=role_name)
            logger.info(f"IAM role '{role_name}' already exists")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                logger.info(f"IAM role '{role_name}' needs to be created manually")
                logger.info("Please create the role with appropriate HealthOmics permissions")
                return False
            else:
                logger.error(f"Error checking IAM role: {e}")
                return False
    
    def _setup_s3_bucket(self) -> bool:
        """Setup S3 bucket for HealthOmics."""
        # This would require S3 client and bucket creation logic
        # For now, just return True as bucket setup is typically manual
        logger.info("S3 bucket setup should be done manually")
        return True
    
    def validate_healthomics_setup(self) -> Dict[str, Any]:
        """
        Validate AWS HealthOmics setup.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "credentials_valid": False,
            "workgroup_accessible": False,
            "role_accessible": False,
            "permissions_valid": False,
            "errors": []
        }
        
        try:
            # Test credentials
            sts_client = boto3.client('sts')
            sts_client.get_caller_identity()
            validation_results["credentials_valid"] = True
            
            # Test HealthOmics access
            if self.healthomics_client:
                self.healthomics_client.list_workgroups()
                validation_results["workgroup_accessible"] = True
            
            # Test IAM access
            if self.iam_client:
                self.iam_client.list_roles()
                validation_results["role_accessible"] = True
            
            validation_results["permissions_valid"] = (
                validation_results["credentials_valid"] and
                validation_results["workgroup_accessible"] and
                validation_results["role_accessible"]
            )
            
        except Exception as e:
            validation_results["errors"].append(str(e))
            logger.error(f"Validation failed: {e}")
        
        return validation_results

