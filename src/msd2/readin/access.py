import kagglehub
import polars as pl
from dataframely import LazyFrame
from kagglehub import KaggleDatasetAdapter

from loguru import logger
from msd2.readin.filters import filter_to_areas
from msd2.readin.interfaces import MSDSchema

from utils4plans.io import read_json
from msd2.paths import DynamicPaths
from msd2.config import NUM_SAMPLES, SEED
import numpy as np


def access_dataset() -> LazyFrame[MSDSchema]:
    file_path = "mds_V2_5.372k.csv"

    lf = kagglehub.dataset_load(
        KaggleDatasetAdapter.POLARS,
        "caspervanengelenburg/modified-swiss-dwellings",
        file_path,
    )

    return MSDSchema.cast(lf)


def sample_unit_ids(num_samples: int = NUM_SAMPLES, seed: int = SEED) -> list[int]:

    valid_unit_ids: list[int] = read_json(DynamicPaths.valid_ids_json)
    assert num_samples < len(
        valid_unit_ids
    ), f"N_samples={num_samples} > n_valid_ids {len(valid_unit_ids)}"

    rng = np.random.default_rng(seed)
    sample_ids = rng.choice(valid_unit_ids, size=num_samples, replace=False)

    return sorted(sample_ids.tolist())


def get_ids_by_indices(start_ix: int, num_samples: int):
    df = pl.read_csv(DynamicPaths.valid_ids_csv).slice(
        offset=start_ix, length=num_samples
    )
    res = df.to_series().cast(pl.Int64).to_list()
    logger.info(f"Unit IDs in [{start_ix}:{start_ix+num_samples}]: {res}")
    return res


def access_sample_datasets_areas_only(
    num_samples: int = NUM_SAMPLES,
) -> LazyFrame[MSDSchema]:
    sample_ids = sample_unit_ids(num_samples)

    logger.info(f"Sampled IDs: {sample_ids}")
    res = (
        access_dataset()
        .pipe(filter_to_areas)
        .filter(pl.col("unit_id").is_in(sample_ids))
    )
    return MSDSchema.cast(res)


def access_random_sample_datasets(
    num_samples: int = NUM_SAMPLES,
) -> LazyFrame[MSDSchema]:
    sample_ids = sample_unit_ids(num_samples)

    logger.info(f"Sampled IDs: {sample_ids}")
    res = access_dataset().filter(pl.col("unit_id").is_in(sample_ids))
    return MSDSchema.cast(res)


def access_datasets_by_unit_ids(unit_ids: list[float]) -> LazyFrame[MSDSchema]:
    res = access_dataset().filter(pl.col("unit_id").is_in(unit_ids))

    return MSDSchema.cast(res)


def access_one_sample_dataset(
    sample_id: float | None = None, seed: int = SEED
) -> LazyFrame[MSDSchema]:
    if not sample_id:
        sample_id = sample_unit_ids(1, seed=seed)[0]
    print(f"Sampled ID: {sample_id}")
    res = access_dataset().filter(pl.col("unit_id") == sample_id)
    return MSDSchema.cast(res)
