from pathlib import Path

from msd2.geom.io import CasePaths


class DatasetPaths:  # TODO: this has to be in a differnt folder..
    def __init__(self, root: Path) -> None:
        self.root = root

        self.data = self.root / "data"
        self.raw = self.data / "raw"

        self.pre_processed = self.root / "pre_processed"
        self.processed = self.root / "processed"

        self.artifacts = self.root / "artifacts"
        self.unit_ids_csv = self.artifacts / "unit_ids.csv"

    def preprocessed_case_tuples(self, case_name: str):
        return CasePaths(
            edges=self.pre_processed / case_name / "edges.json",
            rooms=self.pre_processed / case_name / "rooms.json",
        )

    def preprocessed_case_paths(self, case_name: str):
        return self.pre_processed / case_name
