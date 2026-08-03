from pathlib import Path

from msd2.geom.io import CasePaths


class DatasetPaths:
    def __init__(self, root: Path) -> None:
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
            edges=self.pre_processed / unit_id / "edges.json",
            rooms=self.pre_processed / unit_id / "rooms.json",
        )

    def processed_case_path(self, unit_id: int):
        return self.processed / str(unit_id)

    def processed_case_path_log(self, unit_id: int):
        return self.processed / str(unit_id) / "out.log"
