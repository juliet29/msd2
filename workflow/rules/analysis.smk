# analysis

configfile: "config/test.yaml"
include: "common.smk"

rule make_data: 
  input: 
    "<models_loc>/{sample}/run.idf",
    "<models_loc>/{sample}/results/eplusout.sql"
  output:
    "<models_loc>/{sample}/analysis/data.nc"
  shell: 
    "uv run msd create-data {input} {output}"


rule make_data_all:
  input:
    expand("<models_loc>/{sample}/analysis/data.nc",  sample=get_analysis_ready_samples)


rule make_metrics: 
  input: 
    "<models_loc>/{sample}/run.idf",
  output:
    "<models_loc>/{sample}/analysis/metrics.csv"
  shell: 
    "uv run msd create-metrics {input} {output}"


rule make_metrics_all:
  input:
    expand("<models_loc>/{sample}/analysis/metrics.csv",  sample=get_analysis_ready_samples)


rule summarize_metrics:
  input:
    paths=expand("<models_loc>/{sample}/analysis/metrics.csv",  sample=get_analysis_ready_samples)
  output:  
    outpath="<results_loc>/metrics/out.csv",
  shell:
    "uv run msd create-summary-metrics {input.paths} --outpath {output.outpath}"

rule summarize_data:
  input:
    paths=expand("<models_loc>/{sample}/analysis/data.nc",  sample=get_analysis_ready_samples)
  output:  
    daypath="<results_loc>/data/day/out.csv",
    nightpath="<results_loc>/data/night/out.csv"
  shell:
    "uv run msd create-summary-data {input.paths} --daypath {output.daypath} --nightpath {output.nightpath}"
# rule make_plots:
#   input: 
#     "<models_loc>/{sample}/run.idf",
#     "<models_loc>/{sample}/results/eplusout.sql"
#   output:
#     "<models_loc>/{sample}/analysis/data.nc"
#   shell: 
#     "uv run msd create-data {input} {output}"
