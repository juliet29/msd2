from math import degrees
from typing import cast

import shapely
from icecream import ic
from loguru import logger
from polyfix.geometry.layout import Layout
from polyfix.geometry.ortho import FancyOrthoDomain
from polyfix.geometry.vectors import CardinalDirections, Direction, DirectionNames
from polyfix.rotate.utils import angle_between_vectors
from shapely import MultiPolygon, affinity, get_parts, set_precision

from msd2.geom.interfaces import Edge


def rotate_layout_by_entrance_door(
    layout: Layout,
    entrance_door_edge: Edge,
    GOAL_DIRECTION: Direction = CardinalDirections.SOUTH,
):
    # get surface..
    e = entrance_door_edge
    gd = GOAL_DIRECTION

    domain = layout.get_domain(e.a)
    drn_name = cast(DirectionNames, e.b.lower())
    surface = domain.get_surface(drn_name)

    if surface.direction == gd:
        return str(layout)

    # TODO: make this take function take Vector

    angle = angle_between_vectors(gd.aligned_vector, surface.direction.aligned_vector)  # pyright: ignore[reportArgumentType]
    ic(angle, surface.vector.norm(), surface.direction.aligned_vector)
    logger.info(
        f"Converting {surface.direction.name} to {gd.name}. Rotating layout by {degrees(angle)}º. "
    )

    multipolygon = MultiPolygon([i.polygon for i in layout.domains])
    rotated = affinity.rotate(multipolygon, angle, use_radians=True)
    prec = [set_precision(i, grid_size=1e-8) for i in get_parts(rotated)]

    ic(len(shapely.get_parts(prec)), len(shapely.get_parts(rotated)))
    new_domains = [
        FancyOrthoDomain.from_shapely_polygon(new_poly, dom.name)
        for new_poly, dom in zip(prec, layout.domains)
    ]
    return str(Layout(new_domains))


# TODO: check that precieion does not introduce errors..
