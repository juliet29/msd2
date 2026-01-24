from pathlib import Path

from loguru import logger
from replan2eplus.ops.subsurfaces.user_interfaces import EdgeGroup, SubsurfaceInputs
from msd2.eplus.interfaces import (
    make_details,
    read_edges_to_ezcase_edge_groups,
    read_layout_to_ezcase_rooms,
)
from replan2eplus.ezcase.ez import EZ
from replan2eplus.ops.zones.user_interface import Room
from msd2.config import WEATHER_FILE


def generate_idf(
    rooms: list[Room], edge_groups: list[EdgeGroup], out_path: Path, run: bool = False
):
    case = EZ(output_path=out_path, epw_path=WEATHER_FILE)
    case.add_zones(rooms)

    subsurface_inputs = SubsurfaceInputs(
        edge_groups, make_details()  # pyright: ignore[reportArgumentType]
    )
    case.add_subsurfaces(subsurface_inputs)

    case.add_constructions()
    case.add_airflow_network()
    case.save_and_run(
        output_path=out_path, run=run, save=True
    )  # TODO: shouldlnt have to specify twice in different places.
    return case


def layout_to_idf(edge_path: Path, layout_path: Path, outpath: Path):
    rooms = read_layout_to_ezcase_rooms(layout_path)
    # only doing one type for now
    edge_group = read_edges_to_ezcase_edge_groups(edge_path).interior_door_edges

    logger.debug(f"Rooms to add: {[i.name for i in rooms]}")
    logger.debug(f" Edges to add: {[i.as_tuple for i in edge_group.edges]}")

    # for now, only consider door edges, need different approach for windows..
    # # also need to do airboundaries

    case = generate_idf(rooms, [edge_group], outpath.parent, run=False)
    return case
