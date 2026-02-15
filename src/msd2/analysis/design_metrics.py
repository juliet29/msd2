from loguru import logger
import polars as pl

from pathlib import Path

from polyfix.cli.make.utils import get_case_name


def handle_design_metrics(paths: list[Path]):
    def handle(path):
        case = get_case_name(path)
        res = pl.read_csv(path)

        df = res.with_columns(pl.lit(case).alias("case"))
        logger.debug(df)

        return df

    dfs = [handle(path) for path in paths]
    return pl.concat(dfs, how="vertical_relaxed")
