from pathlib import Path 

configfile: "config/test.yaml"



def get_eplus_ready_samples(wildcards):
  loc = Path(config["pathvars"]["output_loc"])
  json = "out.json"
  ymove_path = loc / "{sample}" / "ymove" /json

  samples, = glob_wildcards(ymove_path)
  return samples



rule make_idf:
  input:
    "<output_loc>/{sample}/edges/out.json", # edges
    "<output_loc>/{sample}/ymove/out.json" # corrected layout
  output:
    "<models_loc>/{sample}/out.idf" # TODO: turn to out.idf, or allow replan to just take the path 
  log:
    "<models_loc>/{sample}/out.log"
  shell:
    "uv run msd create-idf {input} {output} 2>{log}"
    # potentially, info about weather data also.. 
    #

rule make_idf_all:
  input:
    expand("<models_loc>/{sample}/out.idf",  sample=get_eplus_ready_samples)


rule run_idf: 
  input:
    "<models_loc>/{sample}/out.idf"
  output:
    directory("<models_loc>/{sample}/results")
  params:
    schedules="<models_loc>/{sample}/schedules"  
  log:
    "<models_loc>/{sample}/run.log"
  shell:
    "uv run msd run-idf {input} {output} '{params.schedules}' 2>{log}"

rule run_idf_all:
  input:
    expand("<models_loc>/{sample}/results",  sample=get_eplus_ready_samples)
