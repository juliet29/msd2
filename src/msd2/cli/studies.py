from cyclopts import App

from rich.pretty import pretty_repr
from utils4plans.logconfig import logset

from msd2.edges.graph import extract_connectivity_graph
from msd2.geom.create import df_unit_to_room_and_connection_data
from msd2.readin.access import access_random_sample_datasets

from loguru import logger

from msd2.readin.interfaces import MSDSchema


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


def main():
    logset()
    studies_app()


if __name__ == "__main__":
    main()
