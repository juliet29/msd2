from pathlib import Path
from cyclopts import App
from rich.pretty import pretty_repr

from msd2.analysis.data import collect_data
from msd2.analysis.design_metrics import handle_design_metrics
from msd2.analysis.metrics import make_summary_dataset
from msd2.cli.setup import setup_app
from msd2.eplus.main import layout_to_idf, idf_to_results
from msd2.eplus.metrics import calc_plan_metrics_from_path
from msd2.geom.io import write_unit
from utils4plans.logconfig import logset

from loguru import logger

from msd2.readin.access import get_ids_by_indices

app = App()
app.command(setup_app)


# @app.command()
# def generate_input_files(num_samples: int, path: Path):
#     sample_unit_ids_to_files_as_layouts(num_samples, path)


@app.command()  # TODO: may be a snakemake only command for generating the samples..
def get_ids(start_ix: int, num_samples: int):
    res = get_ids_by_indices(start_ix, num_samples)
    logger.info(res)
    return res


@app.command()
def generate(unit_id: float, edge_path: Path, layout_path: Path):
    write_unit(unit_id, edge_path, layout_path)
    pass


# generating geometry handled by polymap..


@app.command()
def create_idf(edge_path: Path, layout_path: Path, outpath: Path):
    case = layout_to_idf(edge_path, layout_path, outpath)
    logger.debug(pretty_repr(case.objects.subsurfaces))


@app.command()
def run_idf(idf_path: Path, results_path: Path):
    idf_to_results(idf_path, results_path)


@app.command()
def create_data(idf_path: Path, sql_path: Path, outpath: Path):
    dataset = collect_data(idf_path, sql_path.parent.parent)
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


def main():
    logset(to_stderr=True)
    app()


if __name__ == "__main__":
    main()
