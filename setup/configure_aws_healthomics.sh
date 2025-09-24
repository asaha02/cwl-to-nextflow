#!/bin/bash

# AWS HealthOmics Configuration Script
# This script sets up AWS HealthOmics environment for CWL to Nextflow migration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
AWS_REGION=${AWS_DEFAULT_REGION:-us-east-1}
WORKGROUP_NAME=${AWS_HEALTHOMICS_WORKGROUP:-default}
ROLE_NAME=${AWS_HEALTHOMICS_ROLE:-HealthOmicsExecutionRole}
BUCKET_NAME=${AWS_HEALTHOMICS_BUCKET:-healthomics-workflows-$(date +%s)}
QUEUE_NAME=${AWS_HEALTHOMICS_QUEUE:-default}
COMPUTE_ENV=${AWS_HEALTHOMICS_COMPUTE_ENV:-default}

echo -e "${BLUE}Setting up AWS HealthOmics environment...${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed. Please install it first.${NC}"
    echo "Visit: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ AWS CLI is configured${NC}"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${BLUE}AWS Account ID: ${AWS_ACCOUNT_ID}${NC}"

# Create S3 bucket for HealthOmics
echo -e "${BLUE}Creating S3 bucket for HealthOmics...${NC}"
if aws s3 ls "s3://$BUCKET_NAME" 2>&1 | grep -q 'NoSuchBucket'; then
    if [ "$AWS_REGION" = "us-east-1" ]; then
        aws s3 mb "s3://$BUCKET_NAME"
    else
        aws s3 mb "s3://$BUCKET_NAME" --region "$AWS_REGION"
    fi
    echo -e "${GREEN}✓ Created S3 bucket: $BUCKET_NAME${NC}"
else
    echo -e "${YELLOW}⚠ S3 bucket already exists: $BUCKET_NAME${NC}"
fi

# Create IAM role for HealthOmics (if it doesn't exist)
echo -e "${BLUE}Setting up IAM role for HealthOmics...${NC}"
if ! aws iam get-role --role-name "$ROLE_NAME" &> /dev/null; then
    echo -e "${YELLOW}⚠ IAM role '$ROLE_NAME' does not exist.${NC}"
    echo -e "${YELLOW}Please create the role manually with the following trust policy:${NC}"
    cat << EOF
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
EOF
    
    echo -e "${YELLOW}And attach the following policies:${NC}"
    echo "- AmazonHealthOmicsFullAccess"
    echo "- AmazonS3FullAccess"
    echo "- AWSBatchFullAccess"
    echo "- CloudWatchLogsFullAccess"
else
    echo -e "${GREEN}✓ IAM role exists: $ROLE_NAME${NC}"
fi

# Create HealthOmics workgroup
echo -e "${BLUE}Creating HealthOmics workgroup...${NC}"
if ! aws omics get-workgroup --name "$WORKGROUP_NAME" &> /dev/null; then
    aws omics create-workgroup \
        --name "$WORKGROUP_NAME" \
        --description "Default workgroup for CWL to Nextflow migration" \
        --region "$AWS_REGION"
    echo -e "${GREEN}✓ Created HealthOmics workgroup: $WORKGROUP_NAME${NC}"
else
    echo -e "${YELLOW}⚠ HealthOmics workgroup already exists: $WORKGROUP_NAME${NC}"
fi

# Create ECR repository for containers
echo -e "${BLUE}Setting up ECR repository...${NC}"
ECR_REPO_NAME="healthomics-workflows"
if ! aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" &> /dev/null; then
    aws ecr create-repository \
        --repository-name "$ECR_REPO_NAME" \
        --region "$AWS_REGION"
    echo -e "${GREEN}✓ Created ECR repository: $ECR_REPO_NAME${NC}"
else
    echo -e "${YELLOW}⚠ ECR repository already exists: $ECR_REPO_NAME${NC}"
fi

# Get ECR login token
echo -e "${BLUE}Getting ECR login token...${NC}"
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
echo -e "${GREEN}✓ ECR login successful${NC}"

# Create environment file
echo -e "${BLUE}Creating environment configuration...${NC}"
cat > .env << EOF
# AWS HealthOmics Configuration
export AWS_DEFAULT_REGION=$AWS_REGION
export AWS_HEALTHOMICS_WORKGROUP=$WORKGROUP_NAME
export AWS_HEALTHOMICS_ROLE=arn:aws:iam::$AWS_ACCOUNT_ID:role/$ROLE_NAME
export AWS_HEALTHOMICS_BUCKET=$BUCKET_NAME
export AWS_HEALTHOMICS_QUEUE=$QUEUE_NAME
export AWS_HEALTHOMICS_COMPUTE_ENV=$COMPUTE_ENV
export AWS_HEALTHOMICS_ECR_REGISTRY=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
export CONTAINER_REGISTRY=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
EOF

echo -e "${GREEN}✓ Created .env file with configuration${NC}"

# Create AWS Batch compute environment (optional)
echo -e "${BLUE}Setting up AWS Batch compute environment...${NC}"
if ! aws batch describe-compute-environments --compute-environments "$COMPUTE_ENV" &> /dev/null; then
    echo -e "${YELLOW}⚠ AWS Batch compute environment '$COMPUTE_ENV' does not exist.${NC}"
    echo -e "${YELLOW}Please create it manually or use an existing one.${NC}"
else
    echo -e "${GREEN}✓ AWS Batch compute environment exists: $COMPUTE_ENV${NC}"
fi

# Create AWS Batch job queue (optional)
echo -e "${BLUE}Setting up AWS Batch job queue...${NC}"
if ! aws batch describe-job-queues --job-queues "$QUEUE_NAME" &> /dev/null; then
    echo -e "${YELLOW}⚠ AWS Batch job queue '$QUEUE_NAME' does not exist.${NC}"
    echo -e "${YELLOW}Please create it manually or use an existing one.${NC}"
else
    echo -e "${GREEN}✓ AWS Batch job queue exists: $QUEUE_NAME${NC}"
fi

# Summary
echo -e "${GREEN}${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AWS HealthOmics Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${BLUE}Configuration Summary:${NC}"
echo -e "  Region: $AWS_REGION"
echo -e "  Workgroup: $WORKGROUP_NAME"
echo -e "  Role: $ROLE_NAME"
echo -e "  S3 Bucket: $BUCKET_NAME"
echo -e "  ECR Registry: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
echo -e "  Job Queue: $QUEUE_NAME"
echo -e "  Compute Environment: $COMPUTE_ENV"
echo -e "${GREEN}${NC}"

echo -e "${YELLOW}Next Steps:${NC}"
echo -e "1. Source the environment file: source .env"
echo -e "2. Verify IAM role permissions"
echo -e "3. Test the setup with: python validate_setup.py"
echo -e "4. Start converting CWL workflows!"

echo -e "${GREEN}Setup completed successfully!${NC}"

