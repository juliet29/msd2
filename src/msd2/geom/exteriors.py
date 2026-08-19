from pathlib import Path

import shapely
from loguru import logger
from polyfix.main.main_class import read_layout_from_path
from rich.pretty import pretty_repr
from shapely import (
    Geometry,
    LineString,
    MultiPolygon,
    STRtree,
    affinity,
    unary_union,
)
from utils4plans.io import read_json

from msd2.geom.interfaces import ConnectionData, Edge


# TODO: promote to interfaces
class EdgeProcessingError(Exception): ...


def check_sufficient_items(items: list[Edge] | list[ConnectionData]):
    if len(items) == 1 or len(items) == 0:
        raise EdgeProcessingError(
            f"Dataset either doesn't have windows or an entrance door. Stopping. \nItems:\n {pretty_repr(items)}"
        )


def filter_duplicate_edges(edges: list[Edge]):
    res = list(set(edges))
    check_sufficient_items(res)
    return res


def arrange_exteriors(cd: list[ConnectionData], path_to_angle_or_angle: Path | float):
    wds = [i for i in cd if i.conn_type == "Window" or i.conn_type == "Entrance Door"]
    check_sufficient_items(wds)

    if isinstance(path_to_angle_or_angle, Path):
        data = read_json(path_to_angle_or_angle)
        angle: float = data["angle"]
    else:
        angle = path_to_angle_or_angle

    multipolygon = MultiPolygon([i.poly for i in wds])
    rotated = affinity.rotate(multipolygon, angle, use_radians=True)
    new_cd = [i._replace(poly=geom) for i, geom in zip(wds, shapely.get_parts(rotated))]
    assert isinstance(angle, float)
    return (
        new_cd,
        angle,
    )  # TODO: this is becomeing a frequent pair, should promote as an interface


def is_exterior(boundary: Geometry, surface_line: LineString):
    assert shapely.contains(boundary, surface_line)


def are_edges_ok(edges: list[Edge]):
    if not edges:
        raise EdgeProcessingError("No valid edges!")


def make_edge_connections(path_to_geom: Path, cd: list[ConnectionData]):
    # NOTE: may be a bit lossy, next thing would be to build trees based on nearest two domains and check for parralel relationship. Now, will drop edge if its not on the layout boundary
    # TODO: if there are no edges, drop ..

    layout = read_layout_from_path(path_to_geom)
    polygons = [i.polygon for i in layout.domains]
    boundary = unary_union(polygons).boundary

    # place in tree so that cd can find nearest
    tree = STRtree(polygons)
    surface_trees = [
        STRtree([s.coords.shapely_line for s in i.surfaces]) for i in layout.domains
    ]

    def handle_conn(cd: ConnectionData):
        ix = tree.nearest(cd.poly)
        domain = layout.domains[ix]

        surface_tree = surface_trees[ix]
        surf_ix = surface_tree.nearest(cd.poly)
        surface = domain.surfaces[surf_ix]
        try:
            is_exterior(boundary, surface.coords.shapely_line)
        except AssertionError as e:
            logger.critical(
                f"Identified surface for {cd.id}, {surface} is not on the boundary of the layout: {e}, skipping.. "
            )
            return
        return Edge(a=domain.name, b=surface.direction.name.upper(), conn=cd.conn_type)

    res = [handle_conn(i) for i in cd]
    edges = [i for i in res if i]
    are_edges_ok(edges)
    return edges
