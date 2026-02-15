from typing import Hashable, Literal, NamedTuple, Sequence, TypeVar
from dataclasses import dataclass

import networkx as nx
import xarray as xr
from plan2eplus.geometry.coords import Coord

NodeType = Literal["zone", "external_node"]


class ZoneNodeData(NamedTuple):
    type_: NodeType
    location: Coord
    area: float
    aspect_ratio: float
    vent_volume: xr.DataArray
    mix_volume: xr.DataArray
    ach: xr.DataArray


class ExternalNodeData(NamedTuple):
    type_: NodeType
    location: Coord
    external_wind_pressure: xr.DataArray


@dataclass(frozen=True)
class AFNNode:
    name: str
    data: ExternalNodeData | ZoneNodeData

    @property
    def entry(self):
        return (self.name, {"data": self.data})


@dataclass(frozen=True)
class ZoneNode(AFNNode):
    name: str
    data: ZoneNodeData


@dataclass(frozen=True)
class ExternalNode(AFNNode):
    name: str
    data: ExternalNodeData


class AFNEdgeData(NamedTuple):
    net_flow_rate: xr.DataArray


class AFNEdge(NamedTuple):
    u: str
    v: str
    data: AFNEdgeData

    @property
    def entry(self):
        return (self.u, self.v, {"data": self.data})


class BasicEdge(NamedTuple):
    u: str
    v: str


AFNNodeType = TypeVar("AFNNodeType", bound=AFNNode)


class AFNGraph(nx.Graph):
    def add_afn_nodes(self, nodes: list[AFNNodeType]):
        self.add_nodes_from([i.entry for i in nodes])

    def add_afn_edges(self, edges: list[AFNEdge]):
        self.add_edges_from([i.entry for i in edges])

    @property
    def edges_with_data(self):
        edges = [AFNEdge(u, v, data["data"]) for u, v, data in self.edges(data=True)]
        return edges

    @property
    def zone_nodes(self):
        nodes = self.nodes(data=True)
        res = [
            ZoneNode(i, data["data"])
            for i, data in nodes
            if isinstance(data["data"], ZoneNodeData)
        ]
        return res

    @property
    def external_nodes(self) -> list[ExternalNode]:
        nodes = self.nodes(data=True)
        res = [
            ExternalNode(i, data["data"])
            for i, data in nodes
            if isinstance(data["data"], ExternalNodeData)
        ]
        return res

    @property
    def zone_names(self):
        return [i.name for i in self.zone_nodes]

    @property
    def external_node_names(self):
        return [i.name for i in self.external_nodes]

    @property
    def all_names(self):
        return self.nodes(data=False)

    @property
    def all_nodes(self):
        return self.zone_nodes + self.external_nodes

    @property
    def layout(self) -> dict[Hashable, tuple[float, float] | Sequence[float]]:
        return {node.name: list(node.data.location.as_tuple) for node in self.all_nodes}

    @property
    def zone_only_subgraph(self):
        sg = nx.Graph()
        sg.add_nodes_from(self.zone_names)
        return sg

    @property
    def external_node_only_subgraph(self):
        sg = nx.Graph()
        sg.add_nodes_from(self.external_node_names)
        return sg

    def make_time_specific_digraph(self, data: list[float]):
        # NOTE: this is a bit risky, becasue not sure the egdes and the the data have the same alignment... maybe should take in a list of the edges also.., but its a property, so should only be calculated once, then cached...
        def make_edge(edge: BasicEdge, datapt: float):
            if abs(datapt) > 0:
                return (edge.u, edge.v)
            else:
                return (edge.v, edge.u)

        G = nx.DiGraph()
        edges = [
            make_edge(BasicEdge(i.u, i.v), datapt)
            for i, datapt in zip(self.edges_with_data, data)
        ]

        G.add_edges_from([i for i in edges])
        return G
