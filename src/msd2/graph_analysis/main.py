import re
from plan2eplus.ops.afn.idfobject import IDFAFNExternalNode
from utils4plans.lists import sort_and_group_objects
from pathlib import Path
from typing import NamedTuple
from plan2eplus.ezcase.objects import Subsurface
from plan2eplus.ops.afn.ezobject import Airboundary
from plan2eplus.results.sql import get_qoi
import xarray as xr
from plan2eplus.ezcase.ez import EZ
from plan2eplus.geometry.domain import Domain
from plan2eplus.geometry.ortho_domain import OrthoDomain
from plan2eplus.ops.zones.ezobject import Zone
from plan2eplus.geometry.contact_points import (
    CardinalPoints,
    calculate_cardinal_points,
)
from plan2eplus.visuals.domains import calculate_cardinal_domain
from msd2.analysis.data import calc_net_flow
from msd2.graph_analysis.interfaces import (
    AFNEdge,
    AFNEdgeData,
    AFNGraph,
    ZoneNodeData,
    ExternalNodeData,
    ZoneNode,
    ExternalNode,
)


def calculate_domain_aspect_ratio(
    domain: OrthoDomain | Domain,
):  # TODO: implement on the class, especially OrthoDomain, and clean up duplication!
    if isinstance(domain, Domain):
        return domain.horz_range.size / domain.vert_range.size
    return (
        domain.bounding_domain.horz_range.size / domain.bounding_domain.vert_range.size
    )


class IDFExternalNode(NamedTuple):
    name: str
    direction: str


def handle_external_nodes(nodes: list[str]):
    def find_drn(node: str):
        node = node.upper()
        pattern = re.compile("(NORTH)|(SOUTH)|(EAST)|(WEST)")
        res = pattern.search(node)
        if res:
            drn = res.group()
            return IDFExternalNode(node, drn)
        else:
            raise ValueError(f"{node} does not contain a direction!")

    ext_nodes = [find_drn(i) for i in nodes]
    grouped_nodes = sort_and_group_objects(ext_nodes, lambda x: x.direction)
    # just want the first from each node
    return [i[0] for i in grouped_nodes]


def get_extenal_nodes(case: EZ):
    # TODO: this should be one of the thing inside the ezcase object..
    nodes = IDFAFNExternalNode.read_and_filter(case.idf)
    node_names = [i.Name for i in nodes]
    res = handle_external_nodes(node_names)
    return res


def get_space_arr(arr: xr.DataArray, name: str):
    try:
        return arr.sel(space_names=name.upper())
    except KeyError:
        raise Exception(f"Could not find data for {name} in {arr}")


def make_graph(idf_path: Path, sql_path: Path, cardinal_expansion_factor: float = 1.3):
    def make_afn_nodes_from_external_nodes(
        extnode: IDFExternalNode, cardinal_locations: CardinalPoints
    ):
        return ExternalNode(
            extnode.direction,
            data=ExternalNodeData(
                type_="external_node",
                location=cardinal_locations[
                    extnode.direction
                ],  # pyright: ignore[reportArgumentType]
                external_wind_pressure=get_space_arr(node_wind_pressure, extnode.name),
            ),
        )

    def make_afn_node_from_zone(zone: Zone):
        domain = zone.domain
        zone_name = zone.zone_name
        return ZoneNode(
            zone.room_name,
            data=ZoneNodeData(
                type_="zone",
                location=domain.centroid,
                area=domain.area,
                aspect_ratio=calculate_domain_aspect_ratio(domain),
                vent_volume=get_space_arr(ventilation_volume, zone_name),
                mix_volume=get_space_arr(mixing_volume, zone_name),
                ach=get_space_arr(ach, zone_name),
            ),
        )

    def make_edge_from_surface(afn_surface: Subsurface | Airboundary):
        e = afn_surface.edge
        return AFNEdge(
            e.space_a,
            e.space_b,
            data=AFNEdgeData(net_flow_rate=get_space_arr(net_flow, afn_surface.name)),
        )

    # get objects
    case = EZ(idf_path)
    afn_surfaces = case.objects.airflow_network.afn_surfaces
    afn_zones = case.objects.zones
    external_nodes = get_extenal_nodes(case)

    # get data
    net_flow = calc_net_flow(sql_path)
    node_wind_pressure = get_qoi("AFN Node Wind Pressure", sql_path).data_arr
    mixing_volume = get_qoi("AFN Zone Mixing Volume", sql_path).data_arr
    ventilation_volume = get_qoi("AFN Zone Ventilation Volume", sql_path).data_arr
    ach = get_qoi("AFN Zone Ventilation Air Change Rate", sql_path).data_arr

    # create the graph
    G = AFNGraph()
    zone_nodes = [make_afn_node_from_zone(i) for i in afn_zones]
    G.add_afn_nodes(zone_nodes)

    cardinal_locations = calculate_cardinal_points(
        calculate_cardinal_domain(
            [i.domain for i in afn_zones],
            cardinal_expansion_factor=cardinal_expansion_factor,
        )
    )
    afn_ext_nodes = [
        make_afn_nodes_from_external_nodes(i, cardinal_locations)
        for i in external_nodes
    ]
    G.add_afn_nodes(afn_ext_nodes)

    edge_nodes = [make_edge_from_surface(i) for i in afn_surfaces]
    G.add_afn_edges(edge_nodes)

    return G
