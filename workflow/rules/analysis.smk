# analysis

configfile: "config/test.yaml"
def get_analysis_ready_samples(wildcards):
  loc = Path(config["pathvars"]["models_loc"])
  path = loc / "{sample}" / "results/eplusout.sql" 

  samples, = glob_wildcards(path)
  return samples

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
# rule make_plots:
#   input: 
#     "<models_loc>/{sample}/run.idf",
#     "<models_loc>/{sample}/results/eplusout.sql"
#   output:
#     "<models_loc>/{sample}/analysis/data.nc"
#   shell: 
#     "uv run msd create-data {input} {output}"
