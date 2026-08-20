from dataclasses import dataclass
from pathlib import Path

from loguru import logger


@dataclass
class PreProcessPaths:
    root: Path

    @property
    def layout(self):
        return self.root / "rooms.json"

    @property
    def unit_df(self):
        return self.root / "unit.parquet"


@dataclass
class ProcessPaths:
    root: Path

    @property
    def case(self):
        return self.root

    @property
    def log(self):
        return self.root / "out.log"

    @property
    def angle(self):
        return self.root / "angle.json"

    @property
    def reconciled(self):
        return self.root / "reconcile/out.json"


@dataclass
class EplusPaths:
    root: Path

    @property
    def case(self):
        return self.root

    @property
    def log(self):
        return self.root / "out.log"

    @property
    def fig(self):
        return self.root / "out.png"


@dataclass
class UnitPaths:
    unit_id: str
    pre_processed_path: Path
    processed_path: Path
    eplus_model_path: Path

    @property
    def pre_process(self):
        return PreProcessPaths(self.pre_processed_path / self.unit_id)

    @property
    def process(self):
        return ProcessPaths(self.processed_path / self.unit_id)

    @property
    def eplus(self):
        return EplusPaths(self.eplus_model_path / self.unit_id)


class DatasetPaths:
    def __init__(self, root: Path) -> None:
        logger.info(f"Intializing dataset paths for {root}")
        self.root = root

        self.data = self.root / "data"
        self.raw = self.data / "raw"

        self.pre_processed = self.root / "pre_processed"
        self.processed = self.root / "processed"
        self.eplus_model = self.root / "model"

        self.artifacts = self.root / "artifacts"
        self.unit_ids_csv = self.artifacts / "unit_ids.csv"

        self.redun_db = self.root / ".redun" / "redun.db"

    def unit(self, unit_id: int):
        return UnitPaths(
            str(unit_id),
            self.pre_processed,
            self.processed,
            self.eplus_model,
        )
