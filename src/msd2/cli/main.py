from pathlib import Path

from cyclopts import App
from loguru import logger
from utils4plans.io import read_pickle, write_pickle
from utils4plans.logconfig import logset

from msd2.analysis.data import collect_data
from msd2.analysis.design_metrics import handle_design_metrics
from msd2.analysis.metrics import make_summary_dataset
from msd2.cli.setup import setup_app
from msd2.eplus.main import idf_to_results, layout_to_idf
from msd2.eplus.metrics import calc_plan_metrics_from_path
from msd2.geom.io import write_unit
from msd2.graph_analysis.main import make_graph
from msd2.graph_analysis.viz import viz_graph
from msd2.readin.access import get_ids_by_indices

app = App()
app.command(setup_app)


@app.command()  # TODO: may be a snakemake only command for generating the samples..
def get_ids(path_to_valid_ids: Path, start_ix: int, num_samples: int):
    res = get_ids_by_indices(path_to_valid_ids, start_ix, num_samples)
    logger.info(res)
    return res


@app.command()
def generate(unit_id: float, edge_path: Path, layout_path: Path):
    write_unit(unit_id, edge_path, layout_path)
    pass


#
# TODO: feel that these thing should be part of plan2eplus?


@app.command()
def create_idf(edge_path: Path, layout_path: Path, outpath: Path):
    case = layout_to_idf(edge_path, layout_path, outpath)
    # TODO: make a nice finishing statement w/ number of zones...
    n_zone = len(case.objects.zones)
    n_subsurface = len(case.objects.subsurfaces)
    fin = f"Wrote case with {n_zone} zones and {n_subsurface} subsurfaces to {outpath.parent.name}/{outpath.name}"
    logger.success(fin)


@app.command()
def run_idf(idf_path: Path, results_directory: Path, schedules_directory: Path):
    idf_to_results(idf_path, results_directory, schedules_directory)


#### ------- DATA ANALYSIS PIPELINE -------------


@app.command()
def create_data(idf_path: Path, sql_path: Path, outpath: Path):
    dataset = collect_data(
        idf_path, sql_path.parent.parent
    )  # TODO: fix sql code so not so pedantic
    dataset.to_netcdf(outpath)


@app.command()
def create_metrics(idf_path: Path, outpath: Path):
    df = calc_plan_metrics_from_path(idf_path)
    df.write_csv(outpath)


@app.command()
def create_summary_data(paths: list[Path], daypath: Path, nightpath: Path):
    day, night = make_summary_dataset(paths)
    day.write_csv(daypath)
    night.write_csv(nightpath)


@app.command()
def create_summary_metrics(paths: list[Path], outpath: Path):
    res = handle_design_metrics(paths)
    res.write_csv(outpath)


@app.command()
def create_graph(idf_path: Path, sql_path: Path, outpath: Path):
    # TODO: using a pickle for now, long term, this is not a good solution -> need to use Pydantic..
    g = make_graph(idf_path, sql_path.parent.parent)
    write_pickle(g, outpath.parent, outpath.stem, OVERWRITE=True)


@app.command()
def create_graph_figure(graph_path: Path, outpath: Path):
    g = read_pickle(graph_path.parent, graph_path.stem)
    fig = viz_graph(g)
    fig.savefig(outpath, dpi=300)


def main():
    logset(to_stderr=True)
    app()


if __name__ == "__main__":
    main()
