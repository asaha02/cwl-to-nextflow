/*
 * Generated Nextflow workflow from CWL
 * Workflow: rnaseq_analysis
 * Version: v1.2
 * Description: A complete RNA-seq analysis pipeline from raw reads to differential expression
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
params.reads1 = null  // Forward reads
params.reads2 = null  // Reverse reads
params.reference_genome = null  // Reference genome
params.annotation = null  // Gene annotation
params.threads = 4  // Number of threads
params.min_length = 50  // Minimum read length

// Input channels
reads1_channel = Channel.value(params.reads1)
reads2_channel = Channel.value(params.reads2)
reference_genome_channel = Channel.value(params.reference_genome)
annotation_channel = Channel.value(params.annotation)

// Process definitions
process fastqc {
    // AWS HealthOmics optimized container
    container 'public.ecr.aws/healthomics/fastqc:latest'
    
    // AWS Batch executor
    executor 'awsbatch'
    
    // Resource requirements optimized for AWS
    cpus 2
    memory '4 GB'
    time '2h'
    
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
    val reads1 from reads1_channel
    val reads2 from reads2_channel
    val threads from params.threads
    
    // Outputs
    output:
    file "reports" into reports_channel
    
    script:
    """
    # HealthOmics process script for fastqc
    echo "Running fastqc on AWS HealthOmics"
    
    fastqc --threads $threads $reads1 $reads2 -o reports/
    
    # Log completion
    echo "fastqc completed successfully"
    """
}

process trimmomatic {
    // AWS HealthOmics optimized container
    container 'public.ecr.aws/healthomics/trimmomatic:latest'
    
    // AWS Batch executor
    executor 'awsbatch'
    
    // Resource requirements optimized for AWS
    cpus 4
    memory '8 GB'
    time '4h'
    
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
    val reads1 from reads1_channel
    val reads2 from reads2_channel
    val threads from params.threads
    val min_length from params.min_length
    
    // Outputs
    output:
    file "trimmed_reads1" into trimmed_reads1_channel
    file "trimmed_reads2" into trimmed_reads2_channel
    
    script:
    """
    # HealthOmics process script for trimmomatic
    echo "Running trimmomatic on AWS HealthOmics"
    
    trimmomatic PE -threads $threads $reads1 $reads2 \
        trimmed_reads1 trimmed_reads1_unpaired \
        trimmed_reads2 trimmed_reads2_unpaired \
        MINLEN:$min_length
    
    # Log completion
    echo "trimmomatic completed successfully"
    """
}

process star_index {
    // AWS HealthOmics optimized container
    container 'public.ecr.aws/healthomics/star:latest'
    
    // AWS Batch executor
    executor 'awsbatch'
    
    // Resource requirements optimized for AWS
    cpus 8
    memory '32 GB'
    time '8h'
    
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
    val reference_genome from reference_genome_channel
    val annotation from annotation_channel
    val threads from params.threads
    
    // Outputs
    output:
    file "index" into index_channel
    
    script:
    """
    # HealthOmics process script for star_index
    echo "Running star index on AWS HealthOmics"
    
    STAR --runMode genomeGenerate \
        --genomeDir index \
        --genomeFastaFiles $reference_genome \
        --sjdbGTFfile $annotation \
        --runThreadN $threads
    
    # Log completion
    echo "star_index completed successfully"
    """
}

process star {
    // AWS HealthOmics optimized container
    container 'public.ecr.aws/healthomics/star:latest'
    
    // AWS Batch executor
    executor 'awsbatch'
    
    // Resource requirements optimized for AWS
    cpus 8
    memory '32 GB'
    time '8h'
    
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
    val trimmed_reads1 from trimmed_reads1_channel
    val trimmed_reads2 from trimmed_reads2_channel
    val index from index_channel
    val threads from params.threads
    
    // Outputs
    output:
    file "bam_files" into bam_files_channel
    
    script:
    """
    # HealthOmics process script for star
    echo "Running star alignment on AWS HealthOmics"
    
    STAR --genomeDir $index \
        --readFilesIn $trimmed_reads1 $trimmed_reads2 \
        --runThreadN $threads \
        --outSAMtype BAM SortedByCoordinate
    
    # Log completion
    echo "star completed successfully"
    """
}

process featurecounts {
    // AWS HealthOmics optimized container
    container 'public.ecr.aws/healthomics/featurecounts:latest'
    
    // AWS Batch executor
    executor 'awsbatch'
    
    // Resource requirements optimized for AWS
    cpus 4
    memory '8 GB'
    time '4h'
    
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
    val bam_files from bam_files_channel
    val annotation from annotation_channel
    val threads from params.threads
    
    // Outputs
    output:
    file "count_matrix" into count_matrix_channel
    
    script:
    """
    # HealthOmics process script for featurecounts
    echo "Running featurecounts on AWS HealthOmics"
    
    featureCounts -T $threads -a $annotation -o count_matrix $bam_files
    
    # Log completion
    echo "featurecounts completed successfully"
    """
}

process deseq2 {
    // AWS HealthOmics optimized container
    container 'public.ecr.aws/healthomics/deseq2:latest'
    
    // AWS Batch executor
    executor 'awsbatch'
    
    // Resource requirements optimized for AWS
    cpus 4
    memory '8 GB'
    time '4h'
    
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
    val count_matrix from count_matrix_channel
    val metadata from params.metadata
    
    // Outputs
    output:
    file "de_results" into de_results_channel
    
    script:
    """
    # HealthOmics process script for deseq2
    echo "Running DESeq2 on AWS HealthOmics"
    
    Rscript -e "
    library(DESeq2)
    # DESeq2 analysis code here
    "
    
    # Log completion
    echo "deseq2 completed successfully"
    """
}

// Workflow definition
workflow {
    // fastqc
    fastqc(reads1_channel, reads2_channel, params.threads)
    
    // trimmomatic
    trimmomatic(reads1_channel, reads2_channel, params.threads, params.min_length)
    
    // star_index
    star_index(reference_genome_channel, annotation_channel, params.threads)
    
    // star
    star(trimmed_reads1_channel, trimmed_reads2_channel, index_channel, params.threads)
    
    // featurecounts
    featurecounts(bam_files_channel, annotation_channel, params.threads)
    
    // deseq2
    deseq2(count_matrix_channel, params.metadata)
    
    // Outputs with S3 publishing
    reports_channel
        .set { fastqc_reports_final }
        .publishDir(
            path: 's3://${AWS_HEALTHOMICS_BUCKET}/results/fastqc_reports/',
            mode: 'copy',
            saveAs: { filename -> filename.equals('versions') ? null : filename }
        )
    
    bam_files_channel
        .set { bam_files_final }
        .publishDir(
            path: 's3://${AWS_HEALTHOMICS_BUCKET}/results/bam_files/',
            mode: 'copy',
            saveAs: { filename -> filename.equals('versions') ? null : filename }
        )
    
    count_matrix_channel
        .set { count_matrix_final }
        .publishDir(
            path: 's3://${AWS_HEALTHOMICS_BUCKET}/results/count_matrix/',
            mode: 'copy',
            saveAs: { filename -> filename.equals('versions') ? null : filename }
        )
    
    de_results_channel
        .set { de_results_final }
        .publishDir(
            path: 's3://${AWS_HEALTHOMICS_BUCKET}/results/de_results/',
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

