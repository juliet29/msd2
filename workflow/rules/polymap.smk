
from snakemake.utils import min_version
min_version("6.0")


configfile: "config/test.yaml"
polymap_path = "../../../../polymap/workflow/rules/cleanup.smk" # TODO in production, use github
# github_path = github("juliet29/polymap", path="workflow/Snakefile", branch="decimals")

module polymap:
    snakefile: polymap_path 
    config: config

use rule * from polymap as polymap_*
 
use rule rotate from polymap as polymap_rotate with:
  input: 
      "<input_loc>/{sample}/layout.json"


rule test_rotate:
  input: 
    "<output_loc>/21063/rotate/out.json"
