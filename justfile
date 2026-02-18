welcome:
  echo 'Welcome to just!'


update-poly:
  uv add /Users/julietnwagwuume-ezeoke/_UILCode/gqe-phd/fpopt/polymap

update-plan:
  uv add plan2eplus --upgrade-package plan2eplus 

update-replan-geomeppy:
  uv add ~/_UILCode/gqe-phd/fpopt/replan2eplus
  uv add ~/_UILCode/gqe-phd/fpopt/geomeppy
update-geomeppy:
  uv add ~/_UILCode/gqe-phd/fpopt/geomeppy

update-deps:
  uv add /Users/julietnwagwuume-ezeoke/_UILCode/gqe-phd/fpopt/replan2eplus
  uv add /Users/julietnwagwuume-ezeoke/_UILCode/gqe-phd/fpopt/utils4plans
  uv add /Users/julietnwagwuume-ezeoke/_UILCode/gqe-phd/fpopt/polymap




output := 'static/_04_temp/workflow/outputs'
plan := '97837'
dir := join(output, plan)

outjson := "out.json"
outpng:= "out.png"


# Utils 
set-out:
  set --path msd2out 'static/_04_temp/workflow/outputs'



# Evaluating geometry fixes 

find-ortho-only:
  ./scripts/ortho_only.sh

show-ortho-only:
  ./scripts/ortho_only.sh | xargs -I {} kitty icat {}/rotate/out.png

summarize folder:
  ./scripts/summary.sh {{folder}}


# -------------- TESTS of the CLI -------------


# Fixing geometry --------------------

trial-xplan: update-poly
  uv run preproc plan "X" {{dir}}/simplify/{{outjson}} {{dir}}/xplan/{{outpng}} {{dir}}/xplan/{{outjson}}

trial-xmove: update-poly
  uv run preproc move "X" {{dir}}/xplan/{{outjson}} {{dir}}/xmove/{{outpng}} {{dir}}/xmove/{{outjson}}


generate:
  uv run cli generate-input-files 30

trial-all:
  uv run snakemake -c 3 -k all

trial-some:
  uv run snakemake -c 3 -k some

trial-one case:
  uv run snakemake -c 1 -f {{output}}/{{case}}/xmove/{{outjson}}
  uv run snakemake -c 1 -f {{output}}/{{case}}/yplan/{{outjson}}
  uv run snakemake -c 1 -f {{output}}/{{case}}/ymove/{{outjson}}




# Running Eplus models ------------------
models_dir := "static/_03_models/snakemake/test"
trial-run-idf case:
  uv run msd run-idf --idf_path={{models_dir}}/{{case}}/out.idf --results_directory={{models_dir}}/{{case}}/results --schedules_directory={{models_dir}}/{{case}}/schedules --msd_config_path=msdconfig/test.yaml


