"""
CWL to Nextflow Migration Toolkit

Core modules for converting Common Workflow Language workflows to Nextflow pipelines
optimized for AWS HealthOmics.
"""

__version__ = "1.0.0"
__author__ = "CWL to Nextflow Migration Team"
__email__ = "support@example.com"

from .cwl_parser import CWLParser
from .nextflow_generator import NextflowGenerator
from .aws_integration import AWSHealthOmicsIntegration
from .resource_mapper import ResourceMapper
from .container_handler import ContainerHandler
from .validation import WorkflowValidator

__all__ = [
    "CWLParser",
    "NextflowGenerator", 
    "AWSHealthOmicsIntegration",
    "ResourceMapper",
    "ContainerHandler",
    "WorkflowValidator"
]

