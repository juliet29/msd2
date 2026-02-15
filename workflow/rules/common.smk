
from msd2.readin.access import get_ids_by_indices

def get_samples(wildcards):
  return get_ids_by_indices(config["start_ix"], config["num_items"])

# TODO: add get-idf-ready samples from msd.smk
def get_analysis_ready_samples(wildcards):
  loc = Path(config["pathvars"]["models_loc"])
  path = loc / "{sample}" / "results/eplusout.sql" 

  samples, = glob_wildcards(path)
  return samples
