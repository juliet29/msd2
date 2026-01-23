from typing import NamedTuple
import polars as pl
from rich import print
from tabulate import tabulate
from msd2.paths import DynamicPaths
from msd2.readin.filters import (
    all_unit_ids,
    sufficient_areas_unit_ids,
    unique_unit_ids,
    valid_geom_only_unit_ids,
)
from msd2.readin.access import access_dataset
from loguru import logger


class DatasetSummary(NamedTuple):
    all_unit_ids: int
    valid_geoms: int
    sufficient_areas: int
    unique_plans: int

    def print(self):
        data = [[k, v] for k, v in self._asdict().items()]
        t = tabulate(data)
        print(t)
        return t


def get_id_list():
    df = access_dataset()
    id_list = list(
        map(
            lambda fx: fx(df),
            [
                all_unit_ids,
                valid_geom_only_unit_ids,
                sufficient_areas_unit_ids,
                unique_unit_ids,
            ],
        )
    )
    return id_list


def summarize_dataset():
    id_list = get_id_list()
    ds = DatasetSummary(*[len(i) for i in id_list])
    logger.info(ds)
    return ds


def find_and_write_valid_unit_ids():
    id_list = get_id_list()
    id_sets = [set(i) for i in id_list]
    s1, s2, s3, s4 = id_sets

    valid_ids = list(s1.intersection(s2, s3, s4))
    df = pl.DataFrame(data={"ids": valid_ids}).sort(by="ids")
    df.write_csv(DynamicPaths.valid_ids_csv)
    logger.success(f"Wrote file to {DynamicPaths.valid_ids_csv}")
    # write_json(valid_ids, DynamicPaths.valid_ids_json, OVERWRITE=True)


if __name__ == "__main__":
    find_and_write_valid_unit_ids()
