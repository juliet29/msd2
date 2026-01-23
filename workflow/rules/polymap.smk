
from snakemake.utils import min_version
min_version("6.0")

include: "common.smk"
configfile: "config/test.yaml"

polymap_path = "../../../../polymap/workflow/rules/cleanup.smk" # TODO in production, use github
# github_path = github("juliet29/polymap", path="workflow/Snakefile", branch="decimals")

module polymap:
    snakefile: polymap_path 
    config: config

use rule * from polymap as polymap_*
 
use rule rotate from polymap as polymap_rotate with:
  input: 
      "<output_loc>/{sample}/layout/out.json"


rule rotate_all:
  input: 
    expand("<output_loc>/{sample}/rotate/out.json",  sample=get_samples)


rule ortho_all:
  input: 
    expand("<output_loc>/{sample}/ortho/out.json",  sample=get_samples)

rule ymove_all:
  input: 
    expand("<output_loc>/{sample}/ymove/out.json",  sample=get_samples)
