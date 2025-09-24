/*
 * Generated Nextflow workflow from CWL for AWS HealthOmics
 * Workflow: example_workflow
 * Version: v1.2
 * Description: A simple example workflow
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
params.input_file = null  // Input file to process
params.threads = 4  // 

// Input channels
input_file_channel = Channel.value(params.input_file)
threads_channel = Channel.value(params.threads)

// Process definitions
process process_step {
    // AWS HealthOmics optimized container
    container 'public.ecr.aws/healthomics/example:latest'
    
    // AWS Batch executor
    executor 'awsbatch'
    
    // Resource requirements optimized for AWS
    cpus 1
    memory '1 GB'
    time '1h'
    
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
    input:
    val input from input_file
    input:
    val threads from threads
    
    // Outputs
    output:
    file "output" into output_channel
    
    script:
    """
    # HealthOmics process script for process_step
    echo "Running process_step on AWS HealthOmics"
    
    
        # Process script for process_step
        # This would be generated from the actual CWL tool definition
        
        # Example command structure
        # Replace with actual command from CWL tool
        echo "Running process_step"
        
        # Input processing
        # Output generation
        
    
    # Log completion
    echo "process_step completed successfully"
    """
}

// Workflow definition
workflow {
    // process_step
    process_step()
    
    // Outputs with S3 publishing
    output_file_channel
        .set { output_file_final }
        .publishDir(
            path: 's3://${AWS_HEALTHOMICS_BUCKET}/results/output_file/',
            mode: 'copy',
            saveAs: { filename -> filename.equals('versions') ? null : filename }
        )
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
