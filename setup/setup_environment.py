#!/usr/bin/env python3
"""
Environment Setup Script for CWL to Nextflow Migration Toolkit

This script sets up the environment and validates all dependencies.
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnvironmentSetup:
    """Handles environment setup and validation."""
    
    def __init__(self):
        """Initialize the environment setup."""
        self.required_commands = {
            'python3': {'min_version': '3.8', 'check_version': True},
            'node': {'min_version': '16.0', 'check_version': True},
            'npm': {'min_version': '8.0', 'check_version': True},
            'docker': {'min_version': '20.0', 'check_version': True},
            'nextflow': {'min_version': '22.0', 'check_version': True},
            'aws': {'min_version': '2.0', 'check_version': True}
        }
        
        self.optional_commands = {
            'singularity': {'min_version': '3.0', 'check_version': True},
            'cwltool': {'min_version': '3.0', 'check_version': True}
        }
        
        self.python_packages = [
            'cwltool', 'ruamel.yaml', 'requests', 'boto3', 'jinja2',
            'click', 'tqdm', 'colorama', 'rich', 'pytest'
        ]
        
        self.node_packages = [
            'cwl-runner', 'cwl-ts'
        ]
    
    def setup_environment(self) -> Dict[str, Any]:
        """Setup the complete environment."""
        logger.info("Setting up CWL to Nextflow migration environment")
        
        setup_results = {
            'success': True,
            'errors': [],
            'warnings': [],
            'installed_components': [],
            'missing_components': [],
            'environment_info': {}
        }
        
        try:
            # Check system requirements
            self._check_system_requirements(setup_results)
            
            # Setup Python environment
            self._setup_python_environment(setup_results)
            
            # Setup Node.js environment
            self._setup_nodejs_environment(setup_results)
            
            # Setup container runtime
            self._setup_container_runtime(setup_results)
            
            # Setup workflow engines
            self._setup_workflow_engines(setup_results)
            
            # Setup AWS tools
            self._setup_aws_tools(setup_results)
            
            # Create configuration files
            self._create_configuration_files(setup_results)
            
            # Validate setup
            self._validate_setup(setup_results)
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            setup_results['success'] = False
            setup_results['errors'].append(str(e))
        
        return setup_results
    
    def _check_system_requirements(self, results: Dict[str, Any]):
        """Check system requirements."""
        logger.info("Checking system requirements")
        
        # Check operating system
        import platform
        system_info = {
            'os': platform.system(),
            'version': platform.version(),
            'architecture': platform.architecture()[0],
            'python_version': platform.python_version()
        }
        
        results['environment_info']['system'] = system_info
        logger.info(f"System: {system_info['os']} {system_info['version']}")
        
        # Check available memory
        try:
            import psutil
            memory = psutil.virtual_memory()
            results['environment_info']['memory'] = {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2)
            }
            
            if memory.total < 4 * 1024**3:  # Less than 4GB
                results['warnings'].append("System has less than 4GB RAM. Some workflows may not run properly.")
        except ImportError:
            results['warnings'].append("psutil not available. Cannot check memory requirements.")
    
    def _setup_python_environment(self, results: Dict[str, Any]):
        """Setup Python environment."""
        logger.info("Setting up Python environment")
        
        # Check Python version
        python_version = self._check_command_version('python3')
        if python_version:
            results['installed_components'].append(f"Python {python_version}")
        else:
            results['missing_components'].append("Python 3.8+")
            results['success'] = False
            return
        
        # Create virtual environment
        venv_path = Path('venv')
        if not venv_path.exists():
            logger.info("Creating Python virtual environment")
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
            results['installed_components'].append("Python virtual environment")
        
        # Install Python packages
        pip_path = venv_path / 'bin' / 'pip' if os.name != 'nt' else venv_path / 'Scripts' / 'pip.exe'
        
        if pip_path.exists():
            logger.info("Installing Python packages")
            subprocess.run([str(pip_path), 'install', '-r', 'requirements.txt'], check=True)
            results['installed_components'].append("Python packages")
        else:
            results['errors'].append("Failed to create virtual environment")
            results['success'] = False
    
    def _setup_nodejs_environment(self, results: Dict[str, Any]):
        """Setup Node.js environment."""
        logger.info("Setting up Node.js environment")
        
        # Check Node.js version
        node_version = self._check_command_version('node')
        if node_version:
            results['installed_components'].append(f"Node.js {node_version}")
        else:
            results['missing_components'].append("Node.js 16+")
            results['success'] = False
            return
        
        # Check npm version
        npm_version = self._check_command_version('npm')
        if npm_version:
            results['installed_components'].append(f"npm {npm_version}")
        else:
            results['missing_components'].append("npm 8+")
            results['success'] = False
            return
        
        # Install Node.js packages
        if Path('package.json').exists():
            logger.info("Installing Node.js packages")
            subprocess.run(['npm', 'install'], check=True)
            results['installed_components'].append("Node.js packages")
        
        # Install CWL reference implementation
        try:
            subprocess.run(['npm', 'install', '-g', 'cwltool'], check=True)
            results['installed_components'].append("CWL reference implementation")
        except subprocess.CalledProcessError:
            results['warnings'].append("Failed to install CWL reference implementation globally")
    
    def _setup_container_runtime(self, results: Dict[str, Any]):
        """Setup container runtime."""
        logger.info("Setting up container runtime")
        
        # Check Docker
        docker_version = self._check_command_version('docker')
        if docker_version:
            results['installed_components'].append(f"Docker {docker_version}")
            
            # Check if Docker daemon is running
            try:
                subprocess.run(['docker', 'info'], check=True, capture_output=True)
                results['installed_components'].append("Docker daemon running")
            except subprocess.CalledProcessError:
                results['warnings'].append("Docker daemon is not running")
        else:
            results['missing_components'].append("Docker 20+")
        
        # Check Singularity (optional)
        singularity_version = self._check_command_version('singularity')
        if singularity_version:
            results['installed_components'].append(f"Singularity {singularity_version}")
        else:
            results['warnings'].append("Singularity not installed (optional)")
    
    def _setup_workflow_engines(self, results: Dict[str, Any]):
        """Setup workflow engines."""
        logger.info("Setting up workflow engines")
        
        # Check Nextflow
        nextflow_version = self._check_command_version('nextflow')
        if nextflow_version:
            results['installed_components'].append(f"Nextflow {nextflow_version}")
        else:
            # Try to install Nextflow
            try:
                logger.info("Installing Nextflow")
                subprocess.run(['curl', '-s', 'https://get.nextflow.io'], 
                             stdout=subprocess.PIPE, text=True, check=True)
                subprocess.run(['bash', '-'], input='curl -s https://get.nextflow.io | bash', 
                             text=True, check=True)
                results['installed_components'].append("Nextflow")
            except subprocess.CalledProcessError:
                results['missing_components'].append("Nextflow 22+")
                results['success'] = False
        
        # Check CWL tool
        cwltool_version = self._check_command_version('cwltool')
        if cwltool_version:
            results['installed_components'].append(f"CWL tool {cwltool_version}")
        else:
            results['warnings'].append("CWL tool not available")
    
    def _setup_aws_tools(self, results: Dict[str, Any]):
        """Setup AWS tools."""
        logger.info("Setting up AWS tools")
        
        # Check AWS CLI
        aws_version = self._check_command_version('aws')
        if aws_version:
            results['installed_components'].append(f"AWS CLI {aws_version}")
            
            # Check AWS credentials
            try:
                result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                                      capture_output=True, text=True, check=True)
                identity = json.loads(result.stdout)
                results['environment_info']['aws'] = {
                    'account_id': identity.get('Account'),
                    'user_id': identity.get('UserId'),
                    'arn': identity.get('Arn')
                }
                results['installed_components'].append("AWS credentials configured")
            except subprocess.CalledProcessError:
                results['warnings'].append("AWS credentials not configured")
        else:
            results['missing_components'].append("AWS CLI 2+")
    
    def _create_configuration_files(self, results: Dict[str, Any]):
        """Create configuration files."""
        logger.info("Creating configuration files")
        
        # Create .env file
        env_content = """# CWL to Nextflow Migration Environment
export AWS_DEFAULT_REGION=us-east-1
export AWS_HEALTHOMICS_WORKGROUP=default
export AWS_HEALTHOMICS_ROLE=HealthOmicsExecutionRole
export AWS_HEALTHOMICS_BUCKET=healthomics-workflows
export AWS_HEALTHOMICS_QUEUE=default
export AWS_HEALTHOMICS_COMPUTE_ENV=default
export CONTAINER_REGISTRY=public.ecr.aws/healthomics
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        results['installed_components'].append("Environment configuration file")
        
        # Create activation script
        activation_script = """#!/bin/bash
# Activation script for CWL to Nextflow migration environment

echo "Activating CWL to Nextflow migration environment..."

# Activate Python virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Python virtual environment activated"
fi

# Load environment variables
if [ -f ".env" ]; then
    source .env
    echo "✓ Environment variables loaded"
fi

echo "Environment ready for CWL to Nextflow migration!"
"""
        
        with open('activate_env.sh', 'w') as f:
            f.write(activation_script)
        
        os.chmod('activate_env.sh', 0o755)
        results['installed_components'].append("Environment activation script")
    
    def _validate_setup(self, results: Dict[str, Any]):
        """Validate the complete setup."""
        logger.info("Validating setup")
        
        # Test Python imports
        try:
            import cwltool
            import boto3
            import jinja2
            results['installed_components'].append("Python package imports working")
        except ImportError as e:
            results['errors'].append(f"Python import error: {e}")
            results['success'] = False
        
        # Test CWL parsing
        try:
            from src.cwl_parser import CWLParser
            results['installed_components'].append("CWL parser module working")
        except ImportError as e:
            results['errors'].append(f"CWL parser error: {e}")
            results['success'] = False
        
        # Test Nextflow generation
        try:
            from src.nextflow_generator import NextflowGenerator
            results['installed_components'].append("Nextflow generator module working")
        except ImportError as e:
            results['errors'].append(f"Nextflow generator error: {e}")
            results['success'] = False
    
    def _check_command_version(self, command: str) -> Optional[str]:
        """Check if a command exists and return its version."""
        try:
            result = subprocess.run([command, '--version'], 
                                  capture_output=True, text=True, check=True)
            version_line = result.stdout.split('\n')[0]
            # Extract version number
            import re
            version_match = re.search(r'(\d+\.\d+\.\d+)', version_line)
            if version_match:
                return version_match.group(1)
            return version_line
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def generate_setup_report(self, results: Dict[str, Any]) -> str:
        """Generate a setup report."""
        report = ["CWL to Nextflow Migration Toolkit - Setup Report", "=" * 60, ""]
        
        # Overall status
        status = "✅ SUCCESS" if results['success'] else "❌ FAILED"
        report.append(f"Setup Status: {status}")
        report.append("")
        
        # Installed components
        if results['installed_components']:
            report.append("Installed Components:")
            for component in results['installed_components']:
                report.append(f"  ✓ {component}")
            report.append("")
        
        # Missing components
        if results['missing_components']:
            report.append("Missing Components:")
            for component in results['missing_components']:
                report.append(f"  ❌ {component}")
            report.append("")
        
        # Warnings
        if results['warnings']:
            report.append("Warnings:")
            for warning in results['warnings']:
                report.append(f"  ⚠️  {warning}")
            report.append("")
        
        # Errors
        if results['errors']:
            report.append("Errors:")
            for error in results['errors']:
                report.append(f"  ❌ {error}")
            report.append("")
        
        # Environment info
        if results['environment_info']:
            report.append("Environment Information:")
            for key, value in results['environment_info'].items():
                report.append(f"  {key}: {value}")
            report.append("")
        
        # Next steps
        if results['success']:
            report.append("Next Steps:")
            report.append("1. Activate environment: source activate_env.sh")
            report.append("2. Configure AWS: ./setup/configure_aws_healthomics.sh")
            report.append("3. Test conversion: python cwl_to_nextflow.py --help")
            report.append("4. Start migrating workflows!")
        else:
            report.append("Please fix the errors above and run setup again.")
        
        return "\n".join(report)


def main():
    """Main setup function."""
    setup = EnvironmentSetup()
    results = setup.setup_environment()
    
    # Generate and print report
    report = setup.generate_setup_report(results)
    print(report)
    
    # Save report to file
    with open('setup_report.txt', 'w') as f:
        f.write(report)
    
    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)


if __name__ == "__main__":
    main()

