/*
 * Generated Nextflow workflow from CWL for AWS HealthOmics
 * Workflow: {{ workflow_info.name }}
 * Version: {{ workflow_info.version }}
 * Description: {{ workflow_info.description }}
 */

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

// Workflow parameters
{% for input in inputs %}
params.{{ input.name }} = {{ input.default if input.default else 'null' }}  // {{ input.description }}
{% endfor %}

// Input channels
{% for input in inputs %}
{{ input.name }}_channel = Channel.value(params.{{ input.name }})
{% endfor %}

// Process definitions
{% for process in processes %}
process {{ process.name }} {
    // AWS HealthOmics optimized container
    {% if process.container %}
    container '{{ process.container }}'
    {% else %}
    container 'public.ecr.aws/healthomics/nextflow:latest'
    {% endif %}
    
    // AWS Batch executor
    executor 'awsbatch'
    
    // Resource requirements optimized for AWS
    {% if process.resources %}
    cpus {{ process.resources.cpus | default(2) }}
    memory '{{ process.resources.memory | default("4 GB") }}'
    time '{{ process.resources.time | default("2h") }}'
    {% else %}
    cpus 2
    memory '4 GB'
    time '2h'
    {% endif %}
    
    // Error handling
    errorStrategy 'retry'
    maxRetries 3
    
    // HealthOmics monitoring
    beforeScript '''
        echo "Starting process: $task.name"
        echo "Process ID: $task.process"
        echo "Task ID: $task.hash"
        echo "Attempt: $task.attempt"
        echo "AWS Region: ${AWS_DEFAULT_REGION}"
        echo "HealthOmics Workgroup: ${AWS_HEALTHOMICS_WORKGROUP}"
    '''
    
    afterScript '''
        echo "Completed process: $task.name"
        echo "Exit status: $task.exitStatus"
        echo "Duration: $task.duration"
        echo "Memory used: $task.memory"
        echo "CPU used: $task.cpus"
    '''
    
    // Inputs
    {% for input in process.inputs %}
    input:
    {% if input.source %}
    val {{ input.name }} from {{ input.source }}
    {% else %}
    val {{ input.name }}
    {% endif %}
    {% endfor %}
    
    // Outputs
    {% for output in process.outputs %}
    output:
    {% if output.type == 'file' %}
    file "{{ output.name }}" into {{ output.name }}_channel
    {% else %}
    val {{ output.name }} into {{ output.name }}_channel
    {% endif %}
    {% endfor %}
    
    script:
    """
    # HealthOmics process script for {{ process.name }}
    echo "Running {{ process.name }} on AWS HealthOmics"
    
    {{ process.script }}
    
    # Log completion
    echo "{{ process.name }} completed successfully"
    """
}
{% endfor %}

// Workflow definition
workflow {
    {% for step in workflow %}
    // {{ step.name }}
    {% if step.dependencies %}
    {% for dep in step.dependencies %}
    {{ step.name }}({{ dep }}_channel)
    {% endfor %}
    {% else %}
    {{ step.name }}()
    {% endif %}
    {% endfor %}
    
    // Outputs with S3 publishing
    {% for output in outputs %}
    {{ output.name }}_channel
        .set { {{ output.name }}_final }
        .publishDir(
            path: 's3://${AWS_HEALTHOMICS_BUCKET}/results/{{ output.name }}/',
            mode: 'copy',
            saveAs: { filename -> filename.equals('versions') ? null : filename }
        )
    {% endfor %}
}

// HealthOmics execution profiles
profiles {
    healthomics {
        process.executor = 'awsbatch'
        aws.region = '${AWS_DEFAULT_REGION}'
        aws.healthomics.workgroup = '${AWS_HEALTHOMICS_WORKGROUP}'
        
        // Enable HealthOmics monitoring
        monitoring.enabled = true
        monitoring.interval = '30s'
        
        // Configure data management
        workDir = 's3://${AWS_HEALTHOMICS_BUCKET}/work/'
    }
    
    healthomics-dev {
        includeConfig 'profiles/healthomics'
        process.cpus = 1
        process.memory = '2 GB'
        process.time = '1h'
    }
    
    healthomics-prod {
        includeConfig 'profiles/healthomics'
        process.cpus = 4
        process.memory = '16 GB'
        process.time = '8h'
    }
}

