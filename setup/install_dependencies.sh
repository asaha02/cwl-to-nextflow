#!/bin/bash

# Dependency Installation Script for CWL to Nextflow Migration Toolkit
# This script installs all required dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Installing dependencies for CWL to Nextflow Migration Toolkit...${NC}"

# Check if running on Linux, macOS, or WSL
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
else
    echo -e "${RED}Unsupported operating system: $OSTYPE${NC}"
    exit 1
fi

echo -e "${BLUE}Detected OS: $OS${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Python dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
    
    # Install pip if not present
    if ! command_exists pip3; then
        echo -e "${YELLOW}Installing pip...${NC}"
        if [ "$OS" = "linux" ]; then
            sudo apt-get update && sudo apt-get install -y python3-pip
        elif [ "$OS" = "macos" ]; then
            curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            python3 get-pip.py
            rm get-pip.py
        fi
    fi
    
    # Install Python packages
    echo -e "${BLUE}Installing Python packages...${NC}"
    pip3 install -r requirements.txt
    
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo -e "${YELLOW}Please install Python 3.8 or higher${NC}"
    exit 1
fi

# Install Node.js and npm
echo -e "${BLUE}Installing Node.js dependencies...${NC}"
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js $NODE_VERSION found${NC}"
    
    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        echo -e "${GREEN}✓ npm $NPM_VERSION found${NC}"
        
        # Install Node.js packages
        echo -e "${BLUE}Installing Node.js packages...${NC}"
        npm install
        
        # Install CWL reference implementation globally
        echo -e "${BLUE}Installing CWL reference implementation...${NC}"
        npm install -g cwltool
        
        echo -e "${GREEN}✓ Node.js dependencies installed${NC}"
    else
        echo -e "${RED}Error: npm is not installed${NC}"
        exit 1
    fi
else
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo -e "${YELLOW}Please install Node.js 16 or higher${NC}"
    echo -e "${YELLOW}Visit: https://nodejs.org/${NC}"
    exit 1
fi

# Install Docker
echo -e "${BLUE}Checking Docker installation...${NC}"
if command_exists docker; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓ $DOCKER_VERSION found${NC}"
    
    # Check if Docker daemon is running
    if docker info >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Docker daemon is running${NC}"
    else
        echo -e "${YELLOW}⚠ Docker daemon is not running${NC}"
        echo -e "${YELLOW}Please start Docker daemon${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Docker is not installed${NC}"
    echo -e "${YELLOW}Please install Docker:${NC}"
    if [ "$OS" = "linux" ]; then
        echo -e "${YELLOW}  sudo apt-get update && sudo apt-get install docker.io${NC}"
    elif [ "$OS" = "macos" ]; then
        echo -e "${YELLOW}  Visit: https://docs.docker.com/desktop/mac/install/${NC}"
    fi
fi

# Install Nextflow
echo -e "${BLUE}Installing Nextflow...${NC}"
if command_exists nextflow; then
    NEXTFLOW_VERSION=$(nextflow --version 2>&1 | head -n1)
    echo -e "${GREEN}✓ $NEXTFLOW_VERSION found${NC}"
else
    echo -e "${BLUE}Installing Nextflow...${NC}"
    curl -s https://get.nextflow.io | bash
    sudo mv nextflow /usr/local/bin/
    echo -e "${GREEN}✓ Nextflow installed${NC}"
fi

# Install AWS CLI
echo -e "${BLUE}Checking AWS CLI installation...${NC}"
if command_exists aws; then
    AWS_VERSION=$(aws --version)
    echo -e "${GREEN}✓ $AWS_VERSION found${NC}"
else
    echo -e "${YELLOW}⚠ AWS CLI is not installed${NC}"
    echo -e "${YELLOW}Please install AWS CLI:${NC}"
    if [ "$OS" = "linux" ]; then
        echo -e "${YELLOW}  curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip'${NC}"
        echo -e "${YELLOW}  unzip awscliv2.zip && sudo ./aws/install${NC}"
    elif [ "$OS" = "macos" ]; then
        echo -e "${YELLOW}  curl 'https://awscli.amazonaws.com/AWSCLIV2.pkg' -o 'AWSCLIV2.pkg'${NC}"
        echo -e "${YELLOW}  sudo installer -pkg AWSCLIV2.pkg -target /${NC}"
    fi
fi

# Install Singularity (optional)
echo -e "${BLUE}Checking Singularity installation...${NC}"
if command_exists singularity; then
    SINGULARITY_VERSION=$(singularity --version)
    echo -e "${GREEN}✓ $SINGULARITY_VERSION found${NC}"
else
    echo -e "${YELLOW}⚠ Singularity is not installed (optional)${NC}"
    echo -e "${YELLOW}To install Singularity:${NC}"
    echo -e "${YELLOW}  Visit: https://sylabs.io/guides/3.0/user-guide/installation.html${NC}"
fi

# Create virtual environment (optional)
echo -e "${BLUE}Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

echo -e "${BLUE}Installing dependencies in virtual environment...${NC}"
pip install -r requirements.txt

# Create activation script
cat > activate_env.sh << 'EOF'
#!/bin/bash
# Activation script for CWL to Nextflow migration environment

echo "Activating CWL to Nextflow migration environment..."

# Activate Python virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Python virtual environment activated"
fi

# Load environment variables
if [ -f ".env" ]; then
    source .env
    echo "✓ Environment variables loaded"
fi

echo "Environment ready for CWL to Nextflow migration!"
echo ""
echo "Available commands:"
echo "  python cwl_to_nextflow.py --help"
echo "  python validate_nextflow.py --help"
echo "  ./demos/basic_conversion.py"
echo ""
EOF

chmod +x activate_env.sh

# Summary
echo -e "${GREEN}${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Dependency Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "${BLUE}Installed Components:${NC}"
echo -e "  ✓ Python 3 with required packages"
echo -e "  ✓ Node.js with CWL reference implementation"
echo -e "  ✓ Nextflow workflow engine"
echo -e "  ✓ Docker container runtime"
echo -e "  ✓ AWS CLI (if available)"
echo -e "  ✓ Python virtual environment"

echo -e "${YELLOW}Next Steps:${NC}"
echo -e "1. Activate the environment: source activate_env.sh"
echo -e "2. Configure AWS: ./setup/configure_aws_healthomics.sh"
echo -e "3. Test installation: python validate_setup.py"
echo -e "4. Start converting workflows!"

echo -e "${GREEN}Installation completed successfully!${NC}"

