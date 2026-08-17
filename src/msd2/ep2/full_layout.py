from dataclasses import dataclass
from pathlib import Path

import polars as pl
from dataframely import DataFrame
from polyfix.geometry.vectors import CardinalDirections
from polyfix.main.main_class import read_layout_from_path
from utils4plans.lists import get_unique_one

from msd2.geom.create import make_connection_data, make_room_data
from msd2.geom.exteriors import arrange_exteriors, make_edge_connections
from msd2.geom.interiors import extract_interior_edges
from msd2.geom.rotate import (
    calculate_angle_to_goal_orientation,
    rotate_edges,
    rotate_layout,
)
from msd2.readin.interfaces import MSDSchema


class OpeningVocab:
    entrance_door = "Entrance Door"
    window = "Window"


@dataclass  ## cant be dataclass anymore.. needs to be a proper classs
class FullLayout:
    def __init__(
        self,
        path_to_geom: Path,
        path_to_angle: Path,
        unit_id: int,
        df: DataFrame[MSDSchema],  # trimmed df
    ):
        self.path_to_geom = path_to_geom
        self.path_to_angle = path_to_angle
        self.unit_id = unit_id
        self.df = df
        self.goal_direction = CardinalDirections.SOUTH

        # TODO: these could potentially all be grouped or
        self.layout = self.make_layout()
        self.connections = self.make_connections()
        self.interior_edges = self.make_interior_edges()

        # TO BE COMPUTED:
        self.angle = None
        self.entrance_door_edge = None
        self.window_edges = []

    def __repr__(self) -> str:
        d = {
            "n_domains": len(self.layout.domains),
            "n_connections": len(self.connections),
        }
        return f"FullLayout({d})"

    def make_layout(self):
        return read_layout_from_path(self.path_to_geom)

    def make_connections(self):
        # reading this from the df..  / may be filterd, or may not be yet..

        connection_df = self.df.filter(pl.col("entity_type") == "opening")
        connections = make_connection_data(MSDSchema.validate(connection_df))
        return connections

    def make_interior_edges(self):
        # rooms.json is written for the process of geom fixing..
        # going to re-read it here for on the fly door and window assignment
        room_data = make_room_data(self.df)
        doors = [i for i in self.connections if i.conn_type == "Door"]
        # TODO: raise exception if no doors
        return extract_interior_edges(room_data, doors)

    def orient_exteriors(self):
        cs = [
            i
            for i in self.connections
            if i.conn_type == OpeningVocab.entrance_door
            or i.conn_type == OpeningVocab.window
        ]
        rotated_conns, angle = arrange_exteriors(cs, self.path_to_angle)
        # project to make connection
        edges = make_edge_connections(self.path_to_geom, rotated_conns)

        self.rotated_conns = rotated_conns
        self.exterior_edges = edges
        self.door_0 = get_unique_one(
            self.exterior_edges, lambda x: x.conn == OpeningVocab.entrance_door
        )
        self.window_0 = [
            i for i in self.exterior_edges if i.conn == OpeningVocab.window
        ]

    def calculate_final_orient_angle(self):
        self.angle = calculate_angle_to_goal_orientation(
            self.layout, self.door_0, self.goal_direction
        )

    def orient_layout(self):
        assert self.angle is not None
        self.oriented_layout = rotate_layout(self.layout, self.angle)

        # rotate the entire geometry and edge based on ed location..

    def orient_exteriors_final(self):
        assert self.angle is not None
        rotate_edges(self.layout, self.angle, self.window_0)

    # def make_window_edges(self):
    #     assert self.angle is not None
    #     assert self.entrance_door_edge is not None
    #
    #     window_conns = [
    #         i for i in self.connections if i.conn_type == OpeningVocab.window
    #     ]
    #     rotated_connections, _ = arrange_exteriors(window_conns, self.angle)
    #     edges = make_edge_connections(self.path_to_geom, rotated_connections)
    #     self.window_edges = edges
    #
    # @property
    # def windows(self):
    #     return [i for i in self.exterior_edges if i.conn == "Window"]
    #
    # @property
    # def entrance_door(self):
    #     return get_unique_one(self.exterior_edges, lambda x: x.conn == "Entrance Door")
