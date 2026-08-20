import os
import shutil

from cyclopts import App
from loguru import logger
from rich.pretty import pretty_repr
from utils4plans.io import make_dir, read_json

from msd2.config import MSDConfig
from msd2.exec.execution import run_batch
from msd2.paths import MSD_CONFIG_PATH, ProjectPaths
from msd2.run.dataset import DataLoader, Dataset
from msd2.run.dataset_paths import DatasetPaths

fullrun = App("fr")

PATH = ProjectPaths.data.test_msd_100
BATCH_SIZE = 20
BATCH_IX = 0
WORKERS = os.cpu_count() or 4


@fullrun.command()
def preprocess(n: int | None = 100):
    shutil.rmtree(PATH, ignore_errors=True)
    make_dir(PATH)
    dataset = Dataset(PATH)

    artifacts_path = ProjectPaths.data.test_msd / "artifacts/unit_ids.csv"
    dataset.downselect(artifacts_path, n=n)
    # TODO: save the artifacts? / or maybe make a reference outside of any given one..

    dataset.pre_process()


@fullrun.command()
def clrp():
    dp = DatasetPaths(PATH)
    shutil.rmtree(dp.processed, ignore_errors=True)
    shutil.rmtree(dp.redun_db, ignore_errors=True)
    make_dir(dp.processed)
    # make_dir(dp.redun_db) # gets remade on next run


@fullrun.command()
def batch(batch_ix: int = BATCH_IX, workers: int = WORKERS):
    loader = DataLoader(Dataset(PATH), BATCH_SIZE)
    unit_ids = loader.get_batch_by_ix(batch_ix)

    config = MSDConfig(MSD_CONFIG_PATH).config
    summary = run_batch(unit_ids, PATH, config, batch_ix, workers)
    logger.info(pretty_repr(summary["failure_summary"]))


@fullrun.command()
def retry(batch_ix: int = BATCH_IX, workers: int = WORKERS):
    prior_report = read_json(PATH / "batch_reports" / f"bix{batch_ix}.json")
    failed_ids = [int(unit_id) for unit_id in prior_report["failed"]]
    logger.info(f"Retrying {len(failed_ids)} failed cases: {pretty_repr(failed_ids)}")
    config = MSDConfig(MSD_CONFIG_PATH).config
    run_batch(failed_ids, PATH, config, batch_ix, workers, retry_failed=True)


@fullrun.command()
def report(batch_ix: int = BATCH_IX):
    logger.info(pretty_repr(read_json(PATH / "batch_reports" / f"bix{batch_ix}.json")))
