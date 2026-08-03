from contextlib import contextmanager
from pathlib import Path

from loguru import logger
from tqdm import tqdm
from utils4plans.io import make_dir

# plain (no rich markup) format for the per-unit file sinks
FILE_FORMAT = (
    "{time:HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {extra} | {message}"
)


@contextmanager
def log_to_file(path: Path):
    make_dir(path)
    sink_id = logger.add(
        path,
        level="TRACE",
        format=FILE_FORMAT,
        mode="w",  # fresh file per run; use "a" to append
        enqueue=False,  # cases run sequentially
        backtrace=True,  # print stack traces
        diagnose=True,
    )
    try:
        yield
    finally:
        logger.remove(sink_id)


@contextmanager
def batch_console():
    sink_id = logger.add(
        lambda msg: tqdm.write(msg, end=""),  # play nice with the progress bar
        level="ERROR",
        filter=lambda record: record["extra"].get("to_console", False),
        format="<red>{level.icon} unit {extra[unit_id]}</red> | {message}",
        colorize=True,
    )
    try:
        yield
    finally:
        logger.remove(sink_id)
