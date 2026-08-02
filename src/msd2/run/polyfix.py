from dataclasses import dataclass
from pathlib import Path

from msd2.run.dataset import DataLoader


@dataclass
class BatchManager:
    batch_id: int
    cases: list[int]
    succeeded: list[int] = []
    failed: dict[int, PolyFixError] = {}

    def update_success(self, unit_id: int):
        self.succeeded.append(unit_id)

    def update_failures(self, unit_id: int, error: PolyFixError):
        self.failed[unit_id] = error

    def save_report(self, path: Path):
        d = self.__dict__
        pass


# dl = DataLoader(ds, batch_size)  # pass in data loader


def handle_batch(dl: DataLoader, batch_ix: int):
    def handle_case(unit_id: int):
        geom_path = dl.dataset.paths.preprocessed_case_tuples(str(unit_id)).rooms

        pf = PolyFixer(geom_path)
        try:
            pf.run()
        except PolyFixError as e:
            bm.update_failures(unit_id, e)

    batch_ids = dl.get_batch_by_ix(batch_ix)

    bm = BatchManager(batch_id=batch_ix, cases=batch_ids)
    for id in batch_ids:
        handle_case(id)
