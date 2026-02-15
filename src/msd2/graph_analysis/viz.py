from loguru import logger
from msd2.analysis.data import QOIRegistry
from msd2.graph_analysis.interfaces import AFNGraph
import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime

from sklearn.preprocessing import minmax_scale
from astropy.visualization import AsinhStretch, SqrtStretch
import networkx as nx
import iplotx as ipx


# def plot_eternal_nodes(nodes: list[AFNNode], ax: Axes):
#     layout = make_layout(nodes)
#     pass
#
def make_datetime(
    year: int = 2017, month: int = 6, day: int = 7, hour: int = 12, minute: int = 0
):
    return datetime(year, month, day, hour, minute)


def norm_size(data: list[float], scale: int = 50):
    t01 = minmax_scale(data, (0, 1))
    stretch_fx = SqrtStretch()
    norm_data = stretch_fx(t01) * scale
    return norm_data


def norm_edge_fx(data: list[float], scale: int = 10):
    t01 = minmax_scale(data, (0.1, 1))
    logger.debug(t01)
    stretch_fx = AsinhStretch()
    norm_data = stretch_fx(t01) * scale
    return norm_data


def select_time(arr: xr.DataArray, dt: datetime = make_datetime()):
    # TODO: use xarray validation to ensure this actually works..
    return float(arr.sel(datetimes=dt).data)


def viz_graph(G: AFNGraph, scale: int = 40, show: bool = False):
    fig, ax = plt.subplots()

    nodedata = [
        select_time(i.data.mix_volume + i.data.vent_volume) for i in G.zone_nodes
    ]
    # logger.debug(nodedata)
    norm_data = norm_size(nodedata, scale)
    # logger.debug(norm_data)

    edgedata = [select_time(i.data.net_flow_rate) for i in G.edges_with_data]
    display_edgedata = [rf"${i:.2f}$" for i in edgedata]
    edge_graph_at_time = G.make_time_specific_digraph(edgedata)

    # # logger.debug(edgedata)
    norm_edge = norm_edge_fx(edgedata)
    # logger.debug(norm_edge)

    node_only_subgraph = nx.Graph()
    node_only_subgraph.add_nodes_from(G.zone_names)

    bbox_style = {"bbox": {"facecolor": "#01245c"}}

    edge_colors = edgedata
    cmap = plt.cm.Blues  # pyright: ignore[reportAttributeAccessIssue]

    # edges
    edges_artist = ipx.network(
        edge_graph_at_time,
        ax=ax,
        layout=G.layout,
        # edge_labels=display_edgedata,
        style={
            "edge": {
                "linewidth": norm_edge,
                "color": edge_colors,
                "cmap": cmap,
                "label": {"bbox": {"facecolor": "#4f5661"}},
                "shrink": 5,
            },
            "vertex": {
                "marker": "o",
                "facecolor": "white",  # hide nodes at this point..
            },
        },
    )
    # zones and size
    zones_artist = ipx.network(
        node_only_subgraph,
        ax=ax,
        layout=G.layout,
        # vertex_labels=G.zone_names,
        style={
            "vertex": {
                "marker": "o",
                "size": norm_data,
                "facecolor": "#6d83a6",
            }
        },
    )
    # external nodes
    ipx.network(
        G.external_node_only_subgraph,
        ax=ax,
        layout=G.layout,
        vertex_labels=list(G.external_node_only_subgraph.nodes),
        fontsize="xx-small",
        strip_axes=False,
        style={
            "vertex": {
                "marker": "o",
                "size": scale,
                "facecolor": "gray",
                "label": bbox_style,
            }
        },
    )
    cbar = fig.colorbar(
        edges_artist[0].get_edges(),
        ax=ax,
    )
    cbar.set_label(QOIRegistry.net_flow.label)
    # res = zones_artist[0].get_nodes()
    # logger.debug(str(res))
    # ax.legend(res)
    if show:
        plt.show()
    return fig
