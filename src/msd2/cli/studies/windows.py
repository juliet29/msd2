import matplotlib
from cyclopts import App
from loguru import logger

from msd2.geom.create import make_connection_data
from msd2.paths import ProjectPaths
from msd2.readin.access import access_datasets_by_unit_ids

matplotlib.use("module://matplotlib-backend-kitty")
import matplotlib.pyplot as plt

windows = App("wd")


PATH = ProjectPaths.data.test_msd_100
CASE = 4969


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
    fig = plot_connection_data(wds)
    plt.show()
