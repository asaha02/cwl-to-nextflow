"""
CWL Parser Module

Handles parsing of Common Workflow Language (CWL) files and extraction of workflow components.
"""

import json
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Try to import cwltool modules, but handle gracefully if not available
try:
    import cwltool
    from cwltool import load_tool
    from cwltool.context import LoadingContext
    from cwltool.workflow import Workflow
    from cwltool.command_line_tool import CommandLineTool
    CWLTOOL_AVAILABLE = True
except ImportError:
    CWLTOOL_AVAILABLE = False
    # Create dummy classes for when cwltool is not available
    class LoadingContext:
        pass
    class Workflow:
        pass
    class CommandLineTool:
        pass

try:
    from ruamel.yaml import YAML
    RUAMEL_YAML_AVAILABLE = True
except ImportError:
    RUAMEL_YAML_AVAILABLE = False
    # Fallback to standard yaml
    import yaml as std_yaml

logger = logging.getLogger(__name__)


class CWLParser:
    """Parser for Common Workflow Language files."""
    
    def __init__(self):
        """Initialize the CWL parser."""
        if RUAMEL_YAML_AVAILABLE:
            self.yaml_loader = YAML(typ='safe')
        else:
            self.yaml_loader = None
            
        if CWLTOOL_AVAILABLE:
            self.loading_context = LoadingContext()
        else:
            self.loading_context = None
        
    def parse_cwl_file(self, cwl_path: str) -> Dict[str, Any]:
        """
        Parse a CWL file and return the workflow definition.
        
        Args:
            cwl_path: Path to the CWL file
            
        Returns:
            Dictionary containing the parsed CWL workflow
        """
        logger.info(f"Parsing CWL file: {cwl_path}")
        
        if not CWLTOOL_AVAILABLE:
            # Fallback to simple YAML parsing when cwltool is not available
            logger.warning("cwltool not available, using simple YAML parsing")
            return self._parse_cwl_yaml_simple(cwl_path)
        
        try:
            # Load the CWL tool/workflow
            tool = load_tool.load_tool(cwl_path, self.loading_context)
            
            # Extract workflow information
            workflow_data = {
                "cwlVersion": getattr(tool, "cwlVersion", "v1.0"),
                "class": getattr(tool, "class", "Workflow"),
                "id": getattr(tool, "id", ""),
                "label": getattr(tool, "label", ""),
                "doc": getattr(tool, "doc", ""),
                "inputs": self._extract_inputs(tool),
                "outputs": self._extract_outputs(tool),
                "steps": self._extract_steps(tool),
                "requirements": self._extract_requirements(tool),
                "hints": self._extract_hints(tool),
                "metadata": self._extract_metadata(tool)
            }
            
            logger.info(f"Successfully parsed CWL workflow with {len(workflow_data['steps'])} steps")
            return workflow_data
            
        except Exception as e:
            logger.error(f"Failed to parse CWL file {cwl_path}: {str(e)}")
            # Fallback to simple YAML parsing
            logger.warning("Falling back to simple YAML parsing")
            return self._parse_cwl_yaml_simple(cwl_path)
    
    def _parse_cwl_yaml_simple(self, cwl_path: str) -> Dict[str, Any]:
        """Simple YAML parsing fallback when cwltool is not available."""
        try:
            with open(cwl_path, 'r') as f:
                if RUAMEL_YAML_AVAILABLE and self.yaml_loader:
                    workflow_data = self.yaml_loader.load(f)
                else:
                    workflow_data = yaml.safe_load(f)
            
            # Ensure required fields exist
            if not isinstance(workflow_data, dict):
                raise ValueError("CWL file must contain a YAML dictionary")
            
            # Set defaults for missing fields
            workflow_data.setdefault("cwlVersion", "v1.0")
            workflow_data.setdefault("class", "Workflow")
            workflow_data.setdefault("id", Path(cwl_path).stem)
            workflow_data.setdefault("inputs", {})
            workflow_data.setdefault("outputs", {})
            workflow_data.setdefault("steps", {})
            workflow_data.setdefault("requirements", [])
            workflow_data.setdefault("hints", [])
            
            return workflow_data
            
        except Exception as e:
            logger.error(f"Failed to parse CWL file as YAML: {str(e)}")
            raise
    
    def extract_components(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and organize workflow components for Nextflow conversion.
        
        Args:
            workflow_data: Parsed CWL workflow data
            
        Returns:
            Dictionary with organized workflow components
        """
        logger.info("Extracting workflow components")
        
        components = {
            "workflow_info": {
                "name": workflow_data.get("id", "unnamed_workflow"),
                "version": workflow_data.get("cwlVersion", "v1.0"),
                "description": workflow_data.get("doc", ""),
                "label": workflow_data.get("label", "")
            },
            "inputs": self._process_inputs(workflow_data.get("inputs", {})),
            "outputs": self._process_outputs(workflow_data.get("outputs", {})),
            "processes": self._process_steps(workflow_data.get("steps", {})),
            "requirements": self._process_requirements(workflow_data.get("requirements", [])),
            "hints": self._process_hints(workflow_data.get("hints", [])),
            "dependencies": self._extract_dependencies(workflow_data)
        }
        
        logger.info(f"Extracted {len(components['processes'])} processes")
        return components
    
    def _extract_inputs(self, tool) -> Dict[str, Any]:
        """Extract input definitions from CWL tool."""
        inputs = {}
        if hasattr(tool, 'inputs') and tool.inputs:
            for input_def in tool.inputs:
                inputs[input_def.name] = {
                    "type": str(input_def.type),
                    "label": getattr(input_def, "label", ""),
                    "doc": getattr(input_def, "doc", ""),
                    "default": getattr(input_def, "default", None),
                    "inputBinding": getattr(input_def, "inputBinding", None)
                }
        return inputs
    
    def _extract_outputs(self, tool) -> Dict[str, Any]:
        """Extract output definitions from CWL tool."""
        outputs = {}
        if hasattr(tool, 'outputs') and tool.outputs:
            for output_def in tool.outputs:
                outputs[output_def.name] = {
                    "type": str(output_def.type),
                    "label": getattr(output_def, "label", ""),
                    "doc": getattr(output_def, "doc", ""),
                    "outputBinding": getattr(output_def, "outputBinding", None)
                }
        return outputs
    
    def _extract_steps(self, tool) -> Dict[str, Any]:
        """Extract step definitions from CWL workflow."""
        steps = {}
        if hasattr(tool, 'steps') and tool.steps:
            for step in tool.steps:
                steps[step.id] = {
                    "run": getattr(step, "run", ""),
                    "in": self._extract_step_inputs(step),
                    "out": self._extract_step_outputs(step),
                    "requirements": getattr(step, "requirements", []),
                    "hints": getattr(step, "hints", []),
                    "scatter": getattr(step, "scatter", None),
                    "scatterMethod": getattr(step, "scatterMethod", None)
                }
        return steps
    
    def _extract_step_inputs(self, step) -> Dict[str, Any]:
        """Extract input mappings for a workflow step."""
        inputs = {}
        if hasattr(step, 'in_') and step.in_:
            for input_mapping in step.in_:
                inputs[input_mapping.id] = {
                    "source": getattr(input_mapping, "source", ""),
                    "valueFrom": getattr(input_mapping, "valueFrom", None),
                    "linkMerge": getattr(input_mapping, "linkMerge", None)
                }
        return inputs
    
    def _extract_step_outputs(self, step) -> List[str]:
        """Extract output names for a workflow step."""
        outputs = []
        if hasattr(step, 'out') and step.out:
            outputs = [str(out) for out in step.out]
        return outputs
    
    def _extract_requirements(self, tool) -> List[Dict[str, Any]]:
        """Extract requirements from CWL tool."""
        requirements = []
        if hasattr(tool, 'requirements') and tool.requirements:
            for req in tool.requirements:
                req_dict = {"class": req.class_}
                # Add requirement-specific fields
                for attr in dir(req):
                    if not attr.startswith('_') and attr != 'class_':
                        value = getattr(req, attr, None)
                        if value is not None:
                            req_dict[attr] = value
                requirements.append(req_dict)
        return requirements
    
    def _extract_hints(self, tool) -> List[Dict[str, Any]]:
        """Extract hints from CWL tool."""
        hints = []
        if hasattr(tool, 'hints') and tool.hints:
            for hint in tool.hints:
                hint_dict = {"class": hint.class_}
                # Add hint-specific fields
                for attr in dir(hint):
                    if not attr.startswith('_') and attr != 'class_':
                        value = getattr(hint, attr, None)
                        if value is not None:
                            hint_dict[attr] = value
                hints.append(hint_dict)
        return hints
    
    def _extract_metadata(self, tool) -> Dict[str, Any]:
        """Extract metadata from CWL tool."""
        metadata = {}
        metadata_fields = ['id', 'label', 'doc', 'cwlVersion', 'baseCommand', 'arguments']
        
        for field in metadata_fields:
            if hasattr(tool, field):
                value = getattr(tool, field)
                if value is not None:
                    metadata[field] = value
        
        return metadata
    
    def _process_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process and normalize input definitions."""
        processed_inputs = {}
        
        for input_name, input_def in inputs.items():
            processed_inputs[input_name] = {
                "name": input_name,
                "type": self._normalize_type(input_def.get("type", "string")),
                "description": input_def.get("doc", ""),
                "default": input_def.get("default"),
                "required": input_def.get("default") is None,
                "input_binding": input_def.get("inputBinding")
            }
        
        return processed_inputs
    
    def _process_outputs(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process and normalize output definitions."""
        processed_outputs = {}
        
        for output_name, output_def in outputs.items():
            processed_outputs[output_name] = {
                "name": output_name,
                "type": self._normalize_type(output_def.get("type", "File")),
                "description": output_def.get("doc", ""),
                "output_binding": output_def.get("outputBinding")
            }
        
        return processed_outputs
    
    def _process_steps(self, steps: Dict[str, Any]) -> Dict[str, Any]:
        """Process and normalize step definitions."""
        processed_steps = {}
        
        for step_name, step_def in steps.items():
            processed_steps[step_name] = {
                "name": step_name,
                "tool": step_def.get("run", ""),
                "inputs": step_def.get("in", {}),
                "outputs": step_def.get("out", []),
                "requirements": step_def.get("requirements", []),
                "hints": step_def.get("hints", []),
                "scatter": step_def.get("scatter"),
                "scatter_method": step_def.get("scatterMethod")
            }
        
        return processed_steps
    
    def _process_requirements(self, requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process and categorize requirements."""
        processed_reqs = {
            "docker": [],
            "software": [],
            "resource": [],
            "other": []
        }
        
        for req in requirements:
            req_class = req.get("class", "").lower()
            
            if "docker" in req_class:
                processed_reqs["docker"].append(req)
            elif "software" in req_class:
                processed_reqs["software"].append(req)
            elif "resource" in req_class:
                processed_reqs["resource"].append(req)
            else:
                processed_reqs["other"].append(req)
        
        return processed_reqs
    
    def _process_hints(self, hints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process and categorize hints."""
        processed_hints = {
            "docker": [],
            "resource": [],
            "other": []
        }
        
        for hint in hints:
            hint_class = hint.get("class", "").lower()
            
            if "docker" in hint_class:
                processed_hints["docker"].append(hint)
            elif "resource" in hint_class:
                processed_hints["resource"].append(hint)
            else:
                processed_hints["other"].append(hint)
        
        return processed_hints
    
    def _extract_dependencies(self, workflow_data: Dict[str, Any]) -> List[str]:
        """Extract workflow dependencies."""
        dependencies = []
        
        # Extract from steps
        for step_name, step_def in workflow_data.get("steps", {}).items():
            tool_path = step_def.get("run", "")
            if tool_path and tool_path not in dependencies:
                dependencies.append(tool_path)
        
        return dependencies
    
    def _normalize_type(self, cwl_type: Union[str, Dict, List]) -> str:
        """Normalize CWL type to a simple string representation."""
        if isinstance(cwl_type, str):
            return cwl_type
        elif isinstance(cwl_type, dict):
            if "type" in cwl_type:
                return cwl_type["type"]
            elif "items" in cwl_type:
                return f"array<{self._normalize_type(cwl_type['items'])}>"
            else:
                return "object"
        elif isinstance(cwl_type, list):
            if len(cwl_type) == 1:
                return self._normalize_type(cwl_type[0])
            else:
                return "union"
        else:
            return "unknown"

