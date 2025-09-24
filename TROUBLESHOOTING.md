# Troubleshooting Guide

This guide helps resolve common issues with the CWL to Nextflow migration toolkit.

## Common Issues

### 1. "cwl_parser module not found" Error

**Problem**: The cwl_parser module cannot be imported.

**Cause**: Missing optional dependencies, particularly `cwltool`.

### 2. "'str' object has no attribute 'get'" Error

**Problem**: Error in step 4 "Generating Nextflow pipeline" with message "'str' object has no attribute 'get'".

**Cause**: The Nextflow generator expects dictionary input definitions but receives string values from CWL step inputs.

**Solution**: This has been fixed in the latest version. The `_process_step_inputs` method now handles both string and dictionary input definitions.

**Solutions**:

#### Option A: Install Optional Dependencies (Recommended)
```bash
# Install optional dependencies for full CWL support
python install_optional_deps.py

# Or install manually
pip install cwltool ruamel.yaml
```

#### Option B: Use Basic Mode (Fallback)
The toolkit will work with basic YAML parsing even without cwltool:
```bash
# Test basic functionality
python test_cwl_parser.py
```

#### Option C: Install All Dependencies
```bash
# Install all dependencies including optional ones
pip install -r requirements.txt
pip install cwltool cwl-utils schema-salad
```

### 2. Import Errors for Custom Modules

**Problem**: Custom modules (cwl_parser, nextflow_generator, etc.) cannot be imported.

**Solutions**:

1. **Check Python Path**:
   ```bash
   # Make sure you're in the project directory
   cd /path/to/cwl-to-nexflow
   
   # Test import
   python -c "import sys; sys.path.insert(0, 'src'); import cwl_parser; print('Success')"
   ```

2. **Install Missing Dependencies**:
   ```bash
   # Install core dependencies
   pip install -r requirements.txt
   
   # Install optional dependencies
   python install_optional_deps.py
   ```

3. **Check File Structure**:
   ```bash
   # Verify all files exist
   ls -la src/
   ls -la templates/
   ls -la examples/
   ```

### 3. AWS HealthOmics Setup Issues

**Problem**: AWS HealthOmics integration fails.

**Solutions**:

1. **Configure AWS Credentials**:
   ```bash
   aws configure
   ```

2. **Check AWS Permissions**:
   ```bash
   aws sts get-caller-identity
   aws omics list-workgroups
   ```

3. **Run Setup Script**:
   ```bash
   ./setup/configure_aws_healthomics.sh
   ```

### 4. Docker Issues

**Problem**: Docker-related errors, especially "test_docker_daemon is giving error however it is running".

**Solutions**:

1. **Run Docker Test Script**:
   ```bash
   # Run comprehensive Docker test
   python test_docker.py
   ```

2. **Start Docker Daemon**:
   ```bash
   # On Linux
   sudo systemctl start docker
   sudo systemctl enable docker
   
   # On macOS/Windows
   # Start Docker Desktop
   ```

3. **Check Docker Access**:
   ```bash
   # Test basic connectivity
   docker --version
   docker info
   
   # Test with longer timeout
   timeout 30 docker info
   ```

4. **Fix Permission Issues**:
   ```bash
   # Add user to docker group (Linux)
   sudo usermod -aG docker $USER
   
   # Log out and log back in, then test
   docker ps
   ```

5. **Check Docker Status**:
   ```bash
   # Check if Docker daemon is running
   sudo systemctl status docker
   
   # Check Docker processes
   ps aux | grep docker
   ```

6. **Common Docker Issues**:
   - **Permission denied**: Add user to docker group
   - **Cannot connect**: Docker daemon not running
   - **Timeout**: Docker daemon is slow to respond (usually OK)
   - **Connection refused**: Docker daemon not started

### 5. Nextflow Issues

**Problem**: Nextflow not found or not working.

**Solutions**:

1. **Install Nextflow**:
   ```bash
   curl -s https://get.nextflow.io | bash
   sudo mv nextflow /usr/local/bin/
   ```

2. **Check Nextflow Version**:
   ```bash
   nextflow --version
   ```

### 6. Node.js/npm Issues

**Problem**: Node.js or npm not found.

**Solutions**:

1. **Install Node.js**:
   - Visit https://nodejs.org/
   - Download and install LTS version

2. **Install CWL Tool**:
   ```bash
   npm install -g cwltool
   ```

## Testing Your Installation

### 1. Run Installation Test
```bash
python test_installation.py
```

### 2. Test Individual Components
```bash
# Test CWL parser
python test_cwl_parser.py

# Test basic conversion
python demos/basic_conversion.py

# Test AWS HealthOmics demo
python demos/aws_healthomics_demo.py
```

### 3. Test with Example Workflows
```bash
# Convert example CWL workflow
python cwl_to_nextflow.py --input examples/cwl/rnaseq_analysis.cwl --output ./test_output/

# Validate converted workflow
python validate_nextflow.py --workflow ./test_output/rnaseq_analysis.nf
```

## Dependency Requirements

### Required Dependencies
- Python 3.8+
- pyyaml or ruamel.yaml
- jinja2
- click
- rich

### Optional Dependencies (for full functionality)
- cwltool (for full CWL parsing)
- cwl-utils (for CWL utilities)
- schema-salad (for schema validation)
- boto3 (for AWS integration)
- docker (for container support)

### System Dependencies
- Node.js 16+ (for CWL tool)
- Docker (for container support)
- Nextflow 22+ (for workflow execution)
- AWS CLI (for AWS integration)

## Getting Help

### 1. Check Logs
```bash
# Enable debug mode
python cwl_to_nextflow.py --input workflow.cwl --debug

# Check validation with verbose output
python validate_nextflow.py --workflow workflow.nf --verbose
```

### 2. Run Diagnostics
```bash
# Run comprehensive test
python test_installation.py

# Check specific components
python -c "import sys; print(sys.path)"
python -c "import cwl_parser; print('CWL parser OK')"
```

### 3. Common Error Messages

#### "ModuleNotFoundError: No module named 'cwltool'"
- Install cwltool: `pip install cwltool`
- Or use basic mode without cwltool

#### "ImportError: cannot import name 'load_tool'"
- Update cwltool: `pip install --upgrade cwltool`
- Check cwltool version: `cwltool --version`

#### "AWS credentials not configured"
- Run: `aws configure`
- Check credentials: `aws sts get-caller-identity`

#### "Docker daemon not running"
- Start Docker daemon
- Check Docker status: `docker info`

## Performance Issues

### 1. Slow Conversion
- Use batch mode for multiple workflows
- Optimize resource requirements
- Use AWS-optimized containers

### 2. Memory Issues
- Increase system memory
- Use smaller instance types
- Optimize workflow complexity

### 3. Network Issues
- Check internet connection
- Configure proxy if needed
- Use local container registries

## Best Practices

### 1. Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
python install_optional_deps.py

# Test installation
python test_installation.py
```

### 2. Production Setup
```bash
# Use specific versions
pip install cwltool==3.1.20231201152605
pip install boto3==1.34.0

# Configure AWS properly
aws configure
./setup/configure_aws_healthomics.sh

# Test with real workflows
python cwl_to_nextflow.py --input your_workflow.cwl --aws-healthomics
```

### 3. Maintenance
- Regularly update dependencies
- Monitor AWS costs
- Clean up temporary files
- Review validation reports

## Still Having Issues?

1. **Check the logs** for specific error messages
2. **Run the test suite** to identify problems
3. **Review the documentation** for detailed setup instructions
4. **Check system requirements** and dependencies
5. **Try the basic mode** without optional dependencies

If you continue to have issues, please:
1. Run `python test_installation.py` and share the output
2. Include the specific error message
3. Provide your system information (OS, Python version, etc.)
