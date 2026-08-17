from typing import cast, get_args

from icecream import ic
from loguru import logger
from polyfix.geometry.layout import Layout
from polyfix.geometry.ortho import FancyOrthoDomain
from polyfix.geometry.vectors import CardinalDirections, Direction, DirectionNames
from polyfix.rotate.utils import angle_between_vectors
from shapely import MultiPolygon, affinity, get_parts, set_precision

from msd2.geom.angle import RadianAngle, VectorPair
from msd2.geom.interfaces import Edge


def rotate_layout(layout: Layout, angle: float):
    multipolygon = MultiPolygon([i.polygon for i in layout.domains])
    rotated = affinity.rotate(multipolygon, angle, use_radians=True)
    prec = [set_precision(i, grid_size=1e-8) for i in get_parts(rotated)]

    # ic(len(shapely.get_parts(prec)), len(shapely.get_parts(rotated)))
    new_domains = [
        FancyOrthoDomain.from_shapely_polygon(new_poly, dom.name)
        for new_poly, dom in zip(prec, layout.domains)
    ]
    return Layout(new_domains)


# TODO: promote
def get_surface_by_edge(layout: Layout, e: Edge):
    domain = layout.get_domain(e.a)
    drn_name = cast(DirectionNames, e.b.lower())
    assert drn_name in get_args(DirectionNames), f"{drn_name} not in {DirectionNames}"
    surface = domain.get_surface(drn_name)
    return surface


def rotate_layout_by_entrance_door(
    layout: Layout,
    entrance_door_edge: Edge,
    GOAL_DIRECTION: Direction = CardinalDirections.SOUTH,
) -> tuple[Layout, float, Edge]:
    # get surface..
    e = entrance_door_edge
    gd = GOAL_DIRECTION

    surface = get_surface_by_edge(layout, e)

    if surface.direction == gd:
        return layout, 0.0, e

    # TODO: make this take function take Vector
    surface_vector = surface.direction.aligned_vector
    angle = angle_between_vectors(gd.aligned_vector, surface_vector)  # pyright: ignore[reportArgumentType]
    angle = VectorPair.from_geom_vectors(
        surface_vector, gd.aligned_vector
    ).directed_angle
    ic(angle, surface.vector.norm(), surface_vector)
    logger.info(
        f"Converting {surface.direction.name} to {gd.name}. Rotating layout by {RadianAngle(angle)} radians. "
    )
    assert isinstance(angle, float)

    new_layout = rotate_layout(layout, angle)

    # update edge also
    new_e = e._replace(
        b=gd.name
    )  # TODO: add some assertion / simplify the case this might have..
    return new_layout, angle, new_e


# TODO: check that precieion does not introduce errors..
