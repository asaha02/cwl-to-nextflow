cwlVersion: v1.0
class: CommandLineTool
baseCommand: [bwa, mem]
hints:
  DockerRequirement:
    dockerPull: biocontainers/bwa:v0.7.17_cv1
inputs:
  reference: File
  fastq_1: File
  fastq_2: File
outputs:
  sam:
    type: File
    outputBinding:
      glob: "output.sam"
arguments:
  - valueFrom: "$(inputs.reference.path)"
  - valueFrom: "$(inputs.fastq_1.path)"
  - valueFrom: "$(inputs.fastq_2.path)"
stdout: output.sam
