from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from loguru import logger
from polyfix.main.fix_class import PolyfixError
from polyfix.main.main_class import PolyFixer
from tqdm import tqdm
from utils4plans.io import make_dir, write_json

from msd2.run.dataset import DataLoader
from msd2.run.logs import batch_console, log_to_file


@dataclass
class BatchManager:
    batch_id: int
    cases: list[int]
    succeeded: list[int] = []
    failed: dict[int, PolyfixError] = {}

    def update_success(self, unit_id: int):
        self.succeeded.append(unit_id)

    def update_failures(self, unit_id: int, error: PolyfixError):
        self.failed[unit_id] = error  # TODO: make sure this is serializable!

    def failure_summary(self):
        return Counter(self.failed.values())

    def save_report(self, path: Path):
        d = self.__dict__
        d["failure_summary"] = self.failure_summary()
        make_dir(path)
        write_json(d, path)

        pass


# dl = DataLoader(ds, batch_size)  # pass in data loader
#


def handle_batch(dl: DataLoader, batch_ix: int):
    def handle_case(unit_id: int):
        paths = dl.dataset.paths
        geom_path = paths.preprocessed_case_tuples(unit_id).rooms
        out_path = paths.processed_case_path(unit_id)
        log_path = paths.processed_case_path_log(unit_id)

        with log_to_file(log_path):
            pf = PolyFixer(init_geom=geom_path, save_loc=out_path)
            try:
                pf()
            except PolyfixError as e:
                logger.bind(to_console=True, unit_id=unit_id).error(
                    f"Failure for {unit_id} | {e.stage}"
                )
                bm.update_failures(unit_id, e)
                return
            bm.update_success(unit_id)

    batch_ids = dl.get_batch_by_ix(batch_ix)

    bm = BatchManager(batch_id=batch_ix, cases=batch_ids)

    logger.remove()
    with batch_console():
        for id in tqdm(batch_ids, desc=f"Handling batch {batch_ix}"):
            handle_case(id)

    bm.save_report(
        dl.dataset.root / "batch_reports" / f"bs{dl.batch_size}_bix{batch_ix}.json"
    )
