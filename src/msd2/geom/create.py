from pathlib import Path

import polars as pl
import shapely as sp
from dataframely import DataFrame
from polyfix.geometry.ortho import FancyOrthoDomain
from polyfix.layout.interfaces import Layout
from polyfix.pydantic_models import layout_to_model

# TODO: depend on utils4plans for many of these if possible?
#
from utils4plans.io import write_json

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


def df_unit_to_room_data(df: DataFrame[MSDSchema], drop_balconies: bool = True):
    area_df = df.filter(pl.col("entity_type") == "area")
    rooms = make_room_data(MSDSchema.validate(area_df))
    if drop_balconies:
        return [i for i in rooms if "Balcony" not in i.entity_subtype]
    return rooms


def write_room_data_to_json_as_layout(rooms: list[RoomData], path: Path):
    def room_data_to_layout(rooms: list[RoomData]):
        filtered_rooms = [i for i in rooms if "balcony" not in i.name]
        doms = map(lambda x: FancyOrthoDomain(x.coords, x.name), filtered_rooms)
        return Layout(list(doms))

    layout = room_data_to_layout(rooms)
    data = layout_to_model(layout).model_dump()
    write_json(data, path)


def write_unit(unit_df: DataFrame[MSDSchema], path: Path):
    rooms = df_unit_to_room_data(unit_df)
    write_room_data_to_json_as_layout(rooms, path)
