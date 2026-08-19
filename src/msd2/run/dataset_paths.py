from pathlib import Path

from loguru import logger

from msd2.geom.io import CasePaths


class DatasetPaths:
    def __init__(self, root: Path) -> None:
        logger.info(f"Intializing dataset paths for {root}")
        self.root = root

        self.data = self.root / "data"
        self.raw = self.data / "raw"

        self.pre_processed = self.root / "pre_processed"
        self.processed = self.root / "processed"

        self.artifacts = self.root / "artifacts"
        self.unit_ids_csv = self.artifacts / "unit_ids.csv"

    def preprocessed_case_tuples(self, unit_id_: int):
        unit_id = str(unit_id_)
        return CasePaths(
            rooms=self.pre_processed / unit_id / "rooms.json",
        )

    def pr_case(self, unit_id: int):
        return self.processed / str(unit_id)

    def pr_case_log(self, unit_id: int):
        return self.processed / str(unit_id) / "out.log"

    def pr_case_angle(self, unit_id: int):
        return self.processed / str(unit_id) / "angle.json"

    def pr_case_reconciled(self, unit_id: int):
        return self.processed / str(unit_id) / "reconcile/out.json"
