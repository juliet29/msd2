
include: "common.smk"
configfile: "config/test.yaml"


rule generate:
  output:
    "<output_loc>/{sample}/edges/out.json", # edges
    "<output_loc>/{sample}/layout/out.json" # layout
  shell:
    "uv run msd generate {wildcards.sample} {output}"


rule generate_all:
  input:
    expand("<output_loc>/{sample}/layout/out.json",  sample=get_samples)
