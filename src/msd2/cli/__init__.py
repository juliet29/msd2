from rich import print
from loguru import logger
from rich.pretty import pretty_repr


def keep():
    print("hi")
    logger.info(pretty_repr({}))
