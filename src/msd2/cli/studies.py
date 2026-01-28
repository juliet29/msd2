## NOTE: These should be temoporary -> regularly move out to tests!
from cyclopts import App

from replan2eplus.ezcase.ez import EZ
from rich.pretty import pretty_repr
from utils4plans.logconfig import logset

from msd2.analysis.data import QOIRegistry, collect_data
from msd2.analysis.design_metrics import handle_design_metrics
from msd2.analysis.metrics import (
    handle_data,
    make_summary_dataset,
    plot_tod_qoi_dataset,
    set_altair_render,
)
from msd2.analysis.plots import make_corr_plot
from msd2.eplus.metrics import calc_plan_metrics_from_path
from msd2.geom.connectivity import extract_connectivity_graph
from msd2.geom.create import df_unit_to_room_and_connection_data
from msd2.graph_analysis.main import make_graph
from msd2.paths import static_paths
from msd2.readin.access import access_random_sample_datasets

from loguru import logger

from msd2.readin.interfaces import MSDSchema
from msd2.readin.scripts import summarize_dataset


studies_app = App()


@studies_app.command()
def show_summarize_dataset():
    summarize_dataset()


@studies_app.command()
def try_edges():
    df = access_random_sample_datasets(1).collect()
    for name, data in df.group_by("unit_id"):
        unit_id = name[0]
        with logger.contextualize(unit_id=unit_id):
            rooms, connections = df_unit_to_room_and_connection_data(
                MSDSchema.validate(data)
            )

            edges = extract_connectivity_graph(rooms, connections)
            logger.debug(pretty_repr(edges))


@studies_app.command()
def create_data(case: str):
    path = static_paths.models / "snakemake" / "0_50" / case
    idf_path = path / "run.idf"
    sql_path = path
    res = collect_data(idf_path, sql_path)
    logger.debug(res)
    return res


@studies_app.command()
def create_metrics(case: str):
    path = static_paths.models / "snakemake" / "0_50" / case
    idf_path = path / "run.idf"
    res = calc_plan_metrics_from_path(idf_path)
    logger.debug(res)
    return res


def get_filtered_paths(filename: str):
    path = static_paths.models / "snakemake" / "0_50"
    paths = [i for i in path.iterdir() if i.is_dir()]
    data_paths = [p / filename for p in paths]
    filtered_paths = [i for i in data_paths if i.exists()]
    return filtered_paths


@studies_app.command()
def try_bar_plot():
    casedata = handle_data(get_filtered_paths("analysis/data.nc"))

    res, chart = plot_tod_qoi_dataset(casedata, QOIRegistry.net_flow, "Day")
    # logger.debug(res)

    set_altair_render("browser")
    chart.show()

    return res


@studies_app.command()
def try_read_metrics():
    df = handle_design_metrics(get_filtered_paths("analysis/metrics.csv"))
    return df


@studies_app.command()
def try_summary_data():
    day, night = make_summary_dataset(get_filtered_paths("analysis/data.nc"))
    logger.debug(day)


@studies_app.command()
def try_corr_plot():
    root = static_paths.figures / "snakemake/0_50"
    csvname = "out.csv"
    data = root / "data/day" / csvname
    metric = root / "metrics" / csvname
    charts = make_corr_plot(data, metric)

    set_altair_render("browser")
    for chart in charts:
        chart.show()


@studies_app.command()
def try_make_graph(casenum: str):  # 6289
    path = static_paths.models / "snakemake" / "0_50" / casenum
    idf_path = path / "run.idf"
    case = EZ(idf_path=idf_path)
    # logger.debug(
    #     pretty_repr(
    #         [(i.room_name, i.zone_name) for i in case.objects.airflow_network.zones]
    #     )
    # )
    # logger.debug(
    #     pretty_repr(
    #         [(i.name, i.edge) for i in case.objects.airflow_network.afn_surfaces]
    #     )
    # )
    g = make_graph(case)
    logger.debug(g)
    logger.debug(pretty_repr([i for i in g.nodes(data=True)]))
    logger.debug(pretty_repr([i for i in g.edges(data=True)]))


def main():
    logset()
    studies_app()


if __name__ == "__main__":
    main()
