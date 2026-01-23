configfile: "config/test.yaml"
from msd2.readin.access import get_ids_by_indices

def get_samples(wildcards):
  return get_ids_by_indices(config["start_ix"], config["num_items"])

rule generate:
  output:
    "<output_loc>/{sample}/edges/out.json", # edges
    "<output_loc>/{sample}/layout/out.json" # layout
  shell:
    "uv run msd generate {wildcards.sample} {output}"


rule generate_all:
  input:
    expand("<output_loc>/{sample}/layout/out.json",  sample=get_samples)
