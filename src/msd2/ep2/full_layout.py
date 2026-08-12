from dataclasses import dataclass
from pathlib import Path

import polars as pl
from dataframely import DataFrame
from polyfix.main.main_class import read_layout_from_path
from utils4plans.lists import get_unique_one

from msd2.geom.connectivity import extract_interior_edges
from msd2.geom.create import make_connection_data, make_room_data
from msd2.geom.new_windows import arrange_exteriors, make_edge_connections
from msd2.readin.interfaces import MSDSchema


@dataclass
class FullLayout:
    path_to_geom: Path
    path_to_angle: Path
    unit_id: int
    df: DataFrame[MSDSchema]  # trimmed df

    @property
    def layout(self):
        return read_layout_from_path(self.path_to_geom)

    @property
    def connections(self):
        # reading this from the df..  / may be filterd, or may not be yet..

        connection_df = self.df.filter(pl.col("entity_type") == "opening")
        connections = make_connection_data(MSDSchema.validate(connection_df))
        return connections

    @property
    def interior_edges(self):
        # rooms.json is written for the process of geom fixing..
        # going to re-read it here for on the fly door and window assignment
        room_data = make_room_data(self.df)
        doors = [i for i in self.connections if i.roomtype == "Door"]
        # TODO: raise exception if no doors
        return extract_interior_edges(room_data, doors)

    @property
    def exterior_edges(self):
        rotated_connections = arrange_exteriors(self.connections, self.path_to_angle)
        edges = make_edge_connections(self.path_to_geom, rotated_connections)
        return edges

    @property
    def windows(self):
        return [i for i in self.exterior_edges if i.conn == "Window"]

    @property
    def entrance_door(self):
        return get_unique_one(self.exterior_edges, lambda x: x.conn == "Exterior Door")
