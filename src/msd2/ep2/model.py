from icecream import ic
from loguru import logger
from plan2eplus.ezcase.ez import EZ, SubsurfaceInputs
from plan2eplus.ops.subsurfaces.user_interfaces import (
    SubsurfaceInputs,
)
from plan2eplus.ops.zones.user_interface import Room
from rich.pretty import pretty_repr

from msd2.config import MSDConfigSchema
from msd2.ep2.full_layout import FullLayout
from msd2.eplus.interfaces import (
    edges_to_ezcase_edge_groups,
    layout_to_ezcase_rooms,
    make_details,
)


def generate_idf(
    rooms: list[Room],
    subsurface_inputs: SubsurfaceInputs,
):
    case = EZ()
    case.add_zones(rooms)

    case.add_subsurfaces(subsurface_inputs)

    sinfo = [
        {"name": s.display_name, "idf_name": s.subsurface_name}
        for s in case.objects.subsurfaces
    ]

    logger.info(pretty_repr(sinfo))

    case.add_constructions()
    case.add_airflow_network()
    return case


def layout_to_idf(fl: FullLayout, msd_config: MSDConfigSchema):
    cfg = msd_config
    ol = fl.to_oriented_layout()
    rooms = layout_to_ezcase_rooms(ol.layout, cfg.room_height)
    deg = edges_to_ezcase_edge_groups(ol)

    details = make_details(cfg.room_height)
    ic(deg.simple_edge_groups)

    # TODO: better mapping here for detail types
    subsurface_inputs = SubsurfaceInputs(deg.simple_edge_groups, details)  # pyright: ignore[reportArgumentType]
    return generate_idf(rooms, subsurface_inputs)
