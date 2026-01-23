from pathlib import Path
from cyclopts import App
from rich.pretty import pretty_repr

from msd2.cli.setup import setup_app
from msd2.eplus.main import layout_to_idf
from msd2.geom.io import write_unit
from utils4plans.logconfig import logset

from msd2.paths import DynamicPaths
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
def create_idf(case_name: str, run: bool = False):
    # this is part of snakemake ..
    folder_path = DynamicPaths.workflow_outputs / case_name
    inpath = folder_path / "ymove/out.json"
    outpath = folder_path / "model"
    case = layout_to_idf(inpath, outpath, run)

    # assess_surface_relations(case)

    logger.debug(pretty_repr(case.objects.subsurfaces))


def main():
    logset()
    app()


if __name__ == "__main__":
    main()
