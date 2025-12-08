from typing import NamedTuple
from utils4plans.geom import Coord
from polymap.geometry.ortho import FancyOrthoDomain
import shapely as sp


class RoomData(NamedTuple):
    entity_type: str
    entity_subtype: str
    height: int
    id: int
    poly: sp.Polygon

    def __post_init__(self):
        assert self.entity_type == "area"

    def __rich_repr__(self):
        yield "entity_subtype", self.entity_subtype
        yield "id", self.id

    @property
    def name(self):
        return f"{self.entity_subtype.lower()}_{self.id}"  # TODO do the names have to be independent? -> maybe have also a type?

    # @property
    # def room(self):
    #     return Room(self.id, self.name, self.domain, self.height)

    @property
    def coords(self):
        return [Coord(*i) for i in self.poly.exterior.normalize().coords]

    # @property
    # def tuple_coords(self):
    #     return [Coord(*i).as_tuple for i in self.poly.exterior.normalize().coords]

    @property
    def ortho_domain(self):
        return FancyOrthoDomain(self.coords)

    # @property
    # def is_orthogonal(self):
    #     return self.ortho_domain.is_orthogonal
