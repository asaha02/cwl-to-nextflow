# CWL to Nextflow Migration Guide

This guide provides detailed instructions for migrating Common Workflow Language (CWL) workflows to Nextflow pipelines optimized for AWS HealthOmics.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Basic Migration](#basic-migration)
5. [Advanced Features](#advanced-features)
6. [AWS HealthOmics Integration](#aws-healthomics-integration)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Overview

The CWL to Nextflow migration toolkit provides automated conversion capabilities to migrate CWL workflows to Nextflow format optimized for AWS HealthOmics. The migration process includes:

- **CWL Parsing**: Extracts workflow definitions, tools, and dependencies
- **Nextflow Generation**: Creates Nextflow pipelines with AWS HealthOmics integration
- **Resource Mapping**: Converts CWL resource requirements to AWS-compatible formats
- **Container Integration**: Handles Docker/Singularity container specifications
- **Parameter Translation**: Maps CWL parameters to Nextflow parameters
- **Validation**: Ensures converted workflows are syntactically correct

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows with WSL
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **Docker**: 20.0 or higher
- **Nextflow**: 22.0 or higher
- **AWS CLI**: 2.0 or higher (for AWS HealthOmics integration)

### AWS Requirements

- AWS account with appropriate permissions
- AWS HealthOmics service access
- S3 bucket for workflow outputs
- IAM role with HealthOmics execution permissions
- ECR repository for container images

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd cwl-to-nexflow
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Install CWL reference implementation
npm install -g cwltool
```

### 3. Setup Environment

```bash
# Run setup script
./setup/install_dependencies.sh

# Activate environment
source activate_env.sh
```

### 4. Configure AWS HealthOmics

```bash
# Configure AWS credentials
aws configure

# Setup HealthOmics environment
./setup/configure_aws_healthomics.sh
```

## Basic Migration

### Single Workflow Conversion

```bash
# Basic conversion
python cwl_to_nextflow.py --input workflow.cwl --output ./nextflow_workflows/

# With AWS HealthOmics optimization
python cwl_to_nextflow.py --input workflow.cwl --output ./nextflow_workflows/ --aws-healthomics

# With resource optimization
python cwl_to_nextflow.py --input workflow.cwl --output ./nextflow_workflows/ --optimize-resources --instance-type m5.large
```

### Batch Conversion

```bash
# Convert multiple workflows
python batch_converter.py --input-dir ./cwl_workflows/ --output-dir ./nextflow_workflows/

# With AWS HealthOmics optimization
python batch_converter.py --input-dir ./cwl_workflows/ --output-dir ./nextflow_workflows/ --aws-healthomics
```

### Validation

```bash
# Validate single workflow
python validate_nextflow.py --workflow ./nextflow_workflows/workflow.nf

# Validate directory of workflows
python validate_nextflow.py --directory ./nextflow_workflows/

# Generate validation report
python validate_nextflow.py --workflow ./nextflow_workflows/workflow.nf --output validation_report.txt
```

## Advanced Features

### Custom Templates

Create custom Nextflow templates for specific use cases:

```bash
# Use custom template
python cwl_to_nextflow.py --input workflow.cwl --template ./custom_template.nf
```

### Resource Optimization

Optimize resource requirements for specific AWS instance types:

```bash
# Optimize for specific instance type
python cwl_to_nextflow.py --input workflow.cwl --instance-type c5.2xlarge --optimize-resources
```

### Container Registry Mapping

The toolkit automatically maps common container registries to AWS ECR:

- `docker.io` → `public.ecr.aws`
- `quay.io` → `public.ecr.aws`
- `gcr.io` → `public.ecr.aws`

### Parameter Mapping

CWL parameters are automatically mapped to Nextflow parameters:

| CWL Type | Nextflow Type |
|----------|---------------|
| `string` | `string` |
| `int` | `integer` |
| `float` | `float` |
| `boolean` | `boolean` |
| `File` | `file` |
| `Directory` | `directory` |
| `array` | `array` |

## AWS HealthOmics Integration

### Configuration

The toolkit generates AWS HealthOmics optimized configurations:

```nextflow
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
```

### Execution Profiles

Three execution profiles are generated:

1. **healthomics-dev**: Development and testing
   - 1 CPU, 2 GB memory, 1 hour time limit

2. **healthomics**: Standard analysis
   - 2 CPUs, 4 GB memory, 2 hour time limit

3. **healthomics-prod**: Production workloads
   - 4 CPUs, 16 GB memory, 8 hour time limit

### Monitoring and Logging

HealthOmics integration includes:

- CloudWatch logging
- Process monitoring
- Error handling and retry logic
- Resource usage tracking

### Deployment

Deploy converted workflows to AWS HealthOmics:

```bash
# Create workflow in HealthOmics
aws omics create-workflow \
    --name "converted-workflow" \
    --description "Converted from CWL" \
    --definition-language NEXTFLOW \
    --definition file://workflow.nf

# Run workflow
aws omics start-run \
    --workflow-id "workflow-123" \
    --role-arn "arn:aws:iam::ACCOUNT:role/HealthOmicsExecutionRole" \
    --output-uri "s3://bucket/outputs/"
```

## Troubleshooting

### Common Issues

#### 1. CWL Parsing Errors

**Problem**: CWL workflow cannot be parsed
**Solution**: 
- Validate CWL syntax with `cwltool --validate workflow.cwl`
- Check CWL version compatibility
- Ensure all referenced tools are available

#### 2. Container Registry Issues

**Problem**: Container images not found
**Solution**:
- Verify container images exist
- Check ECR permissions
- Use AWS-optimized containers

#### 3. Resource Mapping Issues

**Problem**: Resource requirements not properly mapped
**Solution**:
- Check CWL resource requirements syntax
- Verify AWS instance type compatibility
- Review resource optimization settings

#### 4. AWS HealthOmics Setup Issues

**Problem**: HealthOmics integration fails
**Solution**:
- Verify AWS credentials and permissions
- Check HealthOmics workgroup configuration
- Ensure IAM role has required permissions

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
# Enable debug mode
python cwl_to_nextflow.py --input workflow.cwl --debug

# Check validation with verbose output
python validate_nextflow.py --workflow workflow.nf --verbose
```

### Validation Issues

Common validation issues and solutions:

1. **Missing process definitions**: Ensure all CWL steps have corresponding Nextflow processes
2. **Invalid parameter types**: Check CWL parameter type definitions
3. **Container specification errors**: Verify Docker image references
4. **Resource requirement issues**: Review CWL resource requirements

## Best Practices

### CWL Workflow Design

1. **Use standard CWL types**: Stick to well-supported CWL types
2. **Define clear inputs/outputs**: Provide detailed descriptions
3. **Specify resource requirements**: Include CPU, memory, and time requirements
4. **Use container specifications**: Always specify Docker containers
5. **Test locally first**: Validate CWL workflows before conversion

### Nextflow Optimization

1. **Use appropriate execution profiles**: Choose the right profile for your workload
2. **Optimize resource allocation**: Match resources to actual requirements
3. **Implement error handling**: Use retry logic and proper error strategies
4. **Monitor execution**: Enable logging and monitoring
5. **Test thoroughly**: Validate converted workflows before deployment

### AWS HealthOmics Best Practices

1. **Use ECR for containers**: Store containers in AWS ECR
2. **Optimize for AWS instances**: Choose appropriate instance types
3. **Implement proper IAM roles**: Use least-privilege access
4. **Monitor costs**: Track resource usage and costs
5. **Use S3 for data**: Store inputs and outputs in S3

### Migration Strategy

1. **Start with simple workflows**: Begin with basic workflows
2. **Test incrementally**: Convert and test one workflow at a time
3. **Validate thoroughly**: Use validation tools extensively
4. **Document changes**: Keep track of modifications made during conversion
5. **Plan for maintenance**: Establish processes for ongoing maintenance

### Performance Optimization

1. **Parallel execution**: Use Nextflow's parallel execution capabilities
2. **Resource optimization**: Match resources to actual needs
3. **Container optimization**: Use optimized container images
4. **Data management**: Implement efficient data transfer strategies
5. **Caching**: Use Nextflow's caching mechanisms

## Support and Resources

### Documentation

- [Nextflow Documentation](https://www.nextflow.io/docs/latest/)
- [AWS HealthOmics Documentation](https://docs.aws.amazon.com/healthomics/)
- [CWL Specification](https://www.commonwl.org/)

### Community

- [Nextflow Community](https://github.com/nextflow-io/nextflow)
- [CWL Community](https://github.com/common-workflow-language)
- [AWS HealthOmics Community](https://github.com/aws/aws-healthomics)

### Getting Help

1. Check the troubleshooting section above
2. Review validation reports for specific issues
3. Consult the documentation and community resources
4. Submit issues to the project repository

## Conclusion

The CWL to Nextflow migration toolkit provides a comprehensive solution for migrating CWL workflows to Nextflow pipelines optimized for AWS HealthOmics. By following this guide and best practices, you can successfully migrate your workflows and take advantage of the scalability and features offered by AWS HealthOmics.

Remember to test thoroughly, validate your converted workflows, and optimize for your specific use case. The toolkit provides extensive validation and optimization features to help ensure successful migrations.

