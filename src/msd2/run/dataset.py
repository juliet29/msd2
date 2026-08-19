from pathlib import Path

import polars as pl
from loguru import logger
from tqdm import tqdm

from msd2.geom.io import write_unit
from msd2.readin.access import PartitionedDataFrame
from msd2.readin.downselect import find_and_write_valid_unit_ids
from msd2.run.dataset_paths import DatasetPaths


class Dataset:
    def __init__(self, save_loc: Path) -> None:
        logger.info(f"Initializing dataset at {save_loc}")
        self.root = save_loc
        self._unit_ids: list[int] = []
        self.paths = DatasetPaths(self.root)
        self.partitioned_df = PartitionedDataFrame()

    def downselect(self, csv_path: Path | None = None, n: int | None = None):
        if csv_path:
            assert csv_path.exists()
            logger.info(f"Reading unit ids from {csv_path}")
            res: list[float] = pl.read_csv(csv_path).get_column("ids").to_list()
            valid_ids = [int(i) for i in res]

            # pl.read_csv(csv_path)
        else:
            logger.info("Finding valid unit ids")
            valid_ids = find_and_write_valid_unit_ids(self.paths.unit_ids_csv)
        self._unit_ids = valid_ids

        if n:
            self._unit_ids = valid_ids[:n]

    def pre_process(self):
        for id in tqdm(self._unit_ids, desc="pre-processing"):
            unit_df = self.partitioned_df.get_unit_df(id)
            if unit_df is None:
                logger.warning(f"Could not find data for {unit_df}")
                continue
            try:
                write_unit(unit_df, self.paths.preprocessed_case_tuples(id))
            except Exception as e:
                logger.error(f"Problem proccessing {unit_df}: {e}")

    @property
    def true_ids(self):
        # check pre-process folder
        return sorted(
            [int(i.name) for i in self.paths.pre_processed.iterdir() if i.is_dir()]
        )

    def get(self, ix: int):
        return self.true_ids[ix]

    def __len__(self):
        return len(self.true_ids)


class DataLoader:
    def __init__(self, dataset: Dataset, batch_size: int) -> None:
        self.dataset = dataset
        assert dataset.true_ids
        self.batch_size = batch_size
        self.map = self.map_ids()

    def map_ids(self):
        def map_ix(x: int):
            return (x) // self.batch_size

        return {unit_ix: map_ix(ix) for ix, unit_ix in enumerate(self.dataset.true_ids)}

    def get_batch_by_ix(self, ix: int):
        return [k for k, v in self.map.items() if v == ix]

    def __len__(self):
        return len(set(self.map.values()))
