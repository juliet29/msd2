from pathlib import Path
from cyclopts import App
from rich.pretty import pretty_repr

from msd2.eplus.main import layout_to_idf
from msd2.geom.io import sample_unit_ids_to_files_as_layouts
from utils4plans.logconfig import logset

from msd2.paths import DynamicPaths
from loguru import logger

app = App()


@app.command()
def generate_input_files(path: Path, num_samples: int):
    sample_unit_ids_to_files_as_layouts(num_samples, path)


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
