import shutil

from cyclopts import App
from loguru import logger
from utils4plans.io import make_dir

from msd2.paths import ProjectPaths
from msd2.run.batch_polyfix import handle_batch
from msd2.run.dataset import DataLoader, Dataset

# stress test for run module

runstress = App("rs")

PATH = ProjectPaths.data.test_msd_100


@runstress.command()
def clear_dir():
    shutil.rmtree(PATH)
    make_dir(PATH)


@runstress.command()
def fc():
    ds = Dataset(PATH)
    ds.downselect(n=80)
    ds.pre_process()
    logger.debug(ds.true_ids)

    dl = DataLoader(ds, 20)
    print(len(dl))

    # batch = dl.get_batch_by_ix(100)
    # # print(dl.map.values())
    # print(batch)
    #


@runstress.command()
def fd():
    ds = Dataset(PATH)

    dl = DataLoader(ds, batch_size=20)

    # batch = dl.get_batch_by_ix(0)
    # handle_batch(dl, 1, unit_ixes=[5389, 5478, 5531, 5542, 5299])
    handle_batch(dl, 0)
