from pathlib import Path

from redun import Scheduler
from redun.config import Config
from utils4plans.io import make_dir

from msd2.config import MSDConfigSchema
from msd2.exec.logs import redun_console_logger
from msd2.exec.pipeline import process_batch
from msd2.run.dataset_paths import DatasetPaths


def run_batch(
    unit_ids: list[int],
    dataset_root: Path,
    config: MSDConfigSchema,
    batch_ix: int,
    max_workers: int,
    retry_failed: bool = False,
) -> dict:
    paths = DatasetPaths(dataset_root)
    make_dir(paths.redun_db)
    scheduler = Scheduler(
        logger=redun_console_logger(),
        config=Config(
            {
                "backend": {"db_uri": f"sqlite:///{paths.redun_db}"},
                "executors.default": {
                    "type": "local",
                    "mode": "process",
                    "max_workers": str(max_workers),
                    "start_method": "forkserver",
                },
            }
        ),
    )
    scheduler.load()
    batch = process_batch(unit_ids, paths, config, batch_ix)
    return scheduler.run(batch, cache=not retry_failed)
