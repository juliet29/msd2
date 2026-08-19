from pathlib import Path
from typing import NamedTuple

from dataframely import DataFrame
from polyfix.geometry.ortho import FancyOrthoDomain
from polyfix.layout.interfaces import Layout
from polyfix.pydantic_models import layout_to_model

# TODO: depend on utils4plans for many of these if possible?
#
from utils4plans.io import write_json

from msd2.geom.create import df_unit_to_room_data
from msd2.geom.interfaces import RoomData
from msd2.readin.interfaces import MSDSchema


class CasePaths(NamedTuple):
    rooms: Path  # TODO simplify to just a path..


def write_room_data_to_json_as_layout(rooms: list[RoomData], path: Path):
    def room_data_to_layout(rooms: list[RoomData]):
        filtered_rooms = [i for i in rooms if "balcony" not in i.name]
        doms = map(lambda x: FancyOrthoDomain(x.coords, x.name), filtered_rooms)
        return Layout(list(doms))

    layout = room_data_to_layout(rooms)
    data = layout_to_model(layout).model_dump()
    write_json(data, path)


def write_unit(unit_df: DataFrame[MSDSchema], case_data: CasePaths):
    rooms = df_unit_to_room_data(unit_df)
    write_room_data_to_json_as_layout(rooms, case_data.rooms)

    # logger.success(f"Finished writing layout and edges for {unit_id} ")
