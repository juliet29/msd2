import polars as pl
from utils4plans.io import read_json
from msd2.paths import DynamicPaths
from msd2.readin.interfaces import MSDSchema
from dataframely import LazyFrame
import shapely as sp
import warnings
from msd2.config import NUM_SAMPLES, SEED
import numpy as np


# these first two are more utils..
def is_valid_geom(geom: str):
    p = sp.from_wkt(geom)
    if p.is_valid and p.geom_type == "Polygon":
        poly: sp.Polygon = p  # type: ignore
        if len(poly.interiors) == 0 and poly.area > 0:
            return True

    else:
        warnings.warn(f"Invalid geometry: {sp.is_valid_reason(p)}")
    return False


def filter_to_areas(df: LazyFrame[MSDSchema]) -> LazyFrame[MSDSchema]:
    res = df.filter(pl.col("entity_type") == "area")
    return MSDSchema.cast(res)


def get_unit_ids(df: pl.LazyFrame):
    return df.select(pl.col("unit_id")).collect().to_series().to_list()


def valid_geom_only_unit_ids(df: LazyFrame[MSDSchema]) -> list[int]:
    res = (
        df.pipe(filter_to_areas)
        .with_columns(
            pl.col("geom")
            .map_elements(is_valid_geom, return_dtype=pl.Boolean)
            .alias("is_valid_geom")
        )
        .group_by("unit_id")
        .agg(pl.col("is_valid_geom"))
        .filter(pl.col("is_valid_geom").list.all())
    )
    return get_unit_ids(res)


def sufficient_areas_unit_ids(df: LazyFrame[MSDSchema]) -> list[int]:
    res = (
        df.pipe(filter_to_areas)
        .group_by("unit_id")
        .agg(pl.col("geom").len().alias("num_of_area"))
        .filter(pl.col("num_of_area") > 1)
        .select(pl.col("unit_id"))
    )
    return get_unit_ids(res)


def unique_unit_ids(df: LazyFrame[MSDSchema]) -> list[int]:
    res = (
        df.group_by("plan_id").agg(pl.col("unit_id").first()).select(pl.col("unit_id"))
    )
    return get_unit_ids(res)


#
def all_unit_ids(df: LazyFrame[MSDSchema]):
    res = df.select(pl.col("unit_id")).unique()
    return get_unit_ids(res)
    # return UnitIDSchema.validate(res)


def sample_unit_ids(num_samples: int = NUM_SAMPLES, seed: int = SEED) -> list[int]:

    valid_unit_ids: list[int] = read_json(DynamicPaths.valid_ids_json)
    assert num_samples < len(
        valid_unit_ids
    ), f"N_samples={num_samples} > n_valid_ids {len(valid_unit_ids)}"

    rng = np.random.default_rng(seed)
    sample_ids = rng.choice(valid_unit_ids, size=num_samples, replace=False)

    return sorted(sample_ids.tolist())
