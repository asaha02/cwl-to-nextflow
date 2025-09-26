cwlVersion: v1.0
class: CommandLineTool
baseCommand: [samtools, sort, -o, sorted.bam]
hints:
  DockerRequirement:
    dockerPull: biocontainers/samtools:v1.9-4-deb_cv1
inputs:
  sam: File
outputs:
  sorted_bam:
    type: File
    outputBinding:
      glob: "sorted.bam"
stdin: "$(inputs.sam.path)"
