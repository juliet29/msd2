import logging
from contextlib import contextmanager
from itertools import takewhile
from pathlib import Path

from loguru import logger
from tqdm import tqdm
from utils4plans.io import make_dir

# plain (no rich markup) format for the per-unit file sinks
FILE_FORMAT = (
    "{time:HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {extra} | {message}"
)


def summarize_redun_job(message: str) -> str | None:
    if "msd2." not in message:
        return None
    action = "Reject" if message.startswith("***") else message.split()[0]
    task = message.partition("msd2.")[2].partition("(")[0]
    after_unit = message.partition("unit_id=")[2].lstrip("'\"")
    unit = "".join(takewhile(str.isdigit, after_unit))
    unit_label = f" unit={unit}" if unit else ""
    return f"{action} {task}{unit_label}"


class TrimRedunJobLines(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        summary = summarize_redun_job(message)
        if summary is None:
            return message.startswith("***") or "Execution duration" in message
        record.msg = summary
        record.args = ()
        return True


def redun_console_logger() -> logging.Logger:
    logging.getLogger("redun").setLevel(logging.WARNING)
    console = logging.getLogger("msd2.redun")
    console.setLevel(logging.INFO)
    console.propagate = False
    console.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[redun] %(message)s"))
    console.addHandler(handler)
    console.addFilter(TrimRedunJobLines())
    return console


@contextmanager
def log_to_file(path: Path):
    make_dir(path)
    logger.remove()
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
