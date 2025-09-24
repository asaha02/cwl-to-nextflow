#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: Workflow
label: "RNA-seq Analysis Pipeline"
doc: "A complete RNA-seq analysis pipeline from raw reads to differential expression"

inputs:
  # Input files
  reads1:
    type: File[]
    label: "Forward reads"
    doc: "Forward reads in FASTQ format"
    inputBinding:
      position: 1
  
  reads2:
    type: File[]
    label: "Reverse reads"
    doc: "Reverse reads in FASTQ format"
    inputBinding:
      position: 2
  
  reference_genome:
    type: File
    label: "Reference genome"
    doc: "Reference genome in FASTA format"
    inputBinding:
      position: 3
  
  annotation:
    type: File
    label: "Gene annotation"
    doc: "Gene annotation in GTF format"
    inputBinding:
      position: 4
  
  # Parameters
  threads:
    type: int
    label: "Number of threads"
    doc: "Number of threads to use"
    default: 4
    inputBinding:
      position: 5
  
  min_length:
    type: int
    label: "Minimum read length"
    doc: "Minimum read length after trimming"
    default: 50
    inputBinding:
      position: 6

outputs:
  # Quality control outputs
  fastqc_reports:
    type: File[]
    outputSource: fastqc/reports
  
  # Alignment outputs
  bam_files:
    type: File[]
    outputSource: star/bam_files
  
  # Quantification outputs
  count_matrix:
    type: File
    outputSource: featurecounts/count_matrix
  
  # Differential expression outputs
  de_results:
    type: File
    outputSource: deseq2/de_results

steps:
  # Quality control
  fastqc:
    run: tools/fastqc.cwl
    in:
      reads1: reads1
      reads2: reads2
      threads: threads
    out: [reports]
  
  # Read trimming
  trimmomatic:
    run: tools/trimmomatic.cwl
    in:
      reads1: reads1
      reads2: reads2
      threads: threads
      min_length: min_length
    out: [trimmed_reads1, trimmed_reads2]
  
  # Genome indexing
  star_index:
    run: tools/star_index.cwl
    in:
      reference_genome: reference_genome
      annotation: annotation
      threads: threads
    out: [index]
  
  # Read alignment
  star:
    run: tools/star.cwl
    in:
      reads1: trimmomatic/trimmed_reads1
      reads2: trimmomatic/trimmed_reads2
      index: star_index/index
      threads: threads
    out: [bam_files]
  
  # Read counting
  featurecounts:
    run: tools/featurecounts.cwl
    in:
      bam_files: star/bam_files
      annotation: annotation
      threads: threads
    out: [count_matrix]
  
  # Differential expression
  deseq2:
    run: tools/deseq2.cwl
    in:
      count_matrix: featurecounts/count_matrix
      metadata: metadata
    out: [de_results]

requirements:
  - class: DockerRequirement
    dockerPull: "public.ecr.aws/healthomics/rnaseq:latest"
  
  - class: ResourceRequirement
    coresMin: 4
    ramMin: 8000000000
    tmpdirMin: 20000000000
    outdirMin: 10000000000

hints:
  - class: DockerRequirement
    dockerPull: "public.ecr.aws/healthomics/rnaseq:latest"
  
  - class: ResourceRequirement
    coresMin: 8
    ramMin: 16000000000
    tmpdirMin: 50000000000
    outdirMin: 20000000000

