from typing import Literal, NamedTuple
from replan2eplus.geometry.coords import Coord
from replan2eplus.ezcase.objects import Subsurface
from replan2eplus.geometry.directions import WallNormal
from replan2eplus.ops.afn.ezobject import Airboundary
import xarray as xr
from replan2eplus.ezcase.ez import EZ
import networkx as nx
from replan2eplus.geometry.domain import Domain
from replan2eplus.geometry.ortho_domain import OrthoDomain
from replan2eplus.ops.zones.ezobject import Zone


def calculate_domain_aspect_ratio(
    domain: OrthoDomain | Domain,
):  # TODO: implement on the class, especially OrthoDomain, and clean up duplication!
    if isinstance(domain, Domain):
        return domain.horz_range.size / domain.vert_range.size
    return (
        domain.bounding_domain.horz_range.size / domain.bounding_domain.vert_range.size
    )


class AFNNodeData(NamedTuple):
    type_: Literal["zone", "external_node"]
    location: Coord
    # just for internal nodes
    area: float | None = None
    aspect_ratio: float | None = None
    # just for external nodes
    external_wind_pressure: xr.DataArray | None = None  # as  function of time..
    facade: WallNormal | None = None


class AFNNode(NamedTuple):
    name: str
    data: AFNNodeData

    @property
    def entry(self):
        return (self.name, {"data": self.data})


class AFNEdgeData(NamedTuple):
    net_flow_rate: xr.DataArray  # as  function of time..


class AFNEdge(NamedTuple):
    u: str
    v: str
    data: AFNEdgeData

    @property
    def entry(self):
        return (self.u, self.v, {"data": self.data})


class AFNGraph(nx.Graph):
    def add_afn_nodes(self, nodes: list[AFNNode]):
        self.add_nodes_from([i.entry for i in nodes])

    def add_afn_edges(self, edges: list[AFNEdge]):
        self.add_edges_from([i.entry for i in edges])

    # TODO: control how nodes are taken
    def get_nodes(self, data: bool = False):
        if data:
            # TODO: prevent additions of the wrong type..
            return [AFNNode(i, data=data["data"]) for i, data in self.nodes(data=True)]
        else:
            return [i for i in self.nodes]

    # def add_node(  # pyright: ignore[reportIncompatibleMethodOverride]
    #     self, node_for_adding: str, data: AFNNode, **attr: Any
    # ) -> None: ...  # attr: Set or change node attributes using key=value
    # def nodes(  # pyright: ignore[reportIncompatibleVariableOverride]
    #     self,
    # ) -> nx.classes.reportviews.NodeView[AFNNode]: ...
    #
    # def add_edge(  # pyright: ignore[reportIncompatibleMethodOverride]
    #     self, u_of_edge: str, v_of_edge: str, data: AFNEdge, **attr: Any
    # ) -> Hashable | None: ...
    #


def make_graph(case: EZ):
    afn_surfaces = case.objects.airflow_network.afn_surfaces
    afn_zones = case.objects.zones
    # TODO: -> get external nodes directly from the IDF
    # TODO: also need to see how the geometry is being resolved -> do we have floating point issues?

    def make_afn_node_from_zone(zone: Zone):
        domain = zone.domain
        return AFNNode(
            zone.room_name,
            data=AFNNodeData(
                "zone",
                domain.centroid,
                domain.area,
                calculate_domain_aspect_ratio(domain),
            ),
        )

    def make_edge(afn_surface: Subsurface | Airboundary):
        e = afn_surface.edge
        return AFNEdge(e.space_a, e.space_b, data=AFNEdgeData(xr.DataArray()))

    G = AFNGraph()
    zone_nodes = [make_afn_node_from_zone(i) for i in afn_zones]
    G.add_afn_nodes(zone_nodes)

    edge_nodes = [make_edge(i) for i in afn_surfaces]
    G.add_afn_edges(edge_nodes)

    #
    #
    return G
