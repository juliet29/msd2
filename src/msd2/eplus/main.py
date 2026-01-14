from pathlib import Path
from msd2.eplus.interfaces import read_layout_to_ezcase_rooms
from replan2eplus.ezcase.ez import EZ
from replan2eplus.ops.zones.user_interface import Room
from msd2.config import WEATHER_FILE

# from resp.config import ANALYSIS_PERIOD, INPUT_CAMPAIGN_NAME, WEATHER_FILE
# from resp.eplus.campaign import campaign_data, campaign_defn
# from resp.eplus.interfaces import make_details
# from resp.paths import DynamicPaths
#


def generate_idf(rooms: list[Room], out_path: Path, run: bool = False):
    case = EZ(output_path=out_path, epw_path=WEATHER_FILE)
    case.add_zones(rooms)

    # subsurface_inputs = SubsurfaceInputs(
    #     edge_groups, make_details()  # pyright: ignore[reportArgumentType]
    # )
    # case.add_subsurfaces(subsurface_inputs)
    case.add_constructions()
    case.add_airflow_network()
    case.save_and_run(
        output_path=out_path, run=run, save=True
    )  # TODO: shouldlnt have to specify twice in different places.
    return case


def layout_to_idf(path: Path, out_path: Path, run: bool = False):
    rooms = read_layout_to_ezcase_rooms(path)

    # print(rooms)
    case = generate_idf(rooms, out_path, run)
    # bp = make_base_plot(case)
    # bp.show()
