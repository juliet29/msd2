from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import polars as pl
from dataframely import DataFrame
from polyfix.geometry.layout import Layout
from polyfix.geometry.vectors import CardinalDirections
from polyfix.main.main_class import read_layout_from_path
from utils4plans.lists import get_unique_one

from msd2.geom.create import make_connection_data, make_room_data
from msd2.geom.exteriors import (
    arrange_exteriors,
    filter_duplicate_edges,
    make_edge_connections,
)
from msd2.geom.interfaces import Edge
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
    door = "Door"
    passage = "Passage"


class OrientedLayout(NamedTuple):
    layout: Layout
    windows: list[Edge]
    doors: list[Edge]
    passages: list[Edge]
    entrance_door: Edge


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
        connection_df = self.df.filter(pl.col("entity_type") == "opening")
        connections = make_connection_data(MSDSchema.validate(connection_df))
        return connections

    def make_interior_edges(self):
        # rooms.json is written for the process of geom fixing..
        # going to re-read it here for on the fly door and window assignment
        room_data = make_room_data(self.df)
        doors = [i for i in self.connections if i.conn_type == "Door"]
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
        edges = filter_duplicate_edges(edges)

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
        self.oriented_edges = rotate_edges(
            self.oriented_layout, self.angle, self.exterior_edges
        )

        self.door_1 = get_unique_one(
            self.oriented_edges, lambda x: x.conn == OpeningVocab.entrance_door
        )
        self.window_1 = [
            i for i in self.oriented_edges if i.conn == OpeningVocab.window
        ]

    def to_oriented_layout(self):
        self.orient_exteriors()
        self.calculate_final_orient_angle()
        self.orient_layout()
        self.orient_exteriors_final()
        doors = [i for i in self.interior_edges if i.conn == OpeningVocab.door]
        passages = [i for i in self.interior_edges if i.conn == OpeningVocab.passage]
        return OrientedLayout(
            self.oriented_layout, self.window_1, doors, passages, self.door_1
        )
