import matplotlib
from cyclopts import App
from loguru import logger

from msd2.ep2.full_layout import FullLayout
from msd2.ep2.viz import VisualizeFullLayout
from msd2.geom.create import make_connection_data
from msd2.geom.exteriors import arrange_exteriors, make_edge_connections
from msd2.paths import ProjectPaths
from msd2.readin.access import PartitionedDataFrame, access_datasets_by_unit_ids
from msd2.run.dataset import Dataset

matplotlib.use("module://matplotlib-backend-kitty")
import matplotlib.pyplot as plt

windows = App("wd")


PATH = ProjectPaths.data.test_msd_100
CASE = 4969
CASE = 5155
# CASE = 5153
# CASE = 5153


def plot_connection_data(data, title: str = "windows"):
    from shapely.plotting import plot_polygon

    fig, ax = plt.subplots()
    for cd in data:
        plot_polygon(cd.poly, ax=ax, add_points=False, alpha=0.4)
        ax.annotate(
            str(cd.id),
            (cd.poly.centroid.x, cd.poly.centroid.y),
            ha="center",
            fontsize=8,
        )
    ax.set_aspect("equal")
    ax.set_title(title)
    return fig


@windows.command()
def fc():
    df = access_datasets_by_unit_ids([CASE]).collect()
    logger.debug(df)
    data = make_connection_data(df)
    wds = [i for i in data if i.entity_subtype == "WINDOW"]
    _ = plot_connection_data(wds)
    plt.show()


@windows.command()
def fcb(CASE: int = CASE):
    df = access_datasets_by_unit_ids([CASE]).collect()
    data = make_connection_data(df)

    ds = Dataset(PATH)

    rotated_conn_data = arrange_exteriors(data, ds.paths.pr_case_angle(CASE))
    edges = make_edge_connections(ds.paths.pr_case_reconciled(CASE), rotated_conn_data)

    _ = plot_connection_data(rotated_conn_data)
    plt.show()

    return edges


@windows.command()
def fd(CASE: int = CASE):
    ds = Dataset(PATH)
    df = PartitionedDataFrame().get_unit_df(CASE)
    assert df is not None

    fl = FullLayout(
        ds.paths.pr_case_reconciled(CASE), ds.paths.pr_case_angle(CASE), CASE, df
    )
    viz = VisualizeFullLayout(fl)
    viz.make_plot()
    plt.show()
    # fl.orient_layout()
    # fl.make_window_edges()
    # return fl.window_edges
    # return rotate_layout_by_entrance_door(fl.layout, fl.entrance_door)
