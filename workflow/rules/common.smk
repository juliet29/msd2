
from msd2.readin.access import get_ids_by_indices

def get_samples(wildcards):
  return get_ids_by_indices(config["start_ix"], config["num_items"])
