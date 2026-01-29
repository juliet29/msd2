from loguru import logger
from msd2.graph_analysis.interfaces import AFNGraph, make_layout
import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime
import iplotx as ipx


# def plot_eternal_nodes(nodes: list[AFNNode], ax: Axes):
#     layout = make_layout(nodes)
#     pass
#
def make_datetime(
    year: int = 2017, month: int = 6, day: int = 7, hour: int = 12, minute: int = 0
):
    return datetime(year, month, day, hour, minute)


def select_time(arr: xr.DataArray, dt: datetime = make_datetime()):
    return arr.sel(datetimes=dt).data


def viz_graph(G: AFNGraph):
    fig, ax = plt.subplots()
    layout = make_layout(G.get_nodes(data=True))

    # first focus on zones  -> get the data and then make subgraph
    nodedata = [
        select_time(i.data.ach) if i.data.ach.any() else 0 for i in G.zone_nodes
    ]
    logger.debug(nodedata)

    nodesizes = nodedata
    #
    artist = ipx.network(
        G.subgraph([i.name for i in G.zone_nodes]),
        ax=ax,
        layout=layout,
        vertex_labels=G.zone_nodes,
        style={"vertex": {"marker": "r", "size": nodesizes}},
    )
    plt.show()
