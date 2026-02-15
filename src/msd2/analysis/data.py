import xarray as xr
from pathlib import Path
from typing import NamedTuple
from plan2eplus.results.sql import get_qoi
from plan2eplus.ops.output.interfaces import OutputVariables


from plan2eplus.ezcase.ez import EZ


class Metrics(NamedTuple):
    temperature: float
    ventilation: float
    mixing: float


class QOI(NamedTuple):
    name: OutputVariables | str
    nickname: str
    unit: str

    @property
    def label(self):
        return f"{self.name} [{self.unit}]"

    def update_xarray(self, arr: xr.DataArray):
        arr.name = self.name
        arr.attrs["units"] = self.unit
        # TODO would be good to relate to the info that Ladybug gives..


class QOIRegistry:
    net_flow = QOI("AFN Net Linkage Flow Rate", "net_flow", "m3/s")
    temp = QOI("Zone Mean Air Temperature", "temp", "ºC")


def get_afn_zone_names(path: Path):
    case = EZ(path)
    afn_zones = case.objects.airflow_network.zones
    afn_zone_names = [i.zone_name.upper() for i in afn_zones]
    return afn_zone_names


# TODO move to calccs... probably related to registry?
def calc_net_flow(path: Path):
    f12: OutputVariables = "AFN Linkage Node 1 to Node 2 Volume Flow Rate"
    f21: OutputVariables = "AFN Linkage Node 2 to Node 1 Volume Flow Rate"

    f12_arr = get_qoi(f12, path).data_arr
    f21_arr = get_qoi(f21, path).data_arr
    arr = abs(f12_arr - f21_arr)
    return arr


def calc_space_averaged_net_flow_rate(path: Path):
    arr = calc_net_flow(path).mean(dim="space_names")
    QOIRegistry.net_flow.update_xarray(arr)

    return arr


def calc_space_averaged_temperature(idf_path: Path, sql_path: Path):
    qoi: OutputVariables = "Zone Mean Air Temperature"
    data = get_qoi(qoi, sql_path).data_arr

    afn_zone_names = get_afn_zone_names(idf_path)
    afn_filter = data.space_names.isin(afn_zone_names)

    arr = data.sel(space_names=afn_filter).mean(dim="space_names")
    QOIRegistry.temp.update_xarray(arr)

    return arr


def collect_data(idf_path: Path, sql_path: Path):
    temp = calc_space_averaged_temperature(idf_path, sql_path)
    flow_rate = calc_space_averaged_net_flow_rate(sql_path)
    ds = xr.Dataset(
        {QOIRegistry.temp.nickname: temp, QOIRegistry.net_flow.nickname: flow_rate}
    )
    return ds
    # logger.debug(df)
    # df.write_csv(outpath)
