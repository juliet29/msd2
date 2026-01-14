from pathlib import Path

from polymap.geometry.ortho import FancyOrthoDomain
from replan2eplus.geometry.coords import Coord
from replan2eplus.geometry.ortho_domain import OrthoDomain
from replan2eplus.ops.zones.user_interface import Room
from utils4plans.io import read_json
from msd2.config import ROOM_HEIGHT
from polymap.json_interfaces import LayoutModel


# class GeomRoom(BaseModel):
#     name: str
#     id: int
#     coords: CoordsType
#
#     @property
#     def ortho_domain(self):
#         coords = map(lambda x: Coord(*x), self.coords)
#         return OrthoDomain(list(coords))
#
#     @property
#     def as_ezcase_room(self):
#         return Room(self.id, self.name, self.ortho_domain, ROOM_HEIGHT)
#
#     @property
#     def polymap_ortho_domain(self):
#         coords = coords_type_list_to_coords(self.coords)
#         return FancyOrthoDomain(coords, self.name)
#


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


# class GeomPlan(BaseModel):
#     rooms: list[GeomRoom]
#
#     @property
#     def ezcase_rooms(self):
#         res = map(lambda x: x.as_ezcase_room, self.rooms)
#         return list(res)
#
#     @property
#     def layout(self):
#         res = map(lambda x: x.polymap_ortho_domain, self.rooms)
#         return Layout(list(res))
#


def read_layout_to_ezcase_rooms(path: Path):
    data = read_json(path)
    geom_plan = GeomPlan.model_validate(data)
    return geom_plan.ezcase_rooms


# def read_geoms_to_layout(path: Path):
#     data = read_json(path)
#     geom_plan = GeomPlan.model_validate({"rooms": data})
#
#     return geom_plan.layout
