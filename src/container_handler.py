"""
Container Handler Module

Handles Docker and Singularity container specifications for CWL to Nextflow migration.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class ContainerHandler:
    """Handles container specifications and registries."""
    
    def __init__(self):
        """Initialize the container handler."""
        self.registry_mappings = {
            "docker.io": "public.ecr.aws",
            "quay.io": "public.ecr.aws",
            "gcr.io": "public.ecr.aws",
            "k8s.gcr.io": "public.ecr.aws"
        }
        
        # Common bioinformatics containers
        self.bio_containers = {
            "bwa": "public.ecr.aws/healthomics/bwa:latest",
            "samtools": "public.ecr.aws/healthomics/samtools:latest",
            "bcftools": "public.ecr.aws/healthomics/bcftools:latest",
            "gatk": "public.ecr.aws/healthomics/gatk:latest",
            "fastqc": "public.ecr.aws/healthomics/fastqc:latest",
            "trimmomatic": "public.ecr.aws/healthomics/trimmomatic:latest",
            "star": "public.ecr.aws/healthomics/star:latest",
            "hisat2": "public.ecr.aws/healthomics/hisat2:latest",
            "kallisto": "public.ecr.aws/healthomics/kallisto:latest",
            "salmon": "public.ecr.aws/healthomics/salmon:latest"
        }
    
    def process_containers(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process container specifications from CWL components.
        
        Args:
            components: CWL workflow components
            
        Returns:
            Dictionary with processed container specifications
        """
        logger.info("Processing container specifications")
        
        container_specs = {}
        
        # Process requirements and hints for containers
        requirements = components.get("requirements", {})
        hints = components.get("hints", {})
        
        # Extract Docker requirements
        docker_requirements = requirements.get("docker", []) + hints.get("docker", [])
        
        # Process each process
        for process_name, process_def in components.get("processes", {}).items():
            container_specs[process_name] = self._process_process_containers(
                process_def, docker_requirements
            )
        
        return container_specs
    
    def _process_process_containers(
        self, 
        process_def: Dict[str, Any], 
        docker_requirements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process container specifications for a single process."""
        
        container_spec = {
            "image": "",
            "registry": "",
            "tag": "latest",
            "type": "docker",
            "aws_optimized": False,
            "pull_policy": "always"
        }
        
        # Check process-specific requirements
        process_requirements = process_def.get("requirements", [])
        process_hints = process_def.get("hints", [])
        
        # Look for Docker requirements in process
        for req in process_requirements + process_hints:
            if req.get("class") == "DockerRequirement":
                container_spec.update(self._extract_docker_requirement(req))
                break
        
        # If no process-specific container, use global requirements
        if not container_spec["image"] and docker_requirements:
            for req in docker_requirements:
                if req.get("class") == "DockerRequirement":
                    container_spec.update(self._extract_docker_requirement(req))
                    break
        
        # Optimize for AWS if needed
        if container_spec["image"]:
            container_spec = self._optimize_for_aws(container_spec)
        
        return container_spec
    
    def _extract_docker_requirement(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Docker requirement information."""
        
        container_spec = {}
        
        # Extract Docker image
        if "dockerPull" in req:
            image = req["dockerPull"]
            container_spec["image"] = image
            container_spec["registry"], container_spec["tag"] = self._parse_image_name(image)
        elif "dockerImageId" in req:
            image = req["dockerImageId"]
            container_spec["image"] = image
            container_spec["registry"], container_spec["tag"] = self._parse_image_name(image)
        elif "dockerFile" in req:
            # Handle Dockerfile-based containers
            container_spec["dockerfile"] = req["dockerFile"]
            container_spec["image"] = "custom-built"
        
        # Extract additional Docker options
        if "dockerOutputDirectory" in req:
            container_spec["output_directory"] = req["dockerOutputDirectory"]
        
        if "dockerLoad" in req:
            container_spec["load_from"] = req["dockerLoad"]
        
        return container_spec
    
    def _parse_image_name(self, image_name: str) -> Tuple[str, str]:
        """Parse Docker image name into registry and tag."""
        
        # Handle different image formats
        if "/" in image_name:
            parts = image_name.split("/")
            if len(parts) >= 3:
                # Full registry path: registry.com/namespace/image:tag
                registry = "/".join(parts[:-1])
                image_with_tag = parts[-1]
            else:
                # Namespace/image:tag format
                registry = parts[0]
                image_with_tag = parts[1]
        else:
            # Simple image:tag format
            registry = "docker.io"
            image_with_tag = image_name
        
        # Extract tag
        if ":" in image_with_tag:
            image, tag = image_with_tag.rsplit(":", 1)
        else:
            image = image_with_tag
            tag = "latest"
        
        return f"{registry}/{image}", tag
    
    def _optimize_for_aws(self, container_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize container specification for AWS."""
        
        optimized = container_spec.copy()
        
        # Map to AWS-compatible registry
        original_image = optimized["image"]
        aws_image = self._map_to_aws_registry(original_image)
        
        if aws_image != original_image:
            optimized["image"] = aws_image
            optimized["aws_optimized"] = True
            optimized["original_image"] = original_image
        
        # Add AWS-specific settings
        optimized["aws_settings"] = {
            "pull_policy": "always",
            "security_context": {
                "runAsUser": 1000,
                "runAsGroup": 1000
            },
            "resources": {
                "requests": {
                    "memory": "1Gi",
                    "cpu": "1"
                },
                "limits": {
                    "memory": "4Gi", 
                    "cpu": "2"
                }
            }
        }
        
        return optimized
    
    def _map_to_aws_registry(self, image_name: str) -> str:
        """Map container image to AWS-compatible registry."""
        
        # Check if already using AWS registry
        if "public.ecr.aws" in image_name or "dkr.ecr" in image_name:
            return image_name
        
        # Check for known bioinformatics containers
        image_base = self._extract_image_base(image_name)
        if image_base in self.bio_containers:
            return self.bio_containers[image_base]
        
        # Map common registries
        for original_registry, aws_registry in self.registry_mappings.items():
            if image_name.startswith(original_registry):
                return image_name.replace(original_registry, aws_registry)
        
        # For unknown images, suggest AWS ECR format
        return f"public.ecr.aws/healthomics/{image_base}:latest"
    
    def _extract_image_base(self, image_name: str) -> str:
        """Extract base image name without registry and tag."""
        
        # Remove registry
        if "/" in image_name:
            image_name = image_name.split("/")[-1]
        
        # Remove tag
        if ":" in image_name:
            image_name = image_name.split(":")[0]
        
        return image_name
    
    def generate_container_manifest(self, container_specs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate container manifest for deployment."""
        
        manifest = {
            "version": "1.0",
            "containers": {},
            "registries": set(),
            "total_containers": len(container_specs)
        }
        
        for process_name, spec in container_specs.items():
            manifest["containers"][process_name] = {
                "image": spec["image"],
                "registry": spec.get("registry", ""),
                "tag": spec.get("tag", "latest"),
                "type": spec.get("type", "docker"),
                "aws_optimized": spec.get("aws_optimized", False)
            }
            
            # Collect registries
            if spec.get("registry"):
                manifest["registries"].add(spec["registry"])
        
        # Convert set to list for JSON serialization
        manifest["registries"] = list(manifest["registries"])
        
        return manifest
    
    def validate_containers(self, container_specs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate container specifications."""
        
        validation_results = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        for process_name, spec in container_specs.items():
            # Check if image is specified
            if not spec.get("image"):
                validation_results["issues"].append(
                    f"Process '{process_name}' has no container image specified"
                )
                validation_results["valid"] = False
            
            # Check for AWS optimization
            if not spec.get("aws_optimized", False):
                validation_results["warnings"].append(
                    f"Process '{process_name}' container not optimized for AWS"
                )
                validation_results["recommendations"].append(
                    f"Consider using AWS ECR registry for '{process_name}'"
                )
            
            # Check image format
            image = spec.get("image", "")
            if image and not self._is_valid_image_format(image):
                validation_results["issues"].append(
                    f"Process '{process_name}' has invalid image format: {image}"
                )
                validation_results["valid"] = False
        
        return validation_results
    
    def _is_valid_image_format(self, image: str) -> bool:
        """Validate Docker image format."""
        
        # Basic validation regex
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._-]*(/[a-zA-Z0-9][a-zA-Z0-9._-]*)*(:[a-zA-Z0-9][a-zA-Z0-9._-]*)?$'
        return bool(re.match(pattern, image))
    
    def generate_pull_script(self, container_specs: Dict[str, Any]) -> str:
        """Generate script to pull all required containers."""
        
        script_lines = [
            "#!/bin/bash",
            "# Container pull script for CWL to Nextflow migration",
            "set -e",
            "",
            "echo 'Pulling required containers...'",
            ""
        ]
        
        for process_name, spec in container_specs.items():
            image = spec.get("image", "")
            if image:
                script_lines.extend([
                    f"echo 'Pulling container for {process_name}...'",
                    f"docker pull {image}",
                    ""
                ])
        
        script_lines.extend([
            "echo 'All containers pulled successfully!'",
            ""
        ])
        
        return "\n".join(script_lines)
    
    def generate_ecr_push_script(self, container_specs: Dict[str, Any]) -> str:
        """Generate script to push containers to AWS ECR."""
        
        script_lines = [
            "#!/bin/bash",
            "# ECR push script for CWL to Nextflow migration",
            "set -e",
            "",
            "# Set AWS region",
            "AWS_REGION=${AWS_REGION:-us-east-1}",
            "ECR_REGISTRY=${ECR_REGISTRY:-public.ecr.aws/healthomics}",
            "",
            "echo 'Logging into ECR...'",
            "aws ecr-public get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin public.ecr.aws",
            "",
            "echo 'Pushing containers to ECR...'",
            ""
        ]
        
        for process_name, spec in container_specs.items():
            original_image = spec.get("original_image", "")
            aws_image = spec.get("image", "")
            
            if original_image and aws_image and original_image != aws_image:
                script_lines.extend([
                    f"echo 'Tagging and pushing {process_name}...'",
                    f"docker tag {original_image} {aws_image}",
                    f"docker push {aws_image}",
                    ""
                ])
        
        script_lines.extend([
            "echo 'All containers pushed to ECR successfully!'",
            ""
        ])
        
        return "\n".join(script_lines)

