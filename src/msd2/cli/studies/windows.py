from pathlib import Path

import matplotlib
from cyclopts import App
from loguru import logger
from plan2eplus.ops.run_settings.user_interfaces import AnalysisPeriod
from plan2eplus.visuals.simple_plots import make_base_plot

from msd2.config import MSDConfigSchema
from msd2.ep2.full_layout import FullLayout
from msd2.ep2.model import layout_to_idf
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

    rotated_conn_data = arrange_exteriors(data, ds.paths.unit(CASE).process.angle)
    edges = make_edge_connections(
        ds.paths.unit(CASE).process.reconciled, rotated_conn_data
    )

    _ = plot_connection_data(rotated_conn_data)
    plt.show()

    return edges


@windows.command()
def fd(CASE: int = CASE):
    ds = Dataset(PATH)
    df = PartitionedDataFrame().get_unit_df(CASE)
    assert df is not None

    fl = FullLayout(
        ds.paths.unit(CASE).process.reconciled,
        ds.paths.unit(CASE).process.angle,
        CASE,
        df,
    )
    viz = VisualizeFullLayout(fl)
    viz.make_plot()
    plt.show()


@windows.command()
def fe(CASE: int = CASE):
    ds = Dataset(PATH)
    df = ds.partitioned_df.get_unit_df(CASE)
    assert df is not None

    fl = FullLayout(
        ds.paths.unit(CASE).process.reconciled,
        ds.paths.unit(CASE).process.angle,
        CASE,
        df,
    )
    cfg = MSDConfigSchema(3, Path(""), AnalysisPeriod("", 1, 2, 2, 3), Path(""))
    case = layout_to_idf(fl, cfg)
    bp = make_base_plot(case, cardinal_expansion_factor=1.1)
    bp.show()
    # return case
