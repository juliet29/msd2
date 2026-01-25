from pathlib import Path
from cyclopts import App

from rich.pretty import pretty_repr
from utils4plans.logconfig import logset

from msd2.analysis.qois import calc_metrics
from msd2.geom.connectivity import extract_connectivity_graph
from msd2.geom.create import df_unit_to_room_and_connection_data
from msd2.paths import static_paths
from msd2.readin.access import access_random_sample_datasets

from loguru import logger

from msd2.readin.interfaces import MSDSchema

import tempfile


studies_app = App()


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
def create_metrics(case: str):
    path = static_paths.models / "snakemake" / "0_50" / case
    idf_path = path / "run.idf"
    sql_path = path
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir) / "out.csv"
        calc_metrics(idf_path, sql_path, p)


def main():
    logset()
    studies_app()


if __name__ == "__main__":
    main()
