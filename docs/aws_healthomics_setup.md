# AWS HealthOmics Setup Guide

This guide provides detailed instructions for setting up AWS HealthOmics for CWL to Nextflow migration.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [AWS Account Setup](#aws-account-setup)
4. [IAM Configuration](#iam-configuration)
5. [HealthOmics Configuration](#healthomics-configuration)
6. [S3 Setup](#s3-setup)
7. [ECR Setup](#ecr-setup)
8. [AWS Batch Setup](#aws-batch-setup)
9. [Validation](#validation)
10. [Troubleshooting](#troubleshooting)

## Overview

AWS HealthOmics is a fully managed service for analyzing genomic, transcriptomic, and other omics data. This guide covers the complete setup process for using HealthOmics with converted Nextflow workflows.

## Prerequisites

### AWS Account Requirements

- AWS account with administrative access
- AWS CLI installed and configured
- Appropriate AWS service quotas
- Billing enabled for AWS services

### Required AWS Services

- AWS HealthOmics
- AWS Batch
- Amazon S3
- Amazon ECR
- AWS IAM
- Amazon CloudWatch

## AWS Account Setup

### 1. Enable Required Services

```bash
# Enable HealthOmics service
aws omics list-workgroups

# Enable Batch service
aws batch describe-compute-environments

# Enable ECR service
aws ecr describe-repositories
```

### 2. Check Service Quotas

```bash
# Check HealthOmics quotas
aws service-quotas get-service-quota \
    --service-code omics \
    --quota-code L-12345678

# Check Batch quotas
aws service-quotas get-service-quota \
    --service-code batch \
    --quota-code L-12345678
```

### 3. Request Quota Increases (if needed)

```bash
# Request quota increase for HealthOmics
aws service-quotas request-service-quota-increase \
    --service-code omics \
    --quota-code L-12345678 \
    --desired-value 100

# Request quota increase for Batch
aws service-quotas request-service-quota-increase \
    --service-code batch \
    --quota-code L-12345678 \
    --desired-value 50
```

## IAM Configuration

### 1. Create HealthOmics Execution Role

Create a trust policy file `healthomics-trust-policy.json`:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "omics.amazonaws.com",
                    "batch.amazonaws.com"
                ]
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

Create the IAM role:

```bash
# Create the role
aws iam create-role \
    --role-name HealthOmicsExecutionRole \
    --assume-role-policy-document file://healthomics-trust-policy.json

# Attach required policies
aws iam attach-role-policy \
    --role-name HealthOmicsExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonHealthOmicsFullAccess

aws iam attach-role-policy \
    --role-name HealthOmicsExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
    --role-name HealthOmicsExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/AWSBatchFullAccess

aws iam attach-role-policy \
    --role-name HealthOmicsExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
```

### 2. Create Custom Policy (Optional)

Create a custom policy for more restrictive permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "omics:CreateWorkflow",
                "omics:GetWorkflow",
                "omics:ListWorkflows",
                "omics:DeleteWorkflow",
                "omics:CreateRun",
                "omics:GetRun",
                "omics:ListRuns",
                "omics:CancelRun",
                "omics:GetWorkgroup",
                "omics:ListWorkgroups"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "batch:SubmitJob",
                "batch:DescribeJobs",
                "batch:ListJobs",
                "batch:CancelJob",
                "batch:DescribeJobQueues",
                "batch:DescribeComputeEnvironments"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-healthomics-bucket",
                "arn:aws:s3:::your-healthomics-bucket/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage"
            ],
            "Resource": "*"
        }
    ]
}
```

### 3. Create User for HealthOmics (Optional)

```bash
# Create IAM user
aws iam create-user --user-name healthomics-user

# Create access key
aws iam create-access-key --user-name healthomics-user

# Attach policies
aws iam attach-user-policy \
    --user-name healthomics-user \
    --policy-arn arn:aws:iam::aws:policy/AmazonHealthOmicsFullAccess
```

## HealthOmics Configuration

### 1. Create Workgroup

```bash
# Create HealthOmics workgroup
aws omics create-workgroup \
    --name "default" \
    --description "Default workgroup for CWL to Nextflow migration" \
    --max-cpus 100 \
    --max-duration 1440 \
    --max-runs 50
```

### 2. Configure Workgroup Settings

```bash
# Update workgroup settings
aws omics update-workgroup \
    --name "default" \
    --max-cpus 200 \
    --max-duration 2880 \
    --max-runs 100
```

### 3. List Workgroups

```bash
# List all workgroups
aws omics list-workgroups

# Get workgroup details
aws omics get-workgroup --name "default"
```

## S3 Setup

### 1. Create S3 Bucket

```bash
# Create S3 bucket for HealthOmics
aws s3 mb s3://your-healthomics-bucket

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket your-healthomics-bucket \
    --versioning-configuration Status=Enabled

# Enable server-side encryption
aws s3api put-bucket-encryption \
    --bucket your-healthomics-bucket \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }
        ]
    }'
```

### 2. Create Bucket Structure

```bash
# Create directory structure
aws s3api put-object --bucket your-healthomics-bucket --key inputs/
aws s3api put-object --bucket your-healthomics-bucket --key outputs/
aws s3api put-object --bucket your-healthomics-bucket --key logs/
aws s3api put-object --bucket your-healthomics-bucket --key work/
aws s3api put-object --bucket your-healthomics-bucket --key results/
```

### 3. Configure Bucket Policy

Create bucket policy `healthomics-bucket-policy.json`:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "HealthOmicsAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::YOUR_ACCOUNT_ID:role/HealthOmicsExecutionRole"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-healthomics-bucket",
                "arn:aws:s3:::your-healthomics-bucket/*"
            ]
        }
    ]
}
```

Apply the policy:

```bash
aws s3api put-bucket-policy \
    --bucket your-healthomics-bucket \
    --policy file://healthomics-bucket-policy.json
```

## ECR Setup

### 1. Create ECR Repository

```bash
# Create ECR repository
aws ecr create-repository \
    --repository-name healthomics-workflows \
    --image-scanning-configuration scanOnPush=true

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

### 2. Push Container Images

```bash
# Tag and push images
docker tag your-image:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/healthomics-workflows:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/healthomics-workflows:latest
```

### 3. Configure ECR Permissions

```bash
# Create ECR repository policy
aws ecr set-repository-policy \
    --repository-name healthomics-workflows \
    --policy-text '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "HealthOmicsECRAccess",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::YOUR_ACCOUNT_ID:role/HealthOmicsExecutionRole"
                },
                "Action": [
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ecr:BatchCheckLayerAvailability"
                ]
            }
        ]
    }'
```

## AWS Batch Setup

### 1. Create Service Role

```bash
# Create Batch service role
aws iam create-role \
    --role-name AWSServiceRoleForBatch \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "batch.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }'

# Attach Batch service role policy
aws iam attach-role-policy \
    --role-name AWSServiceRoleForBatch \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole
```

### 2. Create Instance Role

```bash
# Create Batch instance role
aws iam create-role \
    --role-name ecsInstanceRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }'

# Attach instance role policy
aws iam attach-role-policy \
    --role-name ecsInstanceRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role
```

### 3. Create Instance Profile

```bash
# Create instance profile
aws iam create-instance-profile --instance-profile-name ecsInstanceRole

# Add role to instance profile
aws iam add-role-to-instance-profile \
    --instance-profile-name ecsInstanceRole \
    --role-name ecsInstanceRole
```

### 4. Create Compute Environment

```bash
# Create compute environment
aws batch create-compute-environment \
    --compute-environment-name healthomics-compute-env \
    --type MANAGED \
    --state ENABLED \
    --service-role arn:aws:iam::YOUR_ACCOUNT_ID:role/AWSServiceRoleForBatch \
    --compute-resources '{
        "type": "EC2",
        "minvCpus": 0,
        "maxvCpus": 100,
        "desiredvCpus": 0,
        "instanceTypes": ["t3.small", "t3.medium", "t3.large", "m5.large", "m5.xlarge"],
        "subnets": ["subnet-12345678", "subnet-87654321"],
        "securityGroupIds": ["sg-12345678"],
        "instanceRole": "arn:aws:iam::YOUR_ACCOUNT_ID:instance-profile/ecsInstanceRole"
    }'
```

### 5. Create Job Queue

```bash
# Create job queue
aws batch create-job-queue \
    --job-queue-name healthomics-job-queue \
    --state ENABLED \
    --priority 1 \
    --compute-environment-order '[
        {
            "order": 1,
            "computeEnvironment": "healthomics-compute-env"
        }
    ]'
```

## Validation

### 1. Test HealthOmics Access

```bash
# Test workgroup access
aws omics get-workgroup --name "default"

# Test workflow creation
aws omics create-workflow \
    --name "test-workflow" \
    --description "Test workflow" \
    --definition-language NEXTFLOW \
    --definition "workflow test { }"
```

### 2. Test S3 Access

```bash
# Test S3 bucket access
aws s3 ls s3://your-healthomics-bucket

# Test file upload
echo "test" | aws s3 cp - s3://your-healthomics-bucket/test.txt

# Test file download
aws s3 cp s3://your-healthomics-bucket/test.txt -
```

### 3. Test ECR Access

```bash
# Test ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Test image pull
docker pull YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/healthomics-workflows:latest
```

### 4. Test Batch Access

```bash
# Test compute environment
aws batch describe-compute-environments --compute-environments healthomics-compute-env

# Test job queue
aws batch describe-job-queues --job-queues healthomics-job-queue
```

## Troubleshooting

### Common Issues

#### 1. Permission Denied Errors

**Problem**: Access denied when accessing AWS services
**Solution**:
- Verify IAM role permissions
- Check service-specific policies
- Ensure correct AWS region

#### 2. Service Quota Exceeded

**Problem**: Service quota limits reached
**Solution**:
- Request quota increases
- Check current usage
- Optimize resource usage

#### 3. HealthOmics Workgroup Issues

**Problem**: Cannot create or access workgroups
**Solution**:
- Verify HealthOmics service is enabled
- Check workgroup limits
- Ensure proper permissions

#### 4. S3 Bucket Access Issues

**Problem**: Cannot access S3 bucket
**Solution**:
- Verify bucket policy
- Check IAM permissions
- Ensure bucket exists in correct region

#### 5. ECR Authentication Issues

**Problem**: Cannot authenticate with ECR
**Solution**:
- Verify ECR repository exists
- Check IAM permissions
- Ensure correct region

### Debug Commands

```bash
# Check AWS credentials
aws sts get-caller-identity

# Check service status
aws omics list-workgroups
aws batch describe-compute-environments
aws s3 ls
aws ecr describe-repositories

# Check IAM roles
aws iam get-role --role-name HealthOmicsExecutionRole
aws iam list-attached-role-policies --role-name HealthOmicsExecutionRole
```

### Log Analysis

```bash
# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix /aws/healthomics
aws logs describe-log-streams --log-group-name /aws/healthomics/workflows
aws logs get-log-events --log-group-name /aws/healthomics/workflows --log-stream-name STREAM_NAME
```

## Best Practices

### Security

1. **Use least-privilege access**: Grant only necessary permissions
2. **Enable encryption**: Use S3 server-side encryption
3. **Monitor access**: Enable CloudTrail logging
4. **Regular audits**: Review IAM permissions regularly

### Cost Optimization

1. **Right-size resources**: Use appropriate instance types
2. **Monitor usage**: Track resource consumption
3. **Use spot instances**: For non-critical workloads
4. **Clean up resources**: Remove unused resources

### Performance

1. **Optimize containers**: Use efficient container images
2. **Parallel execution**: Leverage Nextflow's parallel capabilities
3. **Data locality**: Keep data close to compute resources
4. **Caching**: Use Nextflow's caching mechanisms

### Monitoring

1. **Enable logging**: Use CloudWatch for monitoring
2. **Set up alerts**: Configure alarms for failures
3. **Track metrics**: Monitor resource usage and costs
4. **Regular reviews**: Analyze performance and costs

## Conclusion

This guide provides comprehensive instructions for setting up AWS HealthOmics for CWL to Nextflow migration. By following these steps, you can create a robust, scalable environment for running converted workflows.

Remember to:
- Test all components thoroughly
- Monitor costs and usage
- Keep security best practices in mind
- Regularly review and optimize your setup

For additional support, refer to the AWS HealthOmics documentation and community resources.

