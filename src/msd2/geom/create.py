import shapely as sp
import polars as pl
from dataframely import DataFrame

from msd2.geom.interfaces import ConnectionData, RoomData
from msd2.readin.interfaces import MSDSchema


def msd_geom_to_shapely(geom: str) -> sp.Polygon:
    geo = sp.from_wkt(geom)
    assert isinstance(geo, sp.Polygon)
    return geo


def make_room_data(df: DataFrame[MSDSchema]):
    rooms = [
        RoomData(
            row["entity_type"],
            row["entity_subtype"],
            row["roomtype"],
            row["height"],
            ix,
            msd_geom_to_shapely(row["geom"]),
        )
        for ix, row in enumerate(df.iter_rows(named=True))
    ]
    return rooms


def make_connection_data(df: DataFrame[MSDSchema]):
    connections = [
        ConnectionData(
            row["entity_type"],
            row["entity_subtype"],
            row["roomtype"],
            row["height"],
            ix,
            msd_geom_to_shapely(row["geom"]),
        )
        for ix, row in enumerate(df.iter_rows(named=True))
    ]
    return connections


def df_unit_to_room_and_connection_data(df: DataFrame[MSDSchema]):
    # assuming has already been filtered to the unit id..
    area_df = df.filter(pl.col("entity_type") == "area")
    connection_df = df.filter(pl.col("entity_type") == "opening")
    rooms = make_room_data(MSDSchema.validate(area_df))
    connections = make_connection_data(MSDSchema.validate(connection_df))
    return rooms, connections
