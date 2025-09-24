"""
Resource Mapper Module

Maps CWL resource requirements to AWS-compatible resource specifications.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ResourceMapper:
    """Maps CWL resource requirements to AWS resources."""
    
    def __init__(self):
        """Initialize the resource mapper."""
        # AWS instance type mappings
        self.instance_types = {
            "small": {
                "instance_type": "t3.small",
                "cpus": 2,
                "memory_gb": 2,
                "storage_gb": 20
            },
            "medium": {
                "instance_type": "t3.medium", 
                "cpus": 2,
                "memory_gb": 4,
                "storage_gb": 20
            },
            "large": {
                "instance_type": "t3.large",
                "cpus": 2,
                "memory_gb": 8,
                "storage_gb": 20
            },
            "xlarge": {
                "instance_type": "t3.xlarge",
                "cpus": 4,
                "memory_gb": 16,
                "storage_gb": 20
            },
            "2xlarge": {
                "instance_type": "t3.2xlarge",
                "cpus": 8,
                "memory_gb": 32,
                "storage_gb": 20
            }
        }
        
        # Memory unit conversions
        self.memory_units = {
            "B": 1,
            "KB": 1024,
            "MB": 1024**2,
            "GB": 1024**3,
            "TB": 1024**4
        }
    
    def map_resources(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map CWL resource requirements to AWS resources.
        
        Args:
            components: CWL workflow components
            
        Returns:
            Dictionary with mapped resource requirements
        """
        logger.info("Mapping CWL resources to AWS resources")
        
        resource_mapping = {}
        
        for process_name, process_def in components.get("processes", {}).items():
            resource_mapping[process_name] = self._map_process_resources(process_def)
        
        return resource_mapping
    
    def optimize_for_aws(
        self, 
        components: Dict[str, Any], 
        target_instance_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Optimize resource requirements for AWS.
        
        Args:
            components: CWL workflow components
            target_instance_type: Target AWS instance type
            
        Returns:
            Dictionary with optimized resource requirements
        """
        logger.info("Optimizing resources for AWS")
        
        # Get base resource mapping
        resource_mapping = self.map_resources(components)
        
        # Apply AWS optimizations
        optimized_mapping = {}
        
        for process_name, resources in resource_mapping.items():
            optimized_mapping[process_name] = self._optimize_process_resources(
                resources, target_instance_type
            )
        
        return optimized_mapping
    
    def _map_process_resources(self, process_def: Dict[str, Any]) -> Dict[str, Any]:
        """Map resources for a single process."""
        
        # Default resources
        resources = {
            "cpus": 1,
            "memory": "1 GB",
            "disk": "10 GB",
            "time": "1h",
            "instance_type": "t3.small"
        }
        
        # Extract from requirements
        requirements = process_def.get("requirements", [])
        hints = process_def.get("hints", [])
        
        # Process requirements
        for req in requirements:
            if req.get("class") == "ResourceRequirement":
                resources.update(self._extract_resource_requirement(req))
        
        # Process hints
        for hint in hints:
            if hint.get("class") == "ResourceRequirement":
                resources.update(self._extract_resource_requirement(hint))
        
        return resources
    
    def _extract_resource_requirement(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """Extract resource requirements from CWL requirement."""
        
        resources = {}
        
        # CPU requirements
        if "coresMin" in req:
            resources["cpus"] = req["coresMin"]
        elif "coresMax" in req:
            resources["cpus"] = req["coresMax"]
        
        # Memory requirements
        if "ramMin" in req:
            resources["memory"] = self._convert_memory(req["ramMin"])
        elif "ramMax" in req:
            resources["memory"] = self._convert_memory(req["ramMax"])
        
        # Disk requirements
        if "tmpdirMin" in req:
            resources["disk"] = self._convert_memory(req["tmpdirMin"])
        elif "tmpdirMax" in req:
            resources["disk"] = self._convert_memory(req["tmpdirMax"])
        
        # Time requirements
        if "outdirMin" in req:
            resources["time"] = self._convert_time(req["outdirMin"])
        elif "outdirMax" in req:
            resources["time"] = self._convert_time(req["outdirMax"])
        
        return resources
    
    def _optimize_process_resources(
        self, 
        resources: Dict[str, Any], 
        target_instance_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Optimize resources for a specific AWS instance type."""
        
        optimized = resources.copy()
        
        if target_instance_type:
            # Get instance specifications
            instance_specs = self._get_instance_specs(target_instance_type)
            
            if instance_specs:
                # Optimize CPU
                optimized["cpus"] = min(resources.get("cpus", 1), instance_specs["cpus"])
                
                # Optimize memory
                current_memory_gb = self._parse_memory_gb(resources.get("memory", "1 GB"))
                optimized["memory"] = f"{min(current_memory_gb, instance_specs['memory_gb'])} GB"
                
                # Set instance type
                optimized["instance_type"] = target_instance_type
        
        # Apply AWS-specific optimizations
        optimized = self._apply_aws_optimizations(optimized)
        
        return optimized
    
    def _get_instance_specs(self, instance_type: str) -> Optional[Dict[str, Any]]:
        """Get specifications for an AWS instance type."""
        
        # Common AWS instance types
        instance_specs = {
            "t3.nano": {"cpus": 2, "memory_gb": 0.5},
            "t3.micro": {"cpus": 2, "memory_gb": 1},
            "t3.small": {"cpus": 2, "memory_gb": 2},
            "t3.medium": {"cpus": 2, "memory_gb": 4},
            "t3.large": {"cpus": 2, "memory_gb": 8},
            "t3.xlarge": {"cpus": 4, "memory_gb": 16},
            "t3.2xlarge": {"cpus": 8, "memory_gb": 32},
            "m5.large": {"cpus": 2, "memory_gb": 8},
            "m5.xlarge": {"cpus": 4, "memory_gb": 16},
            "m5.2xlarge": {"cpus": 8, "memory_gb": 32},
            "m5.4xlarge": {"cpus": 16, "memory_gb": 64},
            "c5.large": {"cpus": 2, "memory_gb": 4},
            "c5.xlarge": {"cpus": 4, "memory_gb": 8},
            "c5.2xlarge": {"cpus": 8, "memory_gb": 16},
            "c5.4xlarge": {"cpus": 16, "memory_gb": 32},
            "r5.large": {"cpus": 2, "memory_gb": 16},
            "r5.xlarge": {"cpus": 4, "memory_gb": 32},
            "r5.2xlarge": {"cpus": 8, "memory_gb": 64},
            "r5.4xlarge": {"cpus": 16, "memory_gb": 128}
        }
        
        return instance_specs.get(instance_type)
    
    def _apply_aws_optimizations(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """Apply AWS-specific optimizations."""
        
        optimized = resources.copy()
        
        # Ensure minimum resources for AWS Batch
        optimized["cpus"] = max(optimized.get("cpus", 1), 1)
        
        # Ensure memory is at least 1 GB
        current_memory_gb = self._parse_memory_gb(optimized.get("memory", "1 GB"))
        optimized["memory"] = f"{max(current_memory_gb, 1)} GB"
        
        # Add AWS-specific settings
        optimized["aws_batch"] = {
            "job_queue": "default",
            "job_definition": "nextflow-job",
            "retry_attempts": 3
        }
        
        return optimized
    
    def _convert_memory(self, memory_value: Any) -> str:
        """Convert CWL memory value to human-readable format."""
        
        if isinstance(memory_value, (int, float)):
            # Assume bytes
            return self._bytes_to_human(memory_value)
        elif isinstance(memory_value, str):
            # Parse string format
            return self._parse_memory_string(memory_value)
        else:
            return "1 GB"  # Default
    
    def _convert_time(self, time_value: Any) -> str:
        """Convert CWL time value to human-readable format."""
        
        if isinstance(time_value, (int, float)):
            # Assume seconds
            return self._seconds_to_human(time_value)
        elif isinstance(time_value, str):
            # Parse string format
            return self._parse_time_string(time_value)
        else:
            return "1h"  # Default
    
    def _bytes_to_human(self, bytes_value: int) -> str:
        """Convert bytes to human-readable format."""
        
        for unit, multiplier in reversed(list(self.memory_units.items())):
            if bytes_value >= multiplier:
                value = bytes_value / multiplier
                return f"{value:.1f} {unit}"
        
        return f"{bytes_value} B"
    
    def _parse_memory_string(self, memory_str: str) -> str:
        """Parse memory string and return in GB format."""
        
        memory_str = memory_str.strip().upper()
        
        for unit, multiplier in self.memory_units.items():
            if unit in memory_str:
                value = float(memory_str.replace(unit, "").strip())
                bytes_value = value * multiplier
                return self._bytes_to_human(bytes_value)
        
        return "1 GB"  # Default
    
    def _parse_memory_gb(self, memory_str: str) -> float:
        """Parse memory string and return value in GB."""
        
        memory_str = memory_str.strip().upper()
        
        for unit, multiplier in self.memory_units.items():
            if unit in memory_str:
                value = float(memory_str.replace(unit, "").strip())
                return value * (multiplier / self.memory_units["GB"])
        
        return 1.0  # Default
    
    def _seconds_to_human(self, seconds: int) -> str:
        """Convert seconds to human-readable format."""
        
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours}h"
        else:
            days = seconds // 86400
            return f"{days}d"
    
    def _parse_time_string(self, time_str: str) -> str:
        """Parse time string and return in human-readable format."""
        
        time_str = time_str.strip().lower()
        
        # Common time formats
        if time_str.endswith('s'):
            seconds = int(time_str[:-1])
            return self._seconds_to_human(seconds)
        elif time_str.endswith('m'):
            minutes = int(time_str[:-1])
            return self._seconds_to_human(minutes * 60)
        elif time_str.endswith('h'):
            hours = int(time_str[:-1])
            return self._seconds_to_human(hours * 3600)
        elif time_str.endswith('d'):
            days = int(time_str[:-1])
            return self._seconds_to_human(days * 86400)
        
        return "1h"  # Default
    
    def generate_resource_report(self, resource_mapping: Dict[str, Any]) -> str:
        """Generate a resource usage report."""
        
        report = ["Resource Usage Report", "=" * 50, ""]
        
        total_cpus = 0
        total_memory_gb = 0
        
        for process_name, resources in resource_mapping.items():
            report.append(f"Process: {process_name}")
            report.append(f"  CPUs: {resources.get('cpus', 'N/A')}")
            report.append(f"  Memory: {resources.get('memory', 'N/A')}")
            report.append(f"  Disk: {resources.get('disk', 'N/A')}")
            report.append(f"  Time: {resources.get('time', 'N/A')}")
            report.append(f"  Instance Type: {resources.get('instance_type', 'N/A')}")
            report.append("")
            
            # Accumulate totals
            total_cpus += resources.get('cpus', 0)
            total_memory_gb += self._parse_memory_gb(resources.get('memory', '0 GB'))
        
        report.append("Summary:")
        report.append(f"  Total CPUs: {total_cpus}")
        report.append(f"  Total Memory: {total_memory_gb:.1f} GB")
        report.append("")
        
        return "\n".join(report)

