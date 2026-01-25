import polars as pl
from pathlib import Path
from typing import NamedTuple
from replan2eplus.results.sql import get_qoi
from replan2eplus.ops.output.interfaces import OutputVariables


from replan2eplus.ezcase.ez import EZ


class Metrics(NamedTuple):
    temperature: float
    ventilation: float
    mixing: float


def get_afn_zone_names(path: Path):
    case = EZ(path)
    afn_zones = case.objects.airflow_network.zones
    afn_zone_names = [i.zone_name.upper() for i in afn_zones]
    return afn_zone_names


def get_space_and_time_avg_for_qoi(
    idf_path: Path, sql_path: Path, qoi: OutputVariables
):
    data = get_qoi(qoi, sql_path).data_arr
    afn_zone_names = get_afn_zone_names(idf_path)
    afn_filter = data.space_names.isin(afn_zone_names)
    afn_data = data.sel(space_names=afn_filter)
    return float(afn_data.mean())


def calc_metrics(idf_path: Path, sql_path: Path, outpath: Path):
    qois: list[OutputVariables] = [
        "Zone Mean Air Temperature",
        "AFN Zone Ventilation Volume",
        "AFN Zone Mixing Volume",
    ]
    metrics = Metrics(
        *[get_space_and_time_avg_for_qoi(idf_path, sql_path, qoi) for qoi in qois]
    )
    df = pl.DataFrame(metrics._asdict())
    # logger.debug(df)
    df.write_csv(outpath)
