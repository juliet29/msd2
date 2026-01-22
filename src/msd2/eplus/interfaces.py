from pathlib import Path
from typing import Iterable, Literal, NamedTuple

from polymap.geometry.ortho import FancyOrthoDomain
from polymap.pydantic_models import LayoutModel
from replan2eplus.geometry.coords import Coord
from replan2eplus.geometry.ortho_domain import OrthoDomain
from replan2eplus.ops.subsurfaces.interfaces import Edge, Location
from replan2eplus.ops.subsurfaces.user_interfaces import (
    Detail,
    Dimension,
    EdgeGroup,
    EdgeGroupType,
)
from replan2eplus.ops.zones.user_interface import Room
from utils4plans.io import read_json

from msd2.config import ROOM_HEIGHT
from msd2.geom.interfaces import MSDEdgeModel, MSDEdgesModel


class GeomPlan(LayoutModel):
    @property
    def ezcase_rooms(self):
        def domain_to_room(id: int, dom: FancyOrthoDomain):
            coords = map(lambda x: Coord(*x), dom.coords)
            ortho_dom = OrthoDomain(list(coords))
            return Room(id, dom.name, ortho_dom, ROOM_HEIGHT, reverse_coords=True)

        layout = self.to_layout()
        rooms = [domain_to_room(ix, i) for ix, i in enumerate(layout.domains)]
        return rooms


DETAIL_TYPES = Literal["window", "door"]


def to_edge_group(
    edges: Iterable[MSDEdgeModel], detail: DETAIL_TYPES, type_: EdgeGroupType
):
    ep_edges = [Edge(i.a, i.b) for i in edges]
    return EdgeGroup(ep_edges, detail, type_)


class IncomingEdgeGroups(NamedTuple):
    exterior_door: Iterable[MSDEdgeModel]
    interior_door: Iterable[MSDEdgeModel]
    window: Iterable[MSDEdgeModel]
    airboundary: Iterable[MSDEdgeModel]

    def exterior_door_edges(self):
        return to_edge_group(self.exterior_door, "door", "Zone_Direction")

    def interior_door_edges(self):
        return to_edge_group(self.interior_door, "door", "Zone_Zone")

    def window_edges(self):
        return to_edge_group(self.window, "window", "Zone_Direction")

    def airboundary_edges(self):
        return to_edge_group(
            self.airboundary, "door", "Zone_Zone"
        )  # TODO: this might be a special type


class IncomingEgdes(MSDEdgesModel):
    def distinguish_edge_group(self):
        ext = filter(lambda x: x.conn == "Entrance Door", self.edges)
        inte = filter(lambda x: x.conn == "Door", self.edges)
        window = filter(lambda x: x.conn == "Window", self.edges)
        airboundary = filter(lambda x: x.conn == "Passage", self.edges)
        return IncomingEdgeGroups(ext, inte, window, airboundary)


# class EdgeGroupModel(BaseModel):
#     edges: list[tuple[str, str]]
#     detail: str
#     type_: EdgeGroupType
#
#     @property
#     def edge_group(self):
#         edges = map(lambda x: Edge(*x), self.edges)
#         return EdgeGroup(list(edges), self.detail, self.type_)


def read_layout_to_ezcase_rooms(path: Path):
    data = read_json(path)
    geom_plan = GeomPlan.model_validate(data)
    return geom_plan.ezcase_rooms


def make_details():
    door_detail = Detail(
        Dimension(width=10, height=ROOM_HEIGHT * 0.7),
        location=Location(
            "bm", "SOUTH", "SOUTH"
        ),  # TODO: create list of reasonable defaults, so dont have to think about this..
        type_="Door",
    )
    window_detail = Detail(
        Dimension(width=10, height=ROOM_HEIGHT * 0.5),
        location=Location("mm", "CENTROID", "CENTROID"),
        type_="Window",
    )

    detail_map: dict[DETAIL_TYPES, Detail] = {
        "window": window_detail,
        "door": door_detail,
    }
    return detail_map


def read_edges_to_ezcase_edges(path: Path):
    data = read_json(path)
    edges = MSDEdgesModel.model_validate(data).edges

    def to_edge_group(
        edge: list[MSDEdgeModel], detail: DETAIL_TYPES, type_: EdgeGroupType
    ):
        edges = [Edge(i.a, i.b) for i in edge]
        return EdgeGroup(edges, detail, type_)

    exterior_door_edges = [i for i in edges if i.conn == "Entrance Door"]
    interior_door_edges = [i for i in edges if i.conn == "Door"]
    window_edges = [i for i in edges if i.conn == "Window"]
    airboundary_edges = [i for i in edges if i.conn == "Passage"]

    return edges
