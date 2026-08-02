from pathlib import Path
from typing import NamedTuple

import polars as pl
from loguru import logger
from rich import print
from rich.pretty import pretty_repr
from tabulate import tabulate
from utils4plans.io import make_dir

from msd2.readin.access import access_dataset
from msd2.readin.filters import (
    all_unit_ids,
    sufficient_areas_unit_ids,
    unique_unit_ids,
    valid_geom_only_unit_ids,
)


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
    logger.info(pretty_repr(ds))
    return ds


def find_and_write_valid_unit_ids(save_loc: Path):
    id_list = get_id_list()
    id_sets = [set(i) for i in id_list]
    s1, s2, s3, s4 = id_sets

    valid_ids = sorted(list(s1.intersection(s2, s3, s4)))

    # TODO: optionally save or not
    df = pl.DataFrame(data={"ids": valid_ids}).sort(by="ids")
    make_dir(save_loc)
    df.write_csv(save_loc)
    logger.success(f"Wrote file to {save_loc}")
    return [int(x) for x in valid_ids]  # or ids..

    # write_json(valid_ids, DynamicPaths.valid_ids_json, OVERWRITE=True)
