from cyclopts import App

from msd2.config import NUM_SAMPLES
from msd2.geom.utils import sample_unit_ids_to_files
from polymap.logconf import logset

app = App()


## READING IN.. TODO: add commands from readin/scripts


@app.command()
def generate_input_files(num_samples: int = NUM_SAMPLES):
    sample_unit_ids_to_files(num_samples)


def main():
    # TODO: set logging here
    # logconf.logset()
    app()


if __name__ == "__main__":
    logset()  # TODO: move to utils! and add ability to set log level as a parameter
    main()
