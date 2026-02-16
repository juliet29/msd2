
from snakemake.utils import min_version
min_version("6.0")

include: "common.smk"
configfile: "config/test.yaml"

polyfix_path = "../../../../polyfix/workflow/rules/cleanup.smk" # TODO in production, use github

polyfix_github = github("juliet29/polyfix", path="workflow/rules/cleanup.smk", tag="v0.1.6")

module polyfix:
    snakefile: polyfix_github
    config: config

use rule * from polyfix as polyfix_*
 
use rule rotate from polyfix as polyfix_rotate with:
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
