from typing import cast, get_args

from icecream import ic
from loguru import logger
from polyfix.geometry.layout import Layout
from polyfix.geometry.ortho import FancyOrthoDomain
from polyfix.geometry.vectors import CardinalDirections, Direction, DirectionNames
from shapely import MultiPolygon, affinity, get_parts, set_precision

from msd2.geom.angle import RadianAngle, Vector, VectorPair
from msd2.geom.interfaces import Edge


# TODO: promote
def get_surface_by_edge(layout: Layout, e: Edge):
    domain = layout.get_domain(e.a)
    drn_name = cast(DirectionNames, e.b.lower())
    assert drn_name in get_args(DirectionNames), f"{drn_name} not in {DirectionNames}"
    surface = domain.get_surface(drn_name)
    return surface


def calculate_angle_to_goal_orientation(
    layout: Layout,
    entrance_door_edge: Edge,
    GOAL_DIRECTION: Direction = CardinalDirections.SOUTH,
) -> float:
    e = entrance_door_edge
    gd = GOAL_DIRECTION

    surface = get_surface_by_edge(layout, e)

    if surface.direction == gd:
        return 0.0

    surface_vector = surface.direction.aligned_vector
    angle = VectorPair.from_geom_vectors(
        surface_vector, gd.aligned_vector
    ).directed_angle
    # ic(angle, surface.vector.norm(), surface_vector)
    logger.info(
        f"Converting {surface.direction.name} to {gd.name}. Rotating layout by {RadianAngle(angle)} radians. "
    )
    return angle


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


def rotate_edges(layout: Layout, angle: float, edges: list[Edge]):
    def handle(e: Edge):
        s = get_surface_by_edge(layout, e)
        surface_vector = s.direction.aligned_vector
        v = Vector.from_geom_vector(surface_vector)
        new_vec = RadianAngle(angle).apply_to_vector(v)
        ic(s.direction.name, new_vec)

    handle(edges[0])
