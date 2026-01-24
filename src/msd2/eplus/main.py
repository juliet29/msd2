from collections import Counter
from pathlib import Path

from loguru import logger
from replan2eplus.ops.subsurfaces.user_interfaces import (
    EdgeGroup,
    SubsurfaceInputs,
    Edge,
)
from rich.pretty import pretty_repr
from msd2.eplus.interfaces import (
    make_details,
    read_edges_to_ezcase_edge_groups,
    read_layout_to_ezcase_rooms,
)
from replan2eplus.ezcase.ez import EZ
from replan2eplus.ops.zones.user_interface import Room
from msd2.config import WEATHER_FILE
from replan2eplus.ops.subsurfaces.logic.select import get_zones_by_plan_name


def handle_windows(case: EZ, windows_edge_group: EdgeGroup):
    assert windows_edge_group.type_ == "Zone_Direction"

    seen_zones = Counter()

    def create(edge: Edge):
        zone_a = get_zones_by_plan_name(edge.space_a, case.objects.zones)
        seen_zones[zone_a.zone_name] += 1
        # find first surface with an outside boundary condition
        potential_surfs = list(
            filter(
                lambda x: x.boundary_condition == "outdoors"
                and x.surface_type == "wall",
                zone_a.surfaces,
            )
        )
        seen_count = seen_zones[zone_a.zone_name] - 1

        if seen_count > len(potential_surfs):
            raise IndexError("Seen count > num potential surfs!")
        # get the direction of the first surf
        drn = list(potential_surfs)[seen_count].direction

        new_edge = Edge(edge.space_a, drn.name)
        return new_edge

    new_edges = [create(e) for e in windows_edge_group.edges]
    new_group = EdgeGroup(
        new_edges, windows_edge_group.detail, windows_edge_group.type_
    )

    logger.debug(f"Edges to add: {pretty_repr([i.as_tuple for i in new_group.edges])}")
    return new_group


def handle_edge_groups(case: EZ, edge_groups: list[EdgeGroup]):
    for ix, eg in enumerate(edge_groups):
        if eg.type_ == "Zone_Direction":
            edge_groups[ix] = handle_windows(case, eg)

    return edge_groups


def generate_idf(
    rooms: list[Room], edge_groups: list[EdgeGroup], out_path: Path, run: bool = False
):
    case = EZ(output_path=out_path, epw_path=WEATHER_FILE)
    case.add_zones(rooms)

    corrected_edge_groups = handle_edge_groups(case, edge_groups)

    subsurface_inputs = SubsurfaceInputs(
        corrected_edge_groups, make_details()  # pyright: ignore[reportArgumentType]
    )
    case.add_subsurfaces(subsurface_inputs)

    sinfo = [
        {"name": s.display_name, "idf_name": s.subsurface_name}
        for s in case.objects.subsurfaces
    ]

    logger.info(pretty_repr(sinfo))

    case.add_constructions()
    case.add_airflow_network()
    case.save_and_run(
        output_path=out_path, run=run, save=True
    )  # TODO: shouldlnt have to specify twice in different places.
    return case


def layout_to_idf(edge_path: Path, layout_path: Path, outpath: Path):
    rooms = read_layout_to_ezcase_rooms(layout_path)
    # only doing one type for now
    edge_group_holder = read_edges_to_ezcase_edge_groups(edge_path)
    egs = [edge_group_holder.interior_door_edges, edge_group_holder.window_edges]
    logger.debug(f"Rooms to add: {[i.name for i in rooms]}")
    for eg in egs:
        logger.debug(f"Edges to add: {pretty_repr([i.as_tuple for i in eg.edges])}")

    # for now, only consider door edges, need different approach for windows..
    # # also need to do airboundaries

    case = generate_idf(rooms, egs, outpath.parent, run=False)
    return case
