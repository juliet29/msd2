from collections import defaultdict
from dataclasses import dataclass, replace
from pathlib import Path

import polars as pl
from eppy.runner.run_functions import EnergyPlusRunError
from loguru import logger
from plan2eplus.visuals.simple_plots import make_base_plot
from polyfix.main.fix_class import PolyfixError, Stage
from polyfix.main.main_class import PolyFixer
from redun import File, catch, task
from rich.pretty import pretty_repr
from utils4plans.io import write_json
from utils4plans.io.extras.figures import save_mpl_fig

from msd2.config import MSDConfigSchema
from msd2.ep2.full_layout import FullLayout
from msd2.ep2.model import SingleSideAFNError, layout_to_idf
from msd2.exec.logs import log_to_file
from msd2.geom.exteriors import (
    ConnectionProcessingError,
    DroppedEntranceDoorError,
    EdgeProcessingError,
)
from msd2.readin.interfaces import MSDSchema
from msd2.run.dataset_paths import DatasetPaths, UnitPaths

redun_namespace = "msd2"

CATEGORY_ORDER = [f"FIX:{stage.name}" for stage in Stage] + [
    "TOO_FEW_OPENINGS",
    "DROPPED_ENTRANCE_DOOR",
    "SINGLE_SIDE",
    "BUILD",
    "RUN",
    "SUCCEEDED",
]


@dataclass(frozen=True)
class CaseOutcome:
    unit_id: int
    status: str
    stage: str
    detail: str


@task()
def fix_geometry(rooms: File, up: UnitPaths) -> File:
    with log_to_file(up.process.log):
        fixer = PolyFixer(
            init_geom=Path(rooms.path),
            save_loc=up.process.case,
            save_angle=True,
        )
        fixer()
    return File(str(up.process.reconciled))


@task()
def build_and_run_energy_model(
    reconciled: File,
    unit_df: File,
    up: UnitPaths,
    config: MSDConfigSchema,
) -> CaseOutcome:
    with log_to_file(up.eplus.log):
        layout = FullLayout(
            Path(reconciled.path),
            up.process.angle,
            int(up.unit_id),
            MSDSchema.cast(pl.read_parquet(unit_df.path)),
        )
        run_config = replace(config, save_loc=up.eplus.case)
        case = layout_to_idf(layout, run_config)
        base_plot = make_base_plot(case, cardinal_expansion_factor=1.1)
        save_mpl_fig(base_plot.fig, up.eplus.fig)
        case.save_and_run(save=True, run=True, verbose="s")
    return CaseOutcome(int(up.unit_id), "succeeded", "", str(up.eplus.case))


@task(cache=False)
def record_failure(error: Exception, unit_id: int) -> CaseOutcome:
    if isinstance(error, PolyfixError):
        stage = f"FIX:{error.stage.name}"
    elif isinstance(error, (EdgeProcessingError, ConnectionProcessingError)):
        stage = "TOO_FEW_OPENINGS"
    elif isinstance(error, DroppedEntranceDoorError):
        stage = "DROPPED_ENTRANCE_DOOR"
    elif isinstance(error, SingleSideAFNError):
        stage = "SINGLE_SIDE"
    elif isinstance(error, EnergyPlusRunError):
        stage = "RUN"
    else:
        stage = "BUILD"
    logger.bind(to_console=True, unit_id=unit_id).error(f"failed at {stage}")
    return CaseOutcome(unit_id, "failed", stage, str(error))


def process_case(up: UnitPaths, config: MSDConfigSchema):
    rooms = File(str(up.pre_process.layout))
    unit_df = File(str(up.pre_process.unit_df))
    reconciled = fix_geometry(rooms, up)
    outcome = build_and_run_energy_model(reconciled, unit_df, up, config)
    return catch(outcome, Exception, record_failure.partial(unit_id=int(up.unit_id)))


@task(cache=False)
def summarize_batch(
    outcomes: list[CaseOutcome], paths: DatasetPaths, batch_ix: int
) -> dict:
    units_by_category: dict[str, list[int]] = defaultdict(list)

    def register(outcome: CaseOutcome) -> None:
        category = "SUCCEEDED" if outcome.status == "succeeded" else outcome.stage
        units_by_category[category].append(outcome.unit_id)

    for outcome in outcomes:
        register(outcome)

    cases_by_category = {
        category: sorted(units_by_category[category])
        for category in CATEGORY_ORDER
        if category in units_by_category
    }
    failure_summary = {cat: len(units) for cat, units in cases_by_category.items()}
    failed = {o.unit_id: [o.stage, o.detail] for o in outcomes if o.status == "failed"}

    report = {
        "batch_ix": batch_ix,
        "n_cases": len(outcomes),
        "succeeded": cases_by_category.get("SUCCEEDED", []),
        "failed": failed,
        "failure_summary": failure_summary,
        "cases_by_category": cases_by_category,
    }
    write_json(report, paths.root / "batch_reports" / f"bix{batch_ix}.json")
    logger.info(pretty_repr(failure_summary))
    logger.info(pretty_repr(cases_by_category))
    return report


@task(cache=False)
def process_batch(
    unit_ids: list[int], paths: DatasetPaths, config: MSDConfigSchema, batch_ix: int
) -> dict:
    outcomes = [process_case(paths.unit(unit_id), config) for unit_id in unit_ids]
    return summarize_batch(outcomes, paths, batch_ix)
