# CWL to AWS HealthOmics Nextflow Migration Toolkit

A comprehensive toolkit for migrating Common Workflow Language (CWL) workflows from SevenBridges to AWS HealthOmics Nextflow pipelines.

## Overview

This toolkit provides automated conversion capabilities to migrate CWL workflows to Nextflow format optimized for AWS HealthOmics, including:

- **CWL Parser**: Extracts workflow definitions, tools, and dependencies
- **Nextflow Generator**: Creates Nextflow pipelines with AWS HealthOmics integration
- **Resource Mapping**: Converts CWL resource requirements to AWS-compatible formats
- **Container Integration**: Handles Docker/Singularity container specifications
- **Parameter Translation**: Maps CWL parameters to Nextflow parameters
- **Validation Tools**: Ensures converted workflows are syntactically correct

## Features

- ✅ **Automated CWL Parsing**: Supports CWL v1.0, v1.1, and v1.2
- ✅ **Nextflow Generation**: Creates optimized Nextflow pipelines
- ✅ **AWS HealthOmics Integration**: Native support for AWS HealthOmics features
- ✅ **Container Support**: Docker and Singularity container handling
- ✅ **Resource Optimization**: AWS-specific resource allocation
- ✅ **Parameter Mapping**: Intelligent parameter translation
- ✅ **Validation Suite**: Comprehensive testing and validation
- ✅ **Example Workflows**: Pre-built examples for common bioinformatics tasks

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+ (for CWL reference implementation)
- Docker
- AWS CLI configured
- Nextflow installed

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd cwl-to-nexflow

# Install dependencies
pip install -r requirements.txt
npm install

# Setup AWS HealthOmics
./setup/configure_aws_healthomics.sh
```

### Basic Usage

```bash
# Convert a CWL workflow
python cwl_to_nextflow.py --input workflow.cwl --output ./nextflow_workflows/

# Convert with AWS HealthOmics optimization
python cwl_to_nextflow.py --input workflow.cwl --output ./nextflow_workflows/ --aws-healthomics

# Validate converted workflow
python validate_nextflow.py --workflow ./nextflow_workflows/workflow.nf
```

## Project Structure

```
cwl-to-nexflow/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── package.json                 # Node.js dependencies
├── cwl_to_nextflow.py          # Main conversion script
├── validate_nextflow.py        # Validation utilities
├── setup/                      # Setup and configuration
│   ├── configure_aws_healthomics.sh
│   ├── install_dependencies.sh
│   └── setup_environment.py
├── src/                        # Core conversion modules
│   ├── cwl_parser.py          # CWL parsing logic
│   ├── nextflow_generator.py  # Nextflow generation
│   ├── aws_integration.py     # AWS HealthOmics integration
│   ├── resource_mapper.py     # Resource requirement mapping
│   └── container_handler.py   # Container specification handling
├── examples/                   # Example workflows
│   ├── cwl/                   # Original CWL workflows
│   ├── nextflow/              # Converted Nextflow workflows
│   └── test_data/             # Test datasets
├── templates/                  # Nextflow templates
│   ├── base_template.nf
│   ├── aws_healthomics_template.nf
│   └── container_template.nf
├── tests/                      # Test suite
│   ├── test_cwl_parser.py
│   ├── test_nextflow_generator.py
│   └── test_aws_integration.py
├── docs/                       # Documentation
│   ├── migration_guide.md
│   ├── aws_healthomics_setup.md
│   └── troubleshooting.md
└── demos/                      # Demo scripts
    ├── basic_conversion.py
    ├── aws_healthomics_demo.py
    └── batch_conversion.py
```

## Migration Process

### 1. CWL Analysis
- Parse CWL workflow definitions
- Extract tool specifications
- Identify dependencies and requirements
- Map input/output parameters

### 2. Nextflow Generation
- Create Nextflow pipeline structure
- Generate process definitions
- Implement workflow logic
- Add error handling and logging

### 3. AWS HealthOmics Integration
- Configure AWS-specific parameters
- Set up container registries
- Map resource requirements
- Enable monitoring and logging

### 4. Validation and Testing
- Syntax validation
- Functional testing
- Performance benchmarking
- AWS HealthOmics compatibility check

## Example Workflows

### Basic RNA-seq Analysis
- **CWL**: `examples/cwl/rnaseq_analysis.cwl`
- **Nextflow**: `examples/nextflow/rnaseq_analysis.nf`

### Variant Calling Pipeline
- **CWL**: `examples/cwl/variant_calling.cwl`
- **Nextflow**: `examples/nextflow/variant_calling.nf`

### Multi-sample Analysis
- **CWL**: `examples/cwl/multisample_analysis.cwl`
- **Nextflow**: `examples/nextflow/multisample_analysis.nf`

## Configuration

### AWS HealthOmics Setup

1. Configure AWS credentials:
```bash
aws configure
```

2. Set up HealthOmics service:
```bash
./setup/configure_aws_healthomics.sh
```

3. Configure container registry:
```bash
aws ecr create-repository --repository-name healthomics-workflows
```

### Environment Variables

```bash
export AWS_DEFAULT_REGION=us-east-1
export AWS_HEALTHOMICS_WORKGROUP=default
export AWS_HEALTHOMICS_ROLE=HealthOmicsExecutionRole
export CONTAINER_REGISTRY=your-account.dkr.ecr.us-east-1.amazonaws.com
```

## Advanced Usage

### Batch Conversion

```bash
# Convert multiple workflows
python batch_converter.py --input-dir ./cwl_workflows/ --output-dir ./nextflow_workflows/
```

### Custom Templates

```bash
# Use custom Nextflow template
python cwl_to_nextflow.py --input workflow.cwl --template ./custom_template.nf
```

### Resource Optimization

```bash
# Optimize for specific AWS instance types
python cwl_to_nextflow.py --input workflow.cwl --instance-type m5.large --optimize-resources
```

## Troubleshooting

### Common Issues

1. **Container Registry Access**: Ensure ECR permissions are configured
2. **Resource Limits**: Check AWS HealthOmics resource quotas
3. **Parameter Mapping**: Verify CWL parameter types are supported
4. **Dependencies**: Ensure all required tools are containerized

### Debug Mode

```bash
# Enable verbose logging
python cwl_to_nextflow.py --input workflow.cwl --debug --log-level DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@example.com

## Acknowledgments

- SevenBridges for CWL workflow examples
- AWS HealthOmics team for platform support
- Nextflow community for framework development
- Bioinformatics community for workflow contributions

