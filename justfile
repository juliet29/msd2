welcome:
  echo 'Welcome to just!'


update-deps:
  ../../scripts/pull_modules.sh

output := 'static/_04_temp/workflow/outputs'
plan := '97837'
dir := join(output, plan)

outjson := "out.json"
outpng:= "out.png"

# Fixing geometry 

trial-xplan: update-deps
  uv run preproc plan "X" {{dir}}/simplify/{{outjson}} {{dir}}/xplan/{{outpng}} {{dir}}/xplan/{{outjson}}

trial-xmove: update-deps
  uv run preproc move "X" {{dir}}/xplan/{{outjson}} {{dir}}/xmove/{{outpng}} {{dir}}/xmove/{{outjson}}


generate:
  uv run cli generate-input-files 30

trial-all:
  uv run snakemake -c 3 -k all

trial-some:
  uv run snakemake -c 3 -k some


# Evaluating geometry fixes 

find-ortho-only:
  ./scripts/ortho_only.sh

show-ortho-only:
  ./scripts/ortho_only.sh | xargs -I {} kitty icat {}/rotate/out.png

summarize:
  ./scripts/summary.sh



# Running Eplus models 
create-idf case run:
  uv run cli create-idf {{case}} {{run}}
