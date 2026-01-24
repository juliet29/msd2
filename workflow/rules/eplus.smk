from pathlib import Path 

include: "common.smk"
configfile: "config/test.yaml"



def get_eplus_ready_samples(wildcards):
  loc = Path(config["pathvars"]["output_loc"])
  json = "out.json"
  ymove_path = loc / "{sample}" / "ymove" /json

  samples, = glob_wildcards(ymove_path)
  return samples

rule test_ep_ready:
  input:
    get_eplus_ready_samples
  shell:
    "echo {input}"


rule make_idf:
  input:
    "<output_loc>/{sample}/edges/out.json", # edges
    "<output_loc>/{sample}/ymove/out.json" # corrected layout
  output:
    "<models_loc>/{sample}/run.idf" # TODO: turn to run.idf, or allow replan to just take the path 
  log:
    "<models_loc>/{sample}/out.log"
  shell:
    "uv run msd create-idf {input} {output} 2>{log}"
    # potentially, info about weather data also.. 
    #

rule make_idf_all:
  input:
    expand("<models_loc>/{sample}/run.idf",  sample=get_eplus_ready_samples)
