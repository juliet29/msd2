from pathlib import Path
from typing import Literal

from polymap.geometry.ortho import FancyOrthoDomain
from replan2eplus.geometry.coords import Coord
from replan2eplus.geometry.ortho_domain import OrthoDomain
from replan2eplus.ops.zones.user_interface import Room
from utils4plans.io import read_json
from msd2.config import ROOM_HEIGHT
from polymap.json_interfaces import LayoutModel
from replan2eplus.ops.subsurfaces.interfaces import Location
from replan2eplus.ops.subsurfaces.user_interfaces import (
    Detail,
    Dimension,
)
from pydantic import BaseModel
from replan2eplus.ops.subsurfaces.user_interfaces import (
    EdgeGroup,
    EdgeGroupType,
)
from replan2eplus.ops.subsurfaces.interfaces import Edge


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


class EdgeGroupModel(BaseModel):
    edges: list[tuple[str, str]]
    detail: str
    type_: EdgeGroupType

    @property
    def edge_group(self):
        edges = map(lambda x: Edge(*x), self.edges)
        return EdgeGroup(list(edges), self.detail, self.type_)


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

    detail_map: dict[Literal["window", "door"], Detail] = {
        "window": window_detail,
        "door": door_detail,
    }
    return detail_map
