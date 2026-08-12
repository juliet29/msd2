from typing import cast

from icecream import ic
from polyfix.geometry.layout import Layout
from polyfix.geometry.vectors import DirectionNames

from msd2.geom.interfaces import Edge


def rotate(layout: Layout, entrance_door_edge: Edge):
    # get surface..
    e = entrance_door_edge
    domain = layout.get_domain(e.a)
    drn_name = cast(DirectionNames, e.b.lower())
    surface = domain.get_surface(drn_name)
    ic(surface.name, surface.parallel_axis)

    return surface

    pass
