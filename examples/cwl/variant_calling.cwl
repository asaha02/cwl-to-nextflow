#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: Workflow
label: "Variant Calling Pipeline"
doc: "A complete variant calling pipeline from raw reads to annotated variants"

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
  
  known_sites:
    type: File[]
    label: "Known variant sites"
    doc: "Known variant sites in VCF format"
    inputBinding:
      position: 4
  
  # Parameters
  threads:
    type: int
    label: "Number of threads"
    doc: "Number of threads to use"
    default: 8
    inputBinding:
      position: 5
  
  min_quality:
    type: int
    label: "Minimum base quality"
    doc: "Minimum base quality for variant calling"
    default: 20
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
    outputSource: bwa/bam_files
  
  # Variant calling outputs
  raw_variants:
    type: File
    outputSource: gatk/raw_variants
  
  filtered_variants:
    type: File
    outputSource: gatk_filter/filtered_variants
  
  # Annotation outputs
  annotated_variants:
    type: File
    outputSource: snpeff/annotated_variants

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
    out: [trimmed_reads1, trimmed_reads2]
  
  # Genome indexing
  bwa_index:
    run: tools/bwa_index.cwl
    in:
      reference_genome: reference_genome
    out: [index]
  
  # Read alignment
  bwa:
    run: tools/bwa.cwl
    in:
      reads1: trimmomatic/trimmed_reads1
      reads2: trimmomatic/trimmed_reads2
      index: bwa_index/index
      threads: threads
    out: [bam_files]
  
  # Duplicate marking
  markduplicates:
    run: tools/markduplicates.cwl
    in:
      bam_files: bwa/bam_files
      threads: threads
    out: [marked_bam]
  
  # Base quality recalibration
  baserecalibrator:
    run: tools/baserecalibrator.cwl
    in:
      bam_file: markduplicates/marked_bam
      reference_genome: reference_genome
      known_sites: known_sites
      threads: threads
    out: [recalibrated_bam]
  
  # Variant calling
  gatk:
    run: tools/gatk.cwl
    in:
      bam_file: baserecalibrator/recalibrated_bam
      reference_genome: reference_genome
      min_quality: min_quality
      threads: threads
    out: [raw_variants]
  
  # Variant filtering
  gatk_filter:
    run: tools/gatk_filter.cwl
    in:
      variants: gatk/raw_variants
      reference_genome: reference_genome
    out: [filtered_variants]
  
  # Variant annotation
  snpeff:
    run: tools/snpeff.cwl
    in:
      variants: gatk_filter/filtered_variants
      reference_genome: reference_genome
    out: [annotated_variants]

requirements:
  - class: DockerRequirement
    dockerPull: "public.ecr.aws/healthomics/variant-calling:latest"
  
  - class: ResourceRequirement
    coresMin: 8
    ramMin: 16000000000
    tmpdirMin: 50000000000
    outdirMin: 20000000000

hints:
  - class: DockerRequirement
    dockerPull: "public.ecr.aws/healthomics/variant-calling:latest"
  
  - class: ResourceRequirement
    coresMin: 16
    ramMin: 32000000000
    tmpdirMin: 100000000000
    outdirMin: 50000000000

