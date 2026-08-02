## dataset -> holds pipeline for  analyzing all cases..


# TODO: class for storing all locations


from pathlib import Path

from msd2.geom.io import write_unit
from msd2.readin.downselect import find_and_write_valid_unit_ids
from msd2.run.dataset_paths import DatasetPaths


class Dataset:
    def __init__(self, save_loc: Path) -> None:
        self.root = save_loc
        self.unit_ids: list[int] = []

        pass

    @property
    def paths(self):
        return DatasetPaths(self.root)

    def download(self):
        pass  # access the dataset, choose the correct unit_ids, move raw geometry to folder ~ may still be a dataframe at this point

    def downselect(self):
        valid_ids = find_and_write_valid_unit_ids(self.paths.unit_ids_csv)
        self.unit_ids = valid_ids

    def pre_process(self):
        for id in self.unit_ids:
            # TODO tdqm? try exvep? only return succesful ids..
            write_unit(id, self.paths.preprocessed_case_paths(str(id)))
        # make ready for polyfix
        pass

    def get(self, ix: int):
        return self.unit_ids[ix]

    def __len__(self):
        return len(self.unit_ids)


class DataLoader:
    def __init__(self, dataset: Dataset, batch_size: int) -> None:
        self.dataset = dataset
        assert dataset.unit_ids
        self.batch_size = batch_size
        self.map = self.map_ids()

    def map_ids(self):
        def map_ix(x: int):
            return ((x - 1) // self.batch_size) + 1

        return {unit_ix: map_ix(unit_ix) for unit_ix in self.dataset.unit_ids}

    def get_batch_by_ix(self, ix: int):
        return [k for k, v in self.map.items() if v == ix]

    def __len__(self):
        return len(set(self.map.values()))
