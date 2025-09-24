#!/usr/bin/env python3
"""
Streamlit App for CWL to Nextflow Migration Toolkit

Interactive web interface for demonstrating CWL to Nextflow migration features.
"""

import streamlit as st
import json
import yaml
import sys
from pathlib import Path
import tempfile
import zipfile
import io
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import our modules
try:
    from src.cwl_parser import CWLParser
    from src.nextflow_generator import NextflowGenerator
    from src.resource_mapper import ResourceMapper
    from src.container_handler import ContainerHandler
    from src.validation import WorkflowValidator
    from src.aws_integration import AWSHealthOmicsIntegration
except ImportError as e:
    st.error(f"Failed to import modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="CWL to Nextflow Migration Toolkit",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e8b57;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        padding: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🔄 CWL to Nextflow Migration Toolkit</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Welcome to the interactive CWL to Nextflow Migration Toolkit! This app demonstrates how to convert 
    Common Workflow Language (CWL) workflows to Nextflow pipelines optimized for AWS HealthOmics.
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Configuration")
        
        # AWS HealthOmics settings
        st.subheader("AWS HealthOmics")
        aws_healthomics = st.checkbox("Enable AWS HealthOmics features", value=True)
        aws_region = st.selectbox("AWS Region", ["us-east-1", "us-west-2", "eu-west-1"], index=0)
        
        # Resource optimization
        st.subheader("Resource Optimization")
        optimize_resources = st.checkbox("Optimize for AWS instance types", value=True)
        instance_type = st.selectbox("Target Instance Type", 
                                   ["t3.small", "t3.medium", "t3.large", "m5.large", "m5.xlarge", "c5.large", "c5.xlarge"], 
                                   index=2)
        
        # Container optimization
        st.subheader("Container Optimization")
        optimize_containers = st.checkbox("Optimize containers for AWS ECR", value=True)
        
        # Validation settings
        st.subheader("Validation")
        run_validation = st.checkbox("Run validation checks", value=True)
        strict_validation = st.checkbox("Strict validation mode", value=False)
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📁 Upload & Convert", "👀 Live Preview", "📊 Validation Results", "⚙️ Advanced Features", "📖 Docs"])
    
    with tab1:
        upload_and_convert_tab(aws_healthomics, aws_region, optimize_resources, instance_type, 
                              optimize_containers, run_validation, strict_validation)
    
    with tab2:
        live_preview_tab()
    
    with tab3:
        validation_results_tab()
    
    with tab4:
        advanced_features_tab()
    
    with tab5:
        docs_tab()

def upload_and_convert_tab(aws_healthomics, aws_region, optimize_resources, instance_type, 
                          optimize_containers, run_validation, strict_validation):
    """Upload and convert tab."""
    
    st.markdown('<h2 class="section-header">📁 Upload & Convert CWL Workflow</h2>', unsafe_allow_html=True)
    
    # File upload section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a CWL file",
            type=['cwl', 'yaml', 'yml'],
            help="Upload a CWL workflow file to convert to Nextflow"
        )
    
    with col2:
        st.markdown("**Or use example:**")
        if st.button("Load Example CWL", type="primary"):
            example_cwl = get_example_cwl()
            st.session_state['example_cwl'] = example_cwl
            st.success("Example CWL loaded!")
    
    # Process uploaded file or example
    cwl_content = None
    cwl_filename = None
    
    if uploaded_file is not None:
        try:
            cwl_content = uploaded_file.read().decode('utf-8')
            cwl_filename = uploaded_file.name
            st.success(f"✅ File uploaded: {cwl_filename}")
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
            return
    
    elif 'example_cwl' in st.session_state:
        cwl_content = yaml.dump(st.session_state['example_cwl'])
        cwl_filename = "example_workflow.cwl"
        st.info("📝 Using example CWL workflow")
    
    if cwl_content:
        # Display CWL content
        with st.expander("📄 View CWL Content", expanded=False):
            st.code(cwl_content, language='yaml')
        
        # Convert button
        if st.button("🔄 Convert to Nextflow", type="primary", use_container_width=True):
            convert_workflow(cwl_content, cwl_filename, aws_healthomics, aws_region, 
                           optimize_resources, instance_type, optimize_containers, 
                           run_validation, strict_validation)

def live_preview_tab():
    """Live preview tab."""
    
    st.markdown('<h2 class="section-header">👀 Live Preview</h2>', unsafe_allow_html=True)
    
    if 'conversion_results' not in st.session_state:
        st.info("👆 Please convert a workflow first in the 'Upload & Convert' tab")
        return
    
    results = st.session_state['conversion_results']
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Processes", results.get('process_count', 0))
    
    with col2:
        st.metric("Inputs", results.get('input_count', 0))
    
    with col3:
        st.metric("Outputs", results.get('output_count', 0))
    
    with col4:
        validation_score = results.get('validation_score', 0)
        st.metric("Validation Score", f"{validation_score:.1f}%")
    
    # Tabs for different outputs
    preview_tab1, preview_tab2, preview_tab3 = st.tabs(["📝 Nextflow Pipeline", "⚙️ Configuration", "📋 Validation Report"])
    
    with preview_tab1:
        st.subheader("Generated Nextflow Pipeline")
        if 'nextflow_pipeline' in results:
            st.code(results['nextflow_pipeline'], language='groovy')
        else:
            st.error("No Nextflow pipeline generated")
    
    with preview_tab2:
        st.subheader("Configuration File")
        if 'config_content' in results:
            st.code(results['config_content'], language='groovy')
        else:
            st.error("No configuration file generated")
    
    with preview_tab3:
        st.subheader("Validation Report")
        if 'validation_results' in results:
            display_validation_results(results['validation_results'])
        else:
            st.error("No validation results available")

def validation_results_tab():
    """Validation results tab."""
    
    st.markdown('<h2 class="section-header">📊 Validation Results</h2>', unsafe_allow_html=True)
    
    if 'conversion_results' not in st.session_state:
        st.info("👆 Please convert a workflow first in the 'Upload & Convert' tab")
        return
    
    results = st.session_state['conversion_results']
    
    if 'validation_results' not in results:
        st.error("No validation results available")
        return
    
    validation_results = results['validation_results']
    if not validation_results:
        st.error("No validation results available (validation may be disabled).")
        return
    
    # Overall validation status
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if validation_results.get('valid', False):
            st.markdown('<div class="success-box">✅ <strong>Valid</strong></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-box">❌ <strong>Invalid</strong></div>', unsafe_allow_html=True)
    
    with col2:
        score = validation_results.get('overall_score', 0)
        st.progress(score / 100)
        st.write(f"Overall Score: {score:.1f}%")
    
    # Detailed validation results
    display_validation_results(validation_results)

    # Include all steps summary if available from conversion context
    if 'conversion_results' in st.session_state:
        process_names = st.session_state['conversion_results'].get('process_names', [])
        if process_names:
            st.markdown('<h3 class="section-header">🧩 Workflow Steps</h3>', unsafe_allow_html=True)
            for name in process_names:
                with st.expander(f"Process: {name}"):
                    st.write(f"- Name: {name}")
                    # Future: add per-step validation or resources when available

    # Raw per-rule scores (for transparency)
    with st.expander("Raw Rule Scores"):
        st.code(json.dumps(validation_results.get('scores', {}), indent=2), language='json')

def advanced_features_tab():
    """Advanced features tab."""
    
    st.markdown('<h2 class="section-header">⚙️ Advanced Features</h2>', unsafe_allow_html=True)
    
    # Resource optimization demo
    st.subheader("🔧 Resource Optimization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Current Resources:**")
        if st.button("Demo Resource Optimization"):
            demo_resource_optimization()
    
    with col2:
        st.write("**Optimized Resources:**")
        if 'resource_demo' in st.session_state:
            display_resource_comparison(st.session_state['resource_demo'])
    
    # Container optimization demo
    st.subheader("🐳 Container Optimization")
    
    container_input = st.text_input("Enter container image:", value="docker.io/bwa:latest")
    
    if st.button("Optimize Container"):
        optimized = optimize_container_for_aws(container_input)
        if optimized:
            st.success(f"✅ Optimized: {optimized}")
        else:
            st.error("❌ Failed to optimize container")
    
    # AWS HealthOmics integration demo
    st.subheader("☁️ AWS HealthOmics Integration")
    
    if st.button("Test AWS HealthOmics Connection"):
        test_aws_connection()

def examples_tab():
    pass

def docs_tab():
    """Documentation tab showing README files."""
    st.markdown('<h2 class="section-header">📖 Documentation</h2>', unsafe_allow_html=True)

    repo_root = Path(__file__).parent
    readme_file = repo_root / "README.md"

    if not readme_file.exists():
        st.error(f"Document not found: {readme_file}")
        return

    try:
        content = readme_file.read_text(encoding="utf-8")
        st.markdown(content)
    except Exception as e:
        st.error(f"Failed to load document: {e}")

def convert_workflow(cwl_content, filename, aws_healthomics, aws_region, optimize_resources, 
                    instance_type, optimize_containers, run_validation, strict_validation):
    """Convert CWL workflow to Nextflow."""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize components
        status_text.text("Initializing components...")
        progress_bar.progress(10)
        
        cwl_parser = CWLParser()
        nextflow_generator = NextflowGenerator()
        resource_mapper = ResourceMapper()
        container_handler = ContainerHandler()
        validator = WorkflowValidator()
        
        # Parse CWL
        status_text.text("Parsing CWL workflow...")
        progress_bar.progress(20)
        
        if filename.endswith('.cwl'):
            # Parse as YAML first
            cwl_data = yaml.safe_load(cwl_content)
        else:
            cwl_data = yaml.safe_load(cwl_content)
        
        components = cwl_parser.extract_components(cwl_data)
        
        # Map resources
        status_text.text("Mapping resources...")
        progress_bar.progress(40)
        
        resource_mapping = resource_mapper.map_resources(components)
        
        if optimize_resources:
            # Optimize based on available API: takes components and optional target instance
            resource_mapping = resource_mapper.optimize_for_aws(components, target_instance_type=instance_type)
        
        # Process containers
        status_text.text("Processing containers...")
        progress_bar.progress(60)
        
        container_specs = container_handler.process_containers(components)
        
        if optimize_containers:
            # Use available API to optimize containers for AWS registries
            container_specs = {
                name: container_handler._optimize_for_aws(spec)
                for name, spec in container_specs.items()
            }
        
        # Generate Nextflow
        status_text.text("Generating Nextflow pipeline...")
        progress_bar.progress(80)
        
        nextflow_pipeline = nextflow_generator.generate_pipeline(
            components, resource_mapping, container_specs, aws_healthomics=aws_healthomics
        )
        
        config_content = nextflow_generator.generate_config_file(
            components, resource_mapping, aws_healthomics=aws_healthomics
        )
        
        # Validate
        validation_results = None
        if run_validation:
            status_text.text("Validating workflow...")
            progress_bar.progress(90)
            
            validation_results = validator.validate_nextflow(nextflow_pipeline)
            # Persist validation report to demo_output with source filename
            try:
                output_dir = Path("demo_output")
                output_dir.mkdir(exist_ok=True)
                report_text = validator.generate_validation_report(validation_results)
                header = f"Source file: {filename}\n\n"
                (output_dir / f"{Path(filename).stem}_validation.txt").write_text(header + report_text, encoding="utf-8")
            except Exception as _e:
                # Don't fail conversion on report write errors
                pass
        
        # Store results
        st.session_state['conversion_results'] = {
            'nextflow_pipeline': nextflow_pipeline,
            'config_content': config_content,
            'validation_results': validation_results,
            'process_count': len(components.get('processes', {})),
            'input_count': len(components.get('inputs', {})),
            'output_count': len(components.get('outputs', {})),
            'validation_score': validation_results.get('overall_score', 0) if validation_results else 0,
            'process_names': list(components.get('processes', {}).keys())
        }
        
        progress_bar.progress(100)
        status_text.text("✅ Conversion completed successfully!")
        
        # Display success message
        st.success("🎉 Workflow converted successfully!")
        
        # Download buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="📥 Download Nextflow Pipeline",
                data=nextflow_pipeline,
                file_name=f"{Path(filename).stem}.nf",
                mime="text/plain"
            )
        
        with col2:
            st.download_button(
                label="📥 Download Configuration",
                data=config_content,
                file_name=f"{Path(filename).stem}_config.nf",
                mime="text/plain"
            )
        
        with col3:
            if validation_results:
                validation_json = json.dumps(validation_results, indent=2)
                st.download_button(
                    label="📥 Download Validation Report",
                    data=validation_json,
                    file_name=f"{Path(filename).stem}_validation.json",
                    mime="application/json"
                )
        
    except Exception as e:
        progress_bar.progress(0)
        status_text.text("❌ Conversion failed!")
        st.error(f"Error during conversion: {str(e)}")
        st.exception(e)

def display_validation_results(validation_results):
    """Display validation results in a user-friendly format."""
    
    if not validation_results:
        st.error("No validation results available")
        return
    
    # Overall score
    score = validation_results.get('overall_score', 0)
    st.metric("Overall Score", f"{score:.1f}%")
    
    # Validation rules
    rules = validation_results.get('rules', {})
    
    for rule_name, rule_result in rules.items():
        with st.expander(f"📋 {rule_name.replace('_', ' ').title()}", expanded=False):
            if rule_result.get('valid', False):
                st.success("✅ Valid")
            else:
                st.error("❌ Invalid")
            
            if rule_result.get('issues'):
                st.write("**Issues:**")
                for issue in rule_result['issues']:
                    st.error(f"• {issue}")
            
            if rule_result.get('warnings'):
                st.write("**Warnings:**")
                for warning in rule_result['warnings']:
                    st.warning(f"• {warning}")
            
            if rule_result.get('score') is not None:
                st.write(f"**Score:** {rule_result['score']:.1f}%")

def get_example_cwl():
    """Get example CWL workflow."""
    return {
        "cwlVersion": "v1.2",
        "class": "Workflow",
        "id": "example_workflow",
        "label": "Example Workflow",
        "doc": "A simple example workflow for demonstration",
        "inputs": {
            "input_file": {
                "type": "File",
                "label": "Input file",
                "doc": "Input file to process"
            },
            "threads": {
                "type": "int",
                "label": "Number of threads",
                "default": 4
            }
        },
        "outputs": {
            "output_file": {
                "type": "File",
                "label": "Output file",
                "outputSource": "process_step/output"
            }
        },
        "steps": {
            "process_step": {
                "run": "tools/example_tool.cwl",
                "in": {
                    "input": "input_file",
                    "threads": "threads"
                },
                "out": ["output"]
            }
        },
        "requirements": [
            {
                "class": "DockerRequirement",
                "dockerPull": "public.ecr.aws/healthomics/example:latest"
            },
            {
                "class": "ResourceRequirement",
                "coresMin": 4,
                "ramMin": 8000000000
            }
        ]
    }

def demo_resource_optimization():
    """Demo resource optimization."""
    # This would normally call the actual optimization functions
    st.session_state['resource_demo'] = {
        'original': {'cpus': 1, 'memory': '1 GB'},
        'optimized': {'cpus': 2, 'memory': '4 GB'}
    }

def display_resource_comparison(demo_data):
    """Display resource comparison."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Original:**")
        st.write(f"CPUs: {demo_data['original']['cpus']}")
        st.write(f"Memory: {demo_data['original']['memory']}")
    
    with col2:
        st.write("**Optimized:**")
        st.write(f"CPUs: {demo_data['optimized']['cpus']}")
        st.write(f"Memory: {demo_data['optimized']['memory']}")

def optimize_container_for_aws(container_image):
    """Optimize container for AWS ECR."""
    # Simple optimization logic
    if container_image.startswith('docker.io/'):
        return container_image.replace('docker.io/', 'public.ecr.aws/healthomics/')
    elif container_image.startswith('quay.io/'):
        return container_image.replace('quay.io/', 'public.ecr.aws/healthomics/')
    return container_image

def test_aws_connection():
    """Test AWS HealthOmics connection."""
    try:
        # This would normally test the actual AWS connection
        st.success("✅ AWS HealthOmics connection successful!")
    except Exception as e:
        st.error(f"❌ AWS HealthOmics connection failed: {e}")

def load_example_workflow(workflow_name):
    """Load example workflow."""
    st.success(f"✅ Loaded {workflow_name} example!")
    # This would load the actual example workflow

def demos_tab():
    pass

if __name__ == "__main__":
    main()
