from loguru import logger
from plan2eplus.ezcase.ez import EZ
from plan2eplus.ops.subsurfaces.user_interfaces import (
    SubsurfaceInputs,
)
from plan2eplus.ops.zones.user_interface import Room
from rich.pretty import pretty_repr

from msd2.config import MSDConfigSchema
from msd2.ep2.full_layout import FullLayout
from msd2.ep2.interfaces import (
    edges_to_ezcase_edge_groups,
    layout_to_ezcase_rooms,
    make_details,
)


class SingleSideAFNError(Exception): ...


def generate_idf(
    rooms: list[Room],
    subsurface_inputs: SubsurfaceInputs,
):
    case = EZ(read_existing=False)
    case.add_zones(rooms)

    case.add_subsurfaces(subsurface_inputs)

    case.add_constructions()
    case.add_airflow_network()
    return case


def layout_to_idf(fl: FullLayout, cfg: MSDConfigSchema):
    ol = fl.to_oriented_layout()
    rooms = layout_to_ezcase_rooms(ol.layout, cfg.room_height)
    deg = edges_to_ezcase_edge_groups(ol)

    details = make_details(cfg.room_height)
    logger.info(f"Input edges: {pretty_repr(deg.simple_edge_groups)}")

    subsurface_inputs = SubsurfaceInputs(deg.simple_edge_groups, details)  # pyright: ignore[reportArgumentType]
    case = generate_idf(rooms, subsurface_inputs)

    external_facade_directions = {
        s.surface.direction.name
        for s in case.objects.subsurfaces
        if not s.neighbor_name
    }
    if len(external_facade_directions) < 2:
        raise SingleSideAFNError(
            f"AFN external openings are all on {external_facade_directions}; "
            "at least two facades are required to avoid a single-side boundary condition."
        )

    case.run_settings.output_path = cfg.save_loc
    case.run_settings.analysis_period = cfg.analysis_period
    case.run_settings.epw_path = cfg.weather_file
    # case.save_and_run(run=True, save=True)
    return case
