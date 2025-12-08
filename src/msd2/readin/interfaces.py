import dataframely as dy
from dataframely import DataFrame


class MSDSchema(dy.Schema):
    apartment_id = dy.String(nullable=False)
    site_id = dy.Int64(nullable=False)
    building_id = dy.Int64(nullable=False)
    plan_id = dy.Int64(nullable=False)
    floor_id = dy.Int64(nullable=False)
    unit_id = dy.Float64(nullable=False)
    area_id = dy.Float64(nullable=False)
    unit_usage = dy.String(nullable=False)
    entity_type = dy.String(nullable=False)
    entity_subtype = dy.String(nullable=False)
    geom = dy.String(nullable=False)
    elevation = dy.Float64(nullable=False)
    height = dy.Float64(nullable=False)
    zoning = dy.String(nullable=False)
    roomtype = dy.String(nullable=False)


class UnitIDSchema(dy.Schema):
    unit_id = dy.Float64(nullable=False)


def get_size_of_unit_id_df(df: DataFrame[UnitIDSchema]):
    return df.get_column("unit_id").len()
