from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger
from polyfix.main.fix_class import PolyfixError
from polyfix.main.main_class import PolyFixer
from rich.pretty import pretty_repr
from tqdm import tqdm
from utils4plans.io import make_dir, write_json
from utils4plans.io.extras.figures import save_mpl_fig
from utils4plans.logs import logset

from msd2.run.dataset import DataLoader
from msd2.run.logs import batch_console, log_to_file


@dataclass
class BatchManager:
    batch_id: int
    cases: list[int]
    succeeded: list[int] = field(default_factory=list)
    failed: dict[int, PolyfixError] = field(default_factory=dict)

    def update_success(self, unit_id: int):
        self.succeeded.append(unit_id)

    def update_failures(self, unit_id: int, error: PolyfixError):
        self.failed[unit_id] = error  # TODO: make sure this is serializable!

    def failure_summary(self):
        res = dict(Counter([i.stage.name for i in self.failed.values()]))
        res["SUCCEEDED"] = len(self.succeeded)
        return res

    def save_report(self, path: Path):
        d = {}
        d["succeeded"] = self.succeeded
        d["failed"] = {k: (v.stage.name, str(v)) for k, v in self.failed.items()}
        d["failure_summary"] = self.failure_summary()
        make_dir(path)
        write_json(d, path)

    def show_report(self):
        res = self.failure_summary()
        logger.info(pretty_repr(res))
        logger.success(f"Successful runs: {pretty_repr(self.succeeded)}")
        # logger.info(f"{}")

        pass


# dl = DataLoader(ds, batch_size)  # pass in data loader
#


def handle_batch(dl: DataLoader, batch_ix: int, unit_ixes: list[int] = []):
    def handle_case(unit_id: int):
        paths = dl.dataset.paths
        unit_paths = paths.unit(unit_id)
        geom_path = unit_paths.pre_process.layout
        out_path = unit_paths.process.case
        log_path = unit_paths.process.log

        with log_to_file(log_path):
            pf = PolyFixer(init_geom=geom_path, save_loc=out_path, save_angle=True)
            try:
                pf()
            except PolyfixError as e:
                # TODO: put this all in a function
                # full stack trace -> per-unit file only (not tagged to_console)
                logger.opt(exception=e).error(f"Failure for {unit_id} | {e.stage.name}")
                # short line -> console (also lands in the file, harmlessly)
                logger.bind(to_console=True, unit_id=unit_id).error(
                    f"failed at {e.stage.name}"
                )
                bm.update_failures(unit_id, e)
                return
            bm.update_success(unit_id)

    batch_ids = dl.get_batch_by_ix(batch_ix)
    if unit_ixes:
        batch_ids = [i for i in batch_ids if i in unit_ixes]

    bm = BatchManager(batch_id=batch_ix, cases=batch_ids)

    logger.remove()
    with batch_console():
        for id in tqdm(batch_ids, desc=f"Handling batch {batch_ix}"):
            handle_case(id)

    bm.save_report(
        dl.dataset.root / "batch_reports" / f"bs{dl.batch_size}_bix{batch_ix}.json"
    )

    logset()
    bm.show_report()


def handle_energy_model_making(unit_id: int, path: Path):
    ds = Dataset(PATH)
    df = ds.partitioned_df.get_unit_df(CASE)
    assert df is not None

    # try and log errors
    fl = FullLayout(
        ds.paths.pr_case_reconciled(CASE), ds.paths.pr_case_angle(CASE), CASE, df
    )

    cfg = MSDConfigSchema(3, Path(""), AnalysisPeriod("", 1, 2, 2, 3), Path(""))

    # try and log errors
    case = layout_to_idf(fl, cfg)
    bp = make_base_plot(case, cardinal_expansion_factor=1.1)
    save_mpl_fig(bp.fig, ds.paths.e_fig)

    # try and log errors
    case.save_and_run(save=True, run=True)

    pass
