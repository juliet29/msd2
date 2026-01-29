from typing import Literal, NamedTuple
import networkx as nx
from replan2eplus.geometry.coords import Coord
from replan2eplus.geometry.directions import WallNormal
import xarray as xr


class AFNNodeData(NamedTuple):
    type_: Literal["zone", "external_node"]
    location: Coord
    # just for internal nodes
    area: float | None = None
    aspect_ratio: float | None = None
    vent_volume: xr.DataArray | None = None
    mix_volume: xr.DataArray | None = None
    ach: xr.DataArray | None = None
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
    net_flow_rate: xr.DataArray | None = None  # as  function of time..


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
