from typing import NamedTuple
from tabulate import tabulate
from dataframely import LazyFrame
from utils4plans.io import write_json
from msd2.paths import DynamicPaths
from msd2.readin.filters import (
    all_unit_ids,
    sufficient_areas_unit_ids,
    unique_unit_ids,
    valid_geom_only_unit_ids,
)
from msd2.readin.interfaces import MSDSchema, get_size_of_unit_id_df
from msd2.readin.utils import access_dataset


class DatasetSummary(NamedTuple):
    all_unit_ids: int
    valid_geoms: int
    sufficient_areas: int
    unique_plans: int

    def print(self):
        tabulate(self._asdict())


def write_unit_ids(df: LazyFrame[MSDSchema]):
    unique_ids = df.unique(subset=["unit_id"]).collect().get_column("unit_id").to_list()
    write_json(unique_ids, DynamicPaths.msd_unit_ids)


def write_all_msd_ids():
    df = access_dataset()
    write_unit_ids(df)


def summarize_dataset():
    df = access_dataset()
    summary = list(
        map(
            lambda fx: get_size_of_unit_id_df(fx(df)),
            [
                all_unit_ids,
                valid_geom_only_unit_ids,
                sufficient_areas_unit_ids,
                unique_unit_ids,
            ],
        )
    )
    ds = DatasetSummary(*summary)
    ds.print()
    return ds


if __name__ == "__main__":
    summarize_dataset()
