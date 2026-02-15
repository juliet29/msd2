from pathlib import Path
from functools import reduce
from loguru import logger
import polars as pl
import xarray as xr
from polyfix.cli.make.utils import get_case_name
from typing import Literal
import altair as alt
from msd2.analysis.data import QOI, QOIRegistry


AltairRenderType = Literal["browser", "png"]


def set_altair_render(r: AltairRenderType = "browser"):
    alt.renderers.enable(r)


TimeOfDay = Literal["Night", "Day"]


class DaySplit:
    DATE_START = 0
    MORN_END = 6
    DAY_END = 18
    DATE_END = 23

    @property
    def morning_range(self):
        return range(self.DATE_START, self.MORN_END)

    @property
    def day_range(self):
        return range(self.MORN_END, self.DAY_END)

    @property
    def night_range(self):
        return range(self.DAY_END, self.DATE_END)

    def update_attrs(self, arr: xr.DataArray, time_of_day: TimeOfDay):
        arr.attrs["time_of_day"] = time_of_day
        return arr

    def daytime_data(self, arr: xr.DataArray):
        res = arr.isel(
            datetimes=(arr.datetimes.dt.hour.isin(self.day_range))
        )  # TODO: could move this up to the range..
        return self.update_attrs(res, "Day")

    def nightime_data(self, arr: xr.DataArray):
        pass
        early_morning = arr.isel(
            datetimes=(arr.datetimes.dt.hour.isin(self.morning_range))
        )
        night = arr.isel(datetimes=(arr.datetimes.dt.hour.isin(self.night_range)))
        res = xr.concat([early_morning, night], dim="datetimes")
        return self.update_attrs(res, "Night")

    def process(self, arr: xr.DataArray, time_of_day: TimeOfDay):
        if time_of_day == "Day":
            return self.daytime_data(arr)
        else:
            return self.nightime_data(arr)


def convert_xarray_to_polars(data: xr.DataArray | xr.Dataset, name=""):
    if name:
        data.name = name
    return pl.from_pandas(data.to_dataframe(), include_index=True)


def handle_data(paths: list[Path]):
    def handle(path):
        res = xr.open_dataset(path)
        case = get_case_name(path)
        return (case, res)

    d = {}
    for path in paths:
        case, res = handle(path)
        d[case] = res
    return d


def tod_qoi_dataset(casedata: dict[str, xr.Dataset], qoi: QOI, time_of_day: TimeOfDay):
    d = {}
    for k, v in casedata.items():
        d[k] = DaySplit().process(v[qoi.nickname], time_of_day).mean()
    logger.debug(qoi.nickname)
    df = pl.DataFrame(d).unpivot(variable_name="case", value_name=qoi.nickname)
    # ds = xr.Dataset(d)
    # logger.debug(QOI.nickname)
    # logger.debug(ds)
    #
    # df = convert_xarray_to_polars(ds).unpivot(
    #     index="datetimes", variable_name="case", value_name=QOI.nickname
    # )
    # TODO -> take the mean!
    return df


def join_dfs(dfs: list[pl.DataFrame]):
    df0 = dfs[0]
    other_dfs = dfs[1:]

    merged_df = reduce(lambda left, right: left.join(right, on="case"), other_dfs, df0)
    return merged_df


def make_summary_dataset(paths: list[Path]):

    qois = [QOIRegistry.net_flow, QOIRegistry.temp]

    casedata = handle_data(paths)

    def tod_df(tod: TimeOfDay):
        dfs = [tod_qoi_dataset(casedata, qoi, tod) for qoi in qois]
        res = join_dfs(dfs)
        logger.debug(res)
        return res

    return tod_df("Day"), tod_df("Night")


def plot_tod_qoi_dataset(
    casedata: dict[str, xr.Dataset], qoi: QOI, time_of_day: TimeOfDay
):
    df = tod_qoi_dataset(casedata, qoi, time_of_day)
    # prepare
    prep_df = df.group_by("case").agg(pl.col("value").mean())
    logger.debug(prep_df)
    chart = (
        alt.Chart(prep_df)
        .mark_bar()
        .encode(
            alt.X("case:O").title("Cases").sort("y"), alt.Y("value:Q").title(qoi.label)
        )
    )
    return df, chart
