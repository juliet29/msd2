import polars as pl
from utils4plans.io import read_json
from msd2.paths import DynamicPaths
from msd2.readin.interfaces import MSDSchema, UnitIDSchema
from dataframely import DataFrame, LazyFrame
import shapely as sp
import warnings
from msd2.config import NUM_SAMPLES, SEED
import numpy as np


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


def valid_geom_only_unit_ids(df: LazyFrame[MSDSchema]) -> DataFrame[UnitIDSchema]:
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
        .select(pl.col("unit_id"))
    )
    return UnitIDSchema.validate(res)


def sufficient_areas_unit_ids(df: LazyFrame[MSDSchema]) -> DataFrame[UnitIDSchema]:
    res = (
        df.pipe(filter_to_areas)
        .group_by("unit_id")
        .agg(pl.col("geom").len().alias("num_of_area"))
        .filter(pl.col("num_of_area") > 1)
        .select(pl.col("unit_id"))
    )
    return UnitIDSchema.validate(res)


def unique_unit_ids(df: LazyFrame[MSDSchema]) -> DataFrame[UnitIDSchema]:
    res = (
        df.group_by("plan_id").agg(pl.col("unit_id").first()).select(pl.col("unit_id"))
    )
    return UnitIDSchema.validate(res)


# TODO this should be elsewhere..
#
def all_unit_ids(df: LazyFrame[MSDSchema]):
    res = df.select(pl.col("unit_id")).unique().collect()
    return res
    # return UnitIDSchema.validate(res)


def sample_unit_ids(
    df: LazyFrame[MSDSchema], num_samples: int = NUM_SAMPLES, seed: int = SEED
) -> DataFrame[UnitIDSchema]:
    rng = np.random.default_rng(seed)
    unique_unit_ids: list[int] = read_json(DynamicPaths.msd_unit_ids)
    sample_ids = rng.choice(unique_unit_ids, size=num_samples, replace=False)
    res = df.select(
        pl.col("unit_id").gather(sample_ids)
    ).collect()  # this should actually return a lazyframe which the others will use..

    return UnitIDSchema.validate(res)
