# 🌐 CWL to Nextflow Migration Toolkit - Streamlit App

An interactive web interface for the CWL to Nextflow Migration Toolkit, providing an intuitive way to convert Common Workflow Language (CWL) workflows to Nextflow pipelines optimized for AWS HealthOmics.

## 🚀 Quick Start

### Option 1: Using the Launcher Script (Recommended)
```bash
python run_streamlit.py
```

### Option 2: Direct Streamlit Command
```bash
streamlit run streamlit_app.py
```

### Option 3: With Custom Port
```bash
streamlit run streamlit_app.py --server.port 8080
```

## 📋 Prerequisites

### Required Dependencies
- Python 3.8+
- Streamlit
- PyYAML
- Jinja2

### Optional Dependencies (for full functionality)
- cwltool (for advanced CWL parsing)
- boto3 (for AWS integration)
- ruamel.yaml (for better YAML handling)

### Install Dependencies
```bash
# Install basic requirements
pip install -r requirements_streamlit.txt

# Or install manually
pip install streamlit pyyaml jinja2

# For full functionality (optional)
pip install cwltool boto3 ruamel.yaml
```

## 🎯 Features

### 📁 Upload & Convert Tab
- **File Upload**: Upload CWL workflow files (.cwl, .yaml, .yml)
- **Example Workflows**: Load pre-built example workflows
- **Real-time Conversion**: Convert CWL to Nextflow with progress tracking
- **Configuration Options**: 
  - AWS HealthOmics integration
  - Resource optimization
  - Container optimization
  - Validation settings

### 👀 Live Preview Tab
- **Generated Code**: View the complete Nextflow pipeline
- **Configuration**: Preview the generated configuration file
- **Validation Report**: See detailed validation results
- **Metrics**: Process count, input/output counts, validation score

### 📊 Validation Results Tab
- **Overall Score**: Visual progress bar showing validation score
- **Detailed Results**: Rule-by-rule validation breakdown
- **Issues & Warnings**: Clear identification of problems
- **Recommendations**: Suggestions for improvement

### ⚙️ Advanced Features Tab
- **Resource Optimization**: Demo of AWS instance type optimization
- **Container Optimization**: Convert containers to AWS ECR format
- **AWS HealthOmics Integration**: Test AWS connectivity
- **Performance Tuning**: Advanced configuration options

### 📚 Examples Tab
- **Pre-built Workflows**: RNA-seq, Variant Calling, Protein Analysis
- **Workflow Details**: Process counts, inputs, outputs
- **One-click Loading**: Load examples with a single click

## 🎨 User Interface

### Sidebar Configuration
- **AWS HealthOmics**: Enable/disable AWS features, select region
- **Resource Optimization**: Target instance types, optimization settings
- **Container Optimization**: AWS ECR optimization toggle
- **Validation**: Validation mode and strictness settings

### Main Interface
- **Tabbed Layout**: Organized features in separate tabs
- **Progress Tracking**: Real-time conversion progress
- **Download Options**: Download generated files
- **Visual Feedback**: Success/error indicators, progress bars

## 📥 Download Features

The app provides download buttons for:
- **Nextflow Pipeline** (.nf file)
- **Configuration File** (.nf file)
- **Validation Report** (.json file)

## 🔧 Configuration Options

### AWS HealthOmics Settings
- **Enable/Disable**: Toggle AWS HealthOmics features
- **Region Selection**: Choose AWS region (us-east-1, us-west-2, eu-west-1)
- **Batch Configuration**: Automatic batch job settings

### Resource Optimization
- **Instance Types**: t3.small, t3.medium, t3.large, m5.large, m5.xlarge, c5.large, c5.xlarge
- **CPU/Memory Mapping**: Automatic resource allocation
- **Cost Optimization**: Balance performance and cost

### Container Optimization
- **ECR Migration**: Convert Docker Hub/Quay.io images to AWS ECR
- **Security Scanning**: Enable container vulnerability scanning
- **Performance**: Optimize for AWS infrastructure

## 🧪 Example Workflows

### RNA-seq Analysis
- **Description**: Complete RNA-seq analysis pipeline
- **Processes**: 5 (QC, alignment, quantification, etc.)
- **Inputs**: 3 (reads, reference, annotations)
- **Outputs**: 2 (counts, reports)

### Variant Calling
- **Description**: Genomic variant calling pipeline
- **Processes**: 6 (preprocessing, alignment, variant detection)
- **Inputs**: 4 (reads, reference, known variants, intervals)
- **Outputs**: 3 (variants, metrics, reports)

### Protein Analysis
- **Description**: Protein structure prediction workflow
- **Processes**: 4 (prediction, analysis, visualization)
- **Inputs**: 2 (sequence, parameters)
- **Outputs**: 2 (structures, reports)

## 🚨 Troubleshooting

### Common Issues

#### 1. Streamlit Not Found
```bash
pip install streamlit
```

#### 2. Module Import Errors
```bash
# Install missing dependencies
pip install -r requirements_streamlit.txt

# Or install specific modules
pip install pyyaml jinja2
```

#### 3. Port Already in Use
```bash
# Use different port
streamlit run streamlit_app.py --server.port 8080
```

#### 4. File Upload Issues
- Ensure CWL files are valid YAML
- Check file permissions
- Try smaller files first

### Debug Mode
```bash
# Run with debug information
streamlit run streamlit_app.py --logger.level debug
```

## 🔒 Security Considerations

- **File Uploads**: Files are processed in memory, not saved to disk
- **AWS Credentials**: Use environment variables or AWS CLI configuration
- **Network Access**: App runs on localhost by default
- **Data Privacy**: No data is sent to external services

## 🎯 Best Practices

### For Users
1. **Start Small**: Begin with example workflows
2. **Validate First**: Always run validation checks
3. **Review Output**: Check generated code before using
4. **Test Locally**: Validate Nextflow syntax before deployment

### For Developers
1. **Error Handling**: Comprehensive error messages
2. **Progress Feedback**: Clear progress indicators
3. **Validation**: Multiple validation layers
4. **Documentation**: Inline help and tooltips

## 📊 Performance

- **File Size Limits**: Recommended < 10MB for CWL files
- **Processing Time**: Typically 1-5 seconds for standard workflows
- **Memory Usage**: ~100-200MB for typical workflows
- **Browser Compatibility**: Modern browsers (Chrome, Firefox, Safari, Edge)

## 🤝 Contributing

To contribute to the Streamlit app:

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/new-feature`
3. **Make Changes**: Follow existing code style
4. **Test Thoroughly**: Test with various CWL files
5. **Submit Pull Request**: Include description and tests

## 📞 Support

For issues with the Streamlit app:

1. **Check Troubleshooting**: Review common issues above
2. **Check Logs**: Look at Streamlit console output
3. **File Issues**: Create GitHub issue with details
4. **Community**: Join discussions in GitHub Discussions

## 🔄 Updates

The Streamlit app is regularly updated with:
- **New Features**: Additional conversion options
- **Bug Fixes**: Improved error handling
- **UI Improvements**: Better user experience
- **Performance**: Faster processing

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Happy Converting! 🎉**

Transform your CWL workflows into powerful Nextflow pipelines with just a few clicks!
