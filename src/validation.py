"""
Validation Module

Validates generated Nextflow workflows and provides quality checks.
"""

import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class WorkflowValidator:
    """Validates Nextflow workflows and provides quality checks."""
    
    def __init__(self):
        """Initialize the workflow validator."""
        self.nextflow_syntax_patterns = {
            "process": r'^process\s+\w+\s*\{',
            "workflow": r'^workflow\s+\w*\s*\{',
            "channel": r'^Channel\.',
            "params": r'^params\.',
            "include": r'^include\s+',
            "import": r'^import\s+'
        }
        
        self.validation_rules = {
            "syntax": self._validate_syntax,
            "structure": self._validate_structure,
            "processes": self._validate_processes,
            "workflow": self._validate_workflow,
            "parameters": self._validate_parameters,
            "containers": self._validate_containers,
            "aws_healthomics": self._validate_aws_healthomics
        }
    
    def validate_nextflow(self, nextflow_content: str) -> Dict[str, Any]:
        """
        Validate a Nextflow workflow.
        
        Args:
            nextflow_content: Nextflow workflow content
            
        Returns:
            Dictionary with validation results
        """
        logger.info("Validating Nextflow workflow")
        
        validation_results = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "scores": {},
            "details": {}
        }
        
        # Run all validation rules
        for rule_name, validator in self.validation_rules.items():
            try:
                rule_results = validator(nextflow_content)
                validation_results["details"][rule_name] = rule_results
                
                # Aggregate issues
                if rule_results.get("issues"):
                    validation_results["issues"].extend(rule_results["issues"])
                
                if rule_results.get("warnings"):
                    validation_results["warnings"].extend(rule_results["warnings"])
                
                if rule_results.get("recommendations"):
                    validation_results["recommendations"].extend(rule_results["recommendations"])
                
                # Calculate scores
                validation_results["scores"][rule_name] = rule_results.get("score", 0)
                
            except Exception as e:
                logger.error(f"Validation rule '{rule_name}' failed: {e}")
                validation_results["issues"].append(f"Validation error in {rule_name}: {str(e)}")
        
        # Determine overall validity
        validation_results["valid"] = len(validation_results["issues"]) == 0
        
        # Calculate overall score
        if validation_results["scores"]:
            validation_results["overall_score"] = sum(validation_results["scores"].values()) / len(validation_results["scores"])
        else:
            validation_results["overall_score"] = 0
        
        logger.info(f"Validation completed. Valid: {validation_results['valid']}, Score: {validation_results['overall_score']:.2f}")
        
        return validation_results
    
    def _validate_syntax(self, content: str) -> Dict[str, Any]:
        """Validate Nextflow syntax."""
        
        results = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "score": 0
        }
        
        lines = content.split('\n')
        issues_count = 0
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('//'):
                continue
            
            # Check for basic syntax issues
            if self._has_syntax_issues(line):
                results["issues"].append(f"Line {line_num}: Syntax issue - {line}")
                issues_count += 1
        
        # Calculate score
        total_lines = len([l for l in lines if l.strip() and not l.strip().startswith('//')])
        if total_lines > 0:
            results["score"] = max(0, (total_lines - issues_count) / total_lines * 100)
        
        results["valid"] = issues_count == 0
        
        return results
    
    def _validate_structure(self, content: str) -> Dict[str, Any]:
        """Validate Nextflow workflow structure."""
        
        results = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "score": 0,
            "structure": {}
        }
        
        # Check for required components
        has_processes = bool(re.search(r'^process\s+\w+', content, re.MULTILINE))
        has_workflow = bool(re.search(r'^workflow\s+', content, re.MULTILINE))
        has_params = bool(re.search(r'^params\.', content, re.MULTILINE))
        
        results["structure"] = {
            "has_processes": has_processes,
            "has_workflow": has_workflow,
            "has_params": has_params
        }
        
        # Validate structure
        if not has_processes:
            results["issues"].append("No processes defined")
        
        if not has_workflow:
            results["warnings"].append("No workflow definition found")
        
        if not has_params:
            results["warnings"].append("No parameters defined")
        
        # Calculate score
        score = 0
        if has_processes:
            score += 50
        if has_workflow:
            score += 30
        if has_params:
            score += 20
        
        results["score"] = score
        results["valid"] = len(results["issues"]) == 0
        
        return results
    
    def _validate_processes(self, content: str) -> Dict[str, Any]:
        """Validate Nextflow processes."""
        
        results = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "score": 0,
            "processes": []
        }
        
        # Extract process definitions
        process_pattern = r'^process\s+(\w+)\s*\{([^}]+)\}'
        processes = re.findall(process_pattern, content, re.MULTILINE | re.DOTALL)
        
        for process_name, process_body in processes:
            process_info = {
                "name": process_name,
                "has_input": bool(re.search(r'input:', process_body)),
                "has_output": bool(re.search(r'output:', process_body)),
                "has_script": bool(re.search(r'script:', process_body)),
                "has_container": bool(re.search(r'container:', process_body))
            }
            
            results["processes"].append(process_info)
            
            # Validate process
            if not process_info["has_input"]:
                results["warnings"].append(f"Process '{process_name}' has no input defined")
            
            if not process_info["has_output"]:
                results["warnings"].append(f"Process '{process_name}' has no output defined")
            
            if not process_info["has_script"]:
                results["issues"].append(f"Process '{process_name}' has no script defined")
            
            if not process_info["has_container"]:
                results["warnings"].append(f"Process '{process_name}' has no container defined")
        
        # Calculate score
        if processes:
            total_checks = len(processes) * 4  # 4 checks per process
            passed_checks = sum(
                sum(1 for v in process_info.values() if isinstance(v, bool) and v)
                for process_info in results["processes"]
            )
            results["score"] = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        results["valid"] = len(results["issues"]) == 0
        
        return results
    
    def _validate_workflow(self, content: str) -> Dict[str, Any]:
        """Validate workflow definition."""
        
        results = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "score": 0
        }
        
        # Check for workflow definition
        workflow_match = re.search(r'^workflow\s+(\w*)\s*\{([^}]+)\}', content, re.MULTILINE | re.DOTALL)
        
        if not workflow_match:
            results["warnings"].append("No workflow definition found")
            results["score"] = 0
            return results
        
        workflow_body = workflow_match.group(2)
        
        # Check for process calls
        process_calls = re.findall(r'(\w+)\s*\(', workflow_body)
        
        if not process_calls:
            results["warnings"].append("Workflow has no process calls")
            results["score"] = 20
        else:
            results["score"] = min(100, len(process_calls) * 20)
        
        # Check for output definitions
        if re.search(r'output:', workflow_body):
            results["score"] += 20
        
        results["valid"] = len(results["issues"]) == 0
        
        return results
    
    def _validate_parameters(self, content: str) -> Dict[str, Any]:
        """Validate parameter definitions."""
        
        results = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "score": 0,
            "parameters": []
        }
        
        # Extract parameter definitions
        param_pattern = r'^params\.(\w+)\s*='
        params = re.findall(param_pattern, content, re.MULTILINE)
        
        results["parameters"] = params
        
        if not params:
            results["warnings"].append("No parameters defined")
            results["score"] = 0
        else:
            results["score"] = min(100, len(params) * 25)
        
        results["valid"] = len(results["issues"]) == 0
        
        return results
    
    def _validate_containers(self, content: str) -> Dict[str, Any]:
        """Validate container specifications."""
        
        results = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "score": 0,
            "containers": []
        }
        
        # Extract container specifications
        container_pattern = r'container\s*[\'"]([^\'"]+)[\'"]'
        containers = re.findall(container_pattern, content)
        
        results["containers"] = containers
        
        if not containers:
            results["warnings"].append("No container specifications found")
            results["score"] = 0
        else:
            # Check for AWS-optimized containers
            aws_containers = [c for c in containers if 'ecr.aws' in c or 'public.ecr.aws' in c]
            
            if aws_containers:
                results["score"] = 100
            else:
                results["warnings"].append("No AWS-optimized containers found")
                results["score"] = 50
        
        results["valid"] = len(results["issues"]) == 0
        
        return results
    
    def _validate_aws_healthomics(self, content: str) -> Dict[str, Any]:
        """Validate AWS HealthOmics specific features."""
        
        results = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "score": 0,
            "features": {}
        }
        
        # Check for AWS HealthOmics features
        features = {
            "aws_batch": bool(re.search(r'executor\s*=\s*[\'"]awsbatch[\'"]', content)),
            "aws_region": bool(re.search(r'aws\s*\{[^}]*region', content, re.DOTALL)),
            "healthomics_config": bool(re.search(r'healthomics\s*\{', content)),
            "cloudwatch_logging": bool(re.search(r'cloudwatch|monitoring', content, re.IGNORECASE)),
            "s3_output": bool(re.search(r's3://', content))
        }
        
        results["features"] = features
        
        # Calculate score based on features
        feature_count = sum(features.values())
        results["score"] = (feature_count / len(features)) * 100
        
        if not features["aws_batch"]:
            results["warnings"].append("AWS Batch executor not configured")
        
        if not features["aws_region"]:
            results["warnings"].append("AWS region not specified")
        
        results["valid"] = len(results["issues"]) == 0
        
        return results
    
    def _has_syntax_issues(self, line: str) -> bool:
        """Check if a line has syntax issues."""
        
        # Basic syntax checks
        if line.count('{') != line.count('}'):
            return True
        
        if line.count('(') != line.count(')'):
            return True
        
        if line.count('[') != line.count(']'):
            return True
        
        # Check for common syntax errors
        if re.search(r'[{}]\s*[{}]', line):  # Adjacent braces
            return True
        
        if re.search(r';\s*;', line):  # Double semicolons
            return True
        
        return False
    
    def validate_with_nextflow(self, nextflow_file: str) -> Dict[str, Any]:
        """Validate using Nextflow's built-in validation."""
        
        results = {
            "valid": False,
            "output": "",
            "error": "",
            "exit_code": -1
        }
        
        try:
            # Run nextflow config to validate syntax
            cmd = ["nextflow", "config", nextflow_file]
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            results["exit_code"] = result.returncode
            results["output"] = result.stdout
            results["error"] = result.stderr
            results["valid"] = result.returncode == 0
            
        except subprocess.TimeoutExpired:
            results["error"] = "Validation timed out"
        except FileNotFoundError:
            results["error"] = "Nextflow not found in PATH"
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate a human-readable validation report."""
        
        report = ["Nextflow Workflow Validation Report", "=" * 50, ""]
        
        # Overall status
        status = "✅ VALID" if validation_results["valid"] else "❌ INVALID"
        report.append(f"Overall Status: {status}")
        report.append(f"Overall Score: {validation_results.get('overall_score', 0):.1f}/100")
        report.append("")
        
        # Issues
        if validation_results["issues"]:
            report.append("Issues:")
            for issue in validation_results["issues"]:
                report.append(f"  ❌ {issue}")
            report.append("")
        
        # Warnings
        if validation_results["warnings"]:
            report.append("Warnings:")
            for warning in validation_results["warnings"]:
                report.append(f"  ⚠️  {warning}")
            report.append("")
        
        # Recommendations
        if validation_results["recommendations"]:
            report.append("Recommendations:")
            for rec in validation_results["recommendations"]:
                report.append(f"  💡 {rec}")
            report.append("")
        
        # Detailed scores
        if validation_results["scores"]:
            report.append("Detailed Scores:")
            for rule, score in validation_results["scores"].items():
                report.append(f"  {rule}: {score:.1f}/100")
            report.append("")
        
        return "\n".join(report)

