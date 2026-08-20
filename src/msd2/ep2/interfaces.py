from typing import Iterable, Literal, NamedTuple

from plan2eplus.geometry.coords import Coord
from plan2eplus.geometry.ortho_domain import OrthoDomain
from plan2eplus.ops.subsurfaces.interfaces import Edge, Location
from plan2eplus.ops.subsurfaces.user_interfaces import (
    Detail,
    Dimension,
    EdgeGroup,
    EdgeGroupType,
)
from plan2eplus.ops.zones.user_interface import Room
from polyfix.geometry.layout import Layout
from polyfix.geometry.ortho import FancyOrthoDomain

from msd2.ep2.full_layout import OrientedLayout
from msd2.geom.interfaces import Edge as MSDEdge


def layout_to_ezcase_rooms(layout: Layout, room_height: float):
    def domain_to_room(id: int, dom: FancyOrthoDomain):
        coords = map(lambda x: Coord(*x), dom.coords)
        ortho_dom = OrthoDomain(list(coords))
        return Room(id, dom.name, ortho_dom, room_height, reverse_coords=True)

    rooms = [domain_to_room(ix, i) for ix, i in enumerate(layout.domains)]
    return rooms


DETAIL_TYPES = Literal["window", "door"]


def to_edge_group(edges: Iterable[MSDEdge], detail: DETAIL_TYPES, type_: EdgeGroupType):
    if type_ == "Zone_Direction":
        ep_edges = [Edge(i.a, i.b.upper()) for i in edges]
    else:
        ep_edges = [Edge(i.a, i.b) for i in edges]
    return EdgeGroup(ep_edges, detail, type_)


class DistinguishedEdgeGroups(NamedTuple):
    exterior_door: Iterable[MSDEdge]
    interior_door: Iterable[MSDEdge]
    window: Iterable[MSDEdge]
    airboundary: Iterable[MSDEdge]

    @property
    def exterior_door_edges(self):
        return to_edge_group(self.exterior_door, "door", "Zone_Direction")

    @property
    def interior_door_edges(self):
        return to_edge_group(self.interior_door, "door", "Zone_Zone")

    @property
    def window_edges(self):
        return to_edge_group(self.window, "window", "Zone_Direction")

    @property
    def airboundary_edges(self):
        return to_edge_group(
            self.airboundary, "door", "Zone_Zone"
        )  # TODO: this might be a special type

    @property
    def simple_edge_groups(self):
        return [self.interior_door_edges, self.window_edges]


def edges_to_ezcase_edge_groups(ol: OrientedLayout):
    return DistinguishedEdgeGroups(
        exterior_door=[ol.entrance_door],
        interior_door=ol.doors,
        window=ol.windows,
        airboundary=ol.passages,
    )


def make_details(room_height: float):
    door_detail = Detail(
        Dimension(width=10, height=room_height * 0.7),
        location=Location(
            "bm", "SOUTH", "SOUTH"
        ),  # TODO: create list of reasonable defaults, so dont have to think about this..
        type_="Door",
    )
    window_detail = Detail(
        Dimension(width=10, height=room_height * 0.5),
        location=Location("mm", "CENTROID", "CENTROID"),
        type_="Window",
    )

    detail_map: dict[DETAIL_TYPES, Detail] = {
        "window": window_detail,
        "door": door_detail,
    }
    return detail_map
