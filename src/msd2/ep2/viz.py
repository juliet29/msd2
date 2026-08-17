import matplotlib.pyplot as plt
from icecream import ic
from matplotlib.axes import Axes
from polyfix.geometry.layout import Layout
from polyfix.visuals.visuals import plot_layout
from shapely.plotting import plot_line, plot_polygon

from msd2.ep2.full_layout import FullLayout
from msd2.geom.interfaces import ConnectionData, ConnectionNamesEnum, Edge
from msd2.geom.rotate import get_surface_by_edge


def plot_connection_data(data: list[ConnectionData], ax: Axes):
    cne = ConnectionNamesEnum
    color_map = {
        cne.DOOR.value: "red",
        cne.ENTRANCE_DOOR.value: "orange",
        cne.WINDOW.value: "green",
    }
    for cd in data:
        color = color_map[cd.conn_type]
        plot_polygon(cd.poly, ax=ax, add_points=False, alpha=0.4, color=color)
        ax.annotate(
            str(cd.id),
            (cd.poly.centroid.x, cd.poly.centroid.y),
            ha="center",
            fontsize=8,
        )
    return ax


def plot_edge_data(layout: Layout, edges: list[Edge], ax: Axes, color: str):
    def plot_one(e: Edge):
        ic("")
        s = get_surface_by_edge(layout, e)
        line = s.coords.shapely_line
        plot_line(line, ax=ax, color=color)

    for e in edges:
        plot_one(e)
    # (plot_one(e) for e in edges)


class VisualizeFullLayout:
    # init_layout: Layout
    # orient_layout: Layout
    # connections: list[ConnectionData]
    #
    # interior_door_edge: list[Edge]
    # entrance_door_edge: Edge
    # window_edge: list[Edge]
    #

    def __init__(self, fl: FullLayout) -> None:
        self.fl = fl

    def plot_init_layout(self, ax: Axes):
        ax = plot_layout(self.fl.layout, ax=ax)
        ax = plot_connection_data(self.fl.connections, ax=ax)

        # interior doors immediately resolved
        # complicated to plot though
        # self.fl.orient_entrance_door()
        #
        # assert self.fl.entrance_door_edge
        # plot_edge_data(self.fl.layout, [self.fl.entrance_door_edge], ax, "red")

    def plot_orient_exteriors(self, ax: Axes):
        self.fl.orient_exteriors()
        ax = plot_layout(self.fl.layout, ax=ax)
        ax = plot_connection_data(self.fl.rotated_conns, ax=ax)
        plot_edge_data(self.fl.layout, [self.fl.door_0], ax=ax, color="orange")
        plot_edge_data(self.fl.layout, self.fl.window_0, ax=ax, color="green")

    def plot_oriented_layout(self, ax: Axes):
        self.fl.calculate_final_orient_angle()
        self.fl.orient_layout()

        ax = plot_layout(self.fl.oriented_layout, ax=ax)

        self.fl.orient_exteriors_final()
        plot_edge_data(self.fl.oriented_layout, [self.fl.door_1], ax=ax, color="orange")
        plot_edge_data(self.fl.oriented_layout, self.fl.window_1, ax=ax, color="green")
        # plot_edge_data(self.fl.layout, [self.fl.entrance_door_edge], ax, "orange")

        # self.fl.make_window_edges()
        # plot_edge_data(self.fl.layout, self.fl.window_edges, ax, "green")

    def make_plot(self):
        base_sz = 8
        n_cols = 3
        fig, axes = plt.subplots(nrows=1, ncols=n_cols, figsize=(base_sz * 4, 4))
        self.plot_init_layout(axes[0])
        self.plot_orient_exteriors(axes[1])
        self.plot_oriented_layout(axes[2])
        # self.fl.orient_exteriors_final()
        for ax in axes:
            ax.set_aspect("equal")
        # self.plot_oriented_layout(axes[1])
        return fig
