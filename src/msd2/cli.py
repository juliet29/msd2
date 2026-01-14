from cyclopts import App

from msd2.config import NUM_SAMPLES
from msd2.eplus.main import layout_to_idf
from msd2.geom.utils import sample_unit_ids_to_files
from polymap.logconf import logset

from msd2.paths import DynamicPaths

app = App()


## READING IN.. TODO: add commands from readin/scripts


@app.command()
def generate_input_files(num_samples: int = NUM_SAMPLES):
    sample_unit_ids_to_files(num_samples)


@app.command()
def create_idf(case: str, run: bool = False):
    folder_path = DynamicPaths.workflow_outputs / case
    inpath = folder_path / "ymove/out.json"
    outpath = folder_path / "model"
    layout_to_idf(inpath, outpath, run)


def main():
    app()


if __name__ == "__main__":
    logset()  # TODO: move to utils! and add ability to set log level as a parameter
    main()
