import polars as pl
from msd2.readin.interfaces import MSDSchema
from dataframely import LazyFrame
import shapely as sp
import warnings


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
