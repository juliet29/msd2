from pathlib import Path
import kagglehub
import polars as pl
from dataframely import LazyFrame
from kagglehub import KaggleDatasetAdapter

from loguru import logger
from msd2.readin.interfaces import MSDSchema


def access_dataset() -> LazyFrame[MSDSchema]:
    file_path = "mds_V2_5.372k.csv"

    lf = kagglehub.dataset_load(
        KaggleDatasetAdapter.POLARS,
        "caspervanengelenburg/modified-swiss-dwellings",
        file_path,
    )

    return MSDSchema.cast(lf)


def get_ids_by_indices(path_to_valid_ids: Path, start_ix: int, num_samples: int):
    df = pl.read_csv(path_to_valid_ids).slice(offset=start_ix, length=num_samples)
    res = df.to_series().cast(pl.Int64).to_list()
    logger.info(f"Unit IDs in [{start_ix}:{start_ix+num_samples}]: {res}")
    return res


def access_datasets_by_unit_ids(
    unit_ids: list[float] | list[int],
) -> LazyFrame[MSDSchema]:
    res = access_dataset().filter(pl.col("unit_id").is_in(unit_ids))

    return MSDSchema.cast(res)
