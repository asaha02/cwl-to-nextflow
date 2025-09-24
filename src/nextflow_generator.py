"""
Nextflow Generator Module

Generates Nextflow pipelines from parsed CWL workflow components.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from jinja2 import Environment, FileSystemLoader, Template

logger = logging.getLogger(__name__)


class NextflowGenerator:
    """Generator for Nextflow pipelines from CWL components."""
    
    def __init__(self):
        """Initialize the Nextflow generator."""
        self.template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
    def generate_pipeline(
        self,
        components: Dict[str, Any],
        resource_mapping: Dict[str, Any],
        container_specs: Dict[str, Any],
        aws_healthomics: bool = False,
        custom_template: Optional[str] = None
    ) -> str:
        """
        Generate a Nextflow pipeline from CWL components.
        
        Args:
            components: Parsed CWL workflow components
            resource_mapping: Resource requirements mapping
            container_specs: Container specifications
            aws_healthomics: Enable AWS HealthOmics features
            custom_template: Path to custom template
            
        Returns:
            Generated Nextflow pipeline as string
        """
        logger.info("Generating Nextflow pipeline")
        
        # Select template
        if custom_template:
            template = self._load_custom_template(custom_template)
        elif aws_healthomics:
            template = self.jinja_env.get_template("aws_healthomics_template.nf")
        else:
            template = self.jinja_env.get_template("base_template.nf")
        
        # Prepare template context
        context = self._prepare_context(
            components, resource_mapping, container_specs, aws_healthomics
        )
        
        # Generate pipeline
        pipeline = template.render(**context)
        
        logger.info("Nextflow pipeline generated successfully")
        return pipeline
    
    def _load_custom_template(self, template_path: str) -> Template:
        """Load a custom Jinja2 template."""
        with open(template_path, 'r') as f:
            template_content = f.read()
        return Template(template_content)
    
    def _prepare_context(
        self,
        components: Dict[str, Any],
        resource_mapping: Dict[str, Any],
        container_specs: Dict[str, Any],
        aws_healthomics: bool
    ) -> Dict[str, Any]:
        """Prepare context data for template rendering."""
        
        context = {
            "workflow_info": components["workflow_info"],
            "inputs": self._process_inputs_for_nextflow(components["inputs"]),
            "outputs": self._process_outputs_for_nextflow(components["outputs"]),
            "processes": self._process_steps_for_nextflow(
                components["processes"], resource_mapping, container_specs
            ),
            "workflow": self._generate_workflow_logic(components["processes"]),
            "aws_healthomics": aws_healthomics,
            "resource_mapping": resource_mapping,
            "container_specs": container_specs
        }
        
        return context
    
    def _process_inputs_for_nextflow(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process inputs for Nextflow parameter definitions."""
        nextflow_inputs = []
        
        for input_name, input_def in inputs.items():
            # Debug logging
            logger.debug(f"Processing input: {input_name}, type: {type(input_def)}, value: {input_def}")
            
            # Handle both string and dictionary input definitions
            if isinstance(input_def, str):
                # Simple string input (fallback)
                nextflow_input = {
                    "name": input_name,
                    "type": "string",
                    "description": f"Input parameter: {input_name}",
                    "default": None,
                    "required": True
                }
            elif isinstance(input_def, dict):
                # Dictionary input definition
                nextflow_input = {
                    "name": input_name,
                    "type": self._map_cwl_type_to_nextflow(input_def.get("type", "string")),
                    "description": input_def.get("description", input_def.get("doc", f"Input parameter: {input_name}")),
                    "default": input_def.get("default"),
                    "required": input_def.get("required", input_def.get("default") is None)
                }
            else:
                # Fallback for other types
                logger.warning(f"Unexpected input definition type for {input_name}: {type(input_def)}")
                nextflow_input = {
                    "name": input_name,
                    "type": "string",
                    "description": f"Input parameter: {input_name}",
                    "default": None,
                    "required": True
                }
            
            nextflow_inputs.append(nextflow_input)
        
        return nextflow_inputs
    
    def _process_outputs_for_nextflow(self, outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process outputs for Nextflow output definitions."""
        nextflow_outputs = []
        
        for output_name, output_def in outputs.items():
            # Debug logging
            logger.debug(f"Processing output: {output_name}, type: {type(output_def)}, value: {output_def}")
            
            # Handle both string and dictionary output definitions
            if isinstance(output_def, str):
                # Simple string output (fallback)
                nextflow_output = {
                    "name": output_name,
                    "type": "string",
                    "description": f"Output parameter: {output_name}"
                }
            elif isinstance(output_def, dict):
                # Dictionary output definition
                nextflow_output = {
                    "name": output_name,
                    "type": self._map_cwl_type_to_nextflow(output_def.get("type", "string")),
                    "description": output_def.get("description", output_def.get("doc", f"Output parameter: {output_name}"))
                }
            else:
                # Fallback for other types
                logger.warning(f"Unexpected output definition type for {output_name}: {type(output_def)}")
                nextflow_output = {
                    "name": output_name,
                    "type": "string",
                    "description": f"Output parameter: {output_name}"
                }
            
            nextflow_outputs.append(nextflow_output)
        
        return nextflow_outputs
    
    def _process_steps_for_nextflow(
        self,
        steps: Dict[str, Any],
        resource_mapping: Dict[str, Any],
        container_specs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Process steps into Nextflow process definitions."""
        nextflow_processes = []
        
        for step_name, step_def in steps.items():
            # Ensure step_def is a dictionary
            if not isinstance(step_def, dict):
                logger.warning(f"Step {step_name} definition is not a dictionary: {type(step_def)}")
                continue
            
            # Get inputs with fallback
            inputs = step_def.get("inputs", {})
            if not isinstance(inputs, dict):
                logger.warning(f"Step {step_name} inputs is not a dictionary: {type(inputs)}")
                inputs = {}
            
            # Get outputs with fallback
            outputs = step_def.get("outputs", [])
            if not isinstance(outputs, list):
                logger.warning(f"Step {step_name} outputs is not a list: {type(outputs)}")
                outputs = []
            
            process = {
                "name": step_name,
                "container": container_specs.get(step_name, {}).get("image", ""),
                "resources": resource_mapping.get(step_name, {}),
                "inputs": self._process_step_inputs(inputs),
                "outputs": self._process_step_outputs(outputs),
                "script": self._generate_process_script(step_def),
                "requirements": step_def.get("requirements", []),
                "hints": step_def.get("hints", [])
            }
            nextflow_processes.append(process)
        
        return nextflow_processes
    
    def _process_step_inputs(self, step_inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process step inputs for Nextflow process."""
        inputs = []
        
        for input_name, input_def in step_inputs.items():
            # Handle both string and dictionary input definitions
            if isinstance(input_def, str):
                # Simple string reference (e.g., "input_file")
                input_item = {
                    "name": input_name,
                    "source": input_def,
                    "value_from": None,
                    "link_merge": None
                }
            elif isinstance(input_def, dict):
                # Complex input definition with properties
                input_item = {
                    "name": input_name,
                    "source": input_def.get("source", ""),
                    "value_from": input_def.get("valueFrom"),
                    "link_merge": input_def.get("linkMerge")
                }
            else:
                # Fallback for other types
                input_item = {
                    "name": input_name,
                    "source": str(input_def),
                    "value_from": None,
                    "link_merge": None
                }
            
            inputs.append(input_item)
        
        return inputs
    
    def _process_step_outputs(self, step_outputs: List[str]) -> List[Dict[str, Any]]:
        """Process step outputs for Nextflow process."""
        outputs = []
        
        for output_name in step_outputs:
            output_item = {
                "name": output_name,
                "type": "file"  # Default type, could be enhanced
            }
            outputs.append(output_item)
        
        return outputs
    
    def _generate_process_script(self, step_def: Dict[str, Any]) -> str:
        """Generate the script section for a Nextflow process."""
        # This is a simplified version - in practice, you'd need to parse
        # the actual CWL tool definition to extract the command
        script_template = """
        # Process script for {step_name}
        # This would be generated from the actual CWL tool definition
        
        # Example command structure
        # Replace with actual command from CWL tool
        echo "Running {step_name}"
        
        # Input processing
        # Output generation
        """
        
        # Handle both string and dictionary step definitions
        if isinstance(step_def, dict):
            step_name = step_def.get("name", "unknown")
        else:
            step_name = str(step_def) if step_def else "unknown"
        
        return script_template.format(step_name=step_name)
    
    def _generate_workflow_logic(self, steps: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate workflow logic for Nextflow."""
        workflow_steps = []
        
        for step_name, step_def in steps.items():
            # Handle both string and dictionary step definitions
            if isinstance(step_def, dict):
                inputs = step_def.get("inputs", {})
                outputs = step_def.get("outputs", [])
                inputs_list = list(inputs.keys()) if isinstance(inputs, dict) else []
            else:
                inputs_list = []
                outputs = []
            
            workflow_step = {
                "name": step_name,
                "inputs": inputs_list,
                "outputs": outputs if isinstance(outputs, list) else [],
                "dependencies": self._find_step_dependencies(step_def, steps)
            }
            workflow_steps.append(workflow_step)
        
        return workflow_steps
    
    def _find_step_dependencies(
        self, step_def: Dict[str, Any], all_steps: Dict[str, Any]
    ) -> List[str]:
        """Find dependencies for a workflow step."""
        dependencies = []
        
        # Handle both string and dictionary step definitions
        if isinstance(step_def, dict):
            inputs = step_def.get("inputs", {})
            if isinstance(inputs, dict):
                for input_name, input_def in inputs.items():
                    # Handle both string and dictionary input definitions
                    if isinstance(input_def, str):
                        source = input_def
                    elif isinstance(input_def, dict):
                        source = input_def.get("source", "")
                    else:
                        source = str(input_def)
                    
                    if source and source in all_steps:
                        dependencies.append(source)
        
        return dependencies
    
    def _map_cwl_type_to_nextflow(self, cwl_type: str) -> str:
        """Map CWL types to Nextflow types."""
        type_mapping = {
            "string": "string",
            "int": "integer",
            "float": "float",
            "boolean": "boolean",
            "File": "file",
            "Directory": "directory",
            "array": "array",
            "record": "object"
        }
        
        # Handle complex types
        if "array" in cwl_type.lower():
            return "array"
        elif "file" in cwl_type.lower():
            return "file"
        elif "directory" in cwl_type.lower():
            return "directory"
        else:
            return type_mapping.get(cwl_type.lower(), "string")
    
    def generate_config_file(
        self,
        components: Dict[str, Any],
        resource_mapping: Dict[str, Any],
        aws_healthomics: bool = False
    ) -> str:
        """Generate Nextflow configuration file."""
        
        if aws_healthomics:
            config_template = self.jinja_env.get_template("aws_healthomics_config.nf")
        else:
            config_template = self.jinja_env.get_template("base_config.nf")
        
        context = {
            "workflow_info": components["workflow_info"],
            "resource_mapping": resource_mapping,
            "aws_healthomics": aws_healthomics
        }
        
        return config_template.render(**context)
    
    def generate_dockerfile(self, container_specs: Dict[str, Any]) -> str:
        """Generate Dockerfile for containerized workflow."""
        
        dockerfile_template = """
# Generated Dockerfile for CWL to Nextflow migration
FROM ubuntu:20.04

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    wget \\
    curl \\
    python3 \\
    python3-pip \\
    && rm -rf /var/lib/apt/lists/*

# Install Nextflow
RUN wget -qO- https://get.nextflow.io | bash && \\
    mv nextflow /usr/local/bin/

# Install workflow-specific tools
{% for container_name, spec in container_specs.items() %}
# {{ container_name }}
{% if spec.get('packages') %}
RUN apt-get update && apt-get install -y {{ spec.packages | join(' ') }}
{% endif %}
{% endfor %}

# Set working directory
WORKDIR /workspace

# Copy workflow files
COPY . /workspace/

# Set permissions
RUN chmod +x /workspace/*.nf
"""
        
        template = Template(dockerfile_template)
        return template.render(container_specs=container_specs)

