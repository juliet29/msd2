from cyclopts import App
from rich.pretty import pretty_repr

from msd2.config import NUM_SAMPLES
from msd2.eplus.main import layout_to_idf
from msd2.geom.utils import sample_unit_ids_to_files
from utils4plans.logconfig import logset

from msd2.paths import DynamicPaths
from loguru import logger

app = App()


## READING IN.. TODO: add commands from readin/scripts


@app.command()
def generate_input_files(num_samples: int = NUM_SAMPLES):
    sample_unit_ids_to_files(num_samples)


# STUDIES


@app.command()
def create_idf(case_name: str, run: bool = False):
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
