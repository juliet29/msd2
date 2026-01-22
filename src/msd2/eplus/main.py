from pathlib import Path

from loguru import logger
from replan2eplus.ops.subsurfaces.user_interfaces import EdgeGroup, SubsurfaceInputs
from msd2.eplus.interfaces import make_details, read_layout_to_ezcase_rooms
from replan2eplus.ezcase.ez import EZ
from replan2eplus.ops.zones.user_interface import Room
from msd2.config import WEATHER_FILE
from msd2.eplus.interfaces import EdgeGroupModel
from polymap.cli.make.utils import get_case_name


edge_groups_dict: dict[str, list[EdgeGroupModel]] = {
    "18380": [
        EdgeGroupModel(
            edges=[("room_0", "corridor_4"), ("room_0", "living_dining_3")],
            detail="door",
            type_="Zone_Zone",
        ),
        EdgeGroupModel(
            edges=[("room_0", "NORTH"), ("room_0", "WEST")],
            detail="window",
            type_="Zone_Direction",
        ),
    ],
    "97837": [
        EdgeGroupModel(
            edges=[("bedroom_3", "kitchen_0"), ("bathroom_1", "bedroom_2")],
            detail="door",
            type_="Zone_Zone",
        ),
        EdgeGroupModel(
            edges=[("bedroom_3", "NORTH"), ("kitchen_0", "SOUTH")],
            detail="window",
            type_="Zone_Direction",
        ),
    ],
}


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


def layout_to_idf(path: Path, out_path: Path, run: bool = False):
    rooms = read_layout_to_ezcase_rooms(path)
    case_name = get_case_name(path)

    if case_name in edge_groups_dict.keys():
        logger.debug(f"Found case name: {case_name}")
        edge_group_models = edge_groups_dict[case_name]
        edge_groups = [i.edge_group for i in edge_group_models]
        logger.debug(f"Adding edge groups {edge_groups}")

    else:
        edge_groups = []

    case = generate_idf(rooms, edge_groups, out_path, run)
    return case
