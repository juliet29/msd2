
include: "common.smk"
configfile: "config/test.yaml"

rule make_graph: 
  input: 
    "<models_loc>/{sample}/run.idf",
    "<models_loc>/{sample}/results/eplusout.sql"
  output:
    "<models_loc>/{sample}/graph/graph.pickle"
  shell: 
    "uv run msd create-graph {input} {output}"

rule make_graph_figure: 
  input: 
    "<models_loc>/{sample}/graph/graph.pickle",
  output:
    "<results_loc>/figures/graph_node_volume_edge_flow/{sample}.png"
  shell: 
    "uv run msd create-graph-figure {input} {output}"



rule make_graph_all:
  input:
    expand("<models_loc>/{sample}/graph/graph.pickle",  sample=get_analysis_ready_samples)

rule make_graph_figure_all:
  input:
    expand("<results_loc>/figures/graph_node_volume_edge_flow/{sample}.png",  sample=get_analysis_ready_samples)
