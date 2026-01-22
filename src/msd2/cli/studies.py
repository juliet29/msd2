from cyclopts import App

from rich.pretty import pretty_repr
from utils4plans.logconfig import logset

from msd2.edges.g2 import extact_graph
from msd2.edges.graph import extract_access_graph
from msd2.geom.create import df_unit_to_room_and_connection_data, msd_geom_to_shapely
from msd2.readin.access import access_sample_datasets

from loguru import logger

from msd2.readin.interfaces import MSDSchema


studies_app = App()


def graph_impl(df):
    for name, data in df.group_by("floor_id"):
        floor_id = name[0]
        with logger.contextualize(id=floor_id):
            geoms = data["geom"].map_elements(msd_geom_to_shapely).to_list()
            # logger.debug(geoms)
            geoms_types = data["roomtype"].to_list()
            # logger.debug(geoms_types)
            G = extract_access_graph(geoms, geoms_types, floor_id)

            logger.debug(G)
            # logger.debug(G.nodes(data=True))
            logger.debug(pretty_repr(list(G.edges(data=True))))


@studies_app.command()
def try_edges():
    df = access_sample_datasets(1).collect()
    for name, data in df.group_by("unit_id"):
        unit_id = name[0]
        with logger.contextualize(unit_id=unit_id):
            rooms, connections = df_unit_to_room_and_connection_data(
                MSDSchema.validate(data)
            )

            edges = extact_graph(rooms, connections)
            logger.debug(pretty_repr(edges))


def main():
    logset()
    studies_app()


if __name__ == "__main__":
    main()
