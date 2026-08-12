from pathlib import Path

import shapely
from loguru import logger
from polars import read_json
from polyfix.main.main_class import read_layout_from_path
from shapely import (
    Geometry,
    LineString,
    MultiPolygon,
    STRtree,
    affinity,
    unary_union,
)

from msd2.geom.interfaces import ConnectionData, Edge


class EdgeProcessingError(Exception): ...


def arrange_exteriors(cd: list[ConnectionData], path_to_angle: Path):
    wds = [i for i in cd if i.roomtype == "Window" or i.roomtype == "Entrance Door"]
    if len(wds) == 0:
        raise EdgeProcessingError(f"Dataset at {path_to_angle} has no windows..")
    data = read_json(path_to_angle)
    angle: float = data["angle"][0]

    multipolygon = MultiPolygon([i.poly for i in wds])
    rotated = affinity.rotate(multipolygon, angle, use_radians=True)
    new_cd = [i._replace(poly=geom) for i, geom in zip(wds, shapely.get_parts(rotated))]
    return new_cd


def is_exterior(boundary: Geometry, surface_line: LineString):
    assert shapely.contains(boundary, surface_line)


def are_edges_ok(edges: list[Edge]):
    if not edges:
        raise EdgeProcessingError("No valid edges!")
    conn_types = [i.conn for i in edges]
    if "Entrance Door" not in conn_types:
        raise EdgeProcessingError("Entrance Door is not in edges!")


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
        return Edge(a=domain.name, b=surface.direction.name.upper(), conn=cd.roomtype)

    res = [handle_conn(i) for i in cd]
    edges = [i for i in res if i]
    are_edges_ok(edges)
    return edges
