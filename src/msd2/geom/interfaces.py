from typing import Literal, NamedTuple
from utils4plans.geom import Coord
from polymap.geometry.ortho import FancyOrthoDomain
import shapely as sp


ROOM_NAMES = Literal[
    "Bedroom",
    "Livingroom",
    "Kitchen",
    "Dining",
    "Corridor",
    "Stairs",
    "Storeroom",
    "Bathroom",
    "Balcony",
    "Structure",
    "Door",
    "Entrance Door",
    "Window",
]

CONNECTION_NAMES = Literal[
    "Door",
    "Entrance Door",
    "Window",
]


class RoomData(NamedTuple):
    entity_type: str
    entity_subtype: str
    roomtype: str
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

    @property
    def coords(self):
        return [Coord(*i) for i in self.poly.exterior.normalize().coords]

    @property
    def ortho_domain(self):
        return FancyOrthoDomain(self.coords)


class ConnectionData(NamedTuple):
    entity_type: Literal["opening"]
    entity_subtype: str
    roomtype: CONNECTION_NAMES
    height: int
    id: int

    poly: sp.Polygon

    @property
    def name(self):
        return f"{self.entity_subtype.lower()}_{self.id}"  # TODO do the names have to be independent? -> maybe have also a type?
