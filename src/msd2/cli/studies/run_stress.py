from cyclopts import App

from msd2.paths import ProjectPaths
from msd2.run.batch_polyfix import handle_batch
from msd2.run.dataset import DataLoader, Dataset

# stress test for run module

runstress = App("rs")


@runstress.command()
def fc():
    ds = Dataset(ProjectPaths.data.test_msd)
    # ds.downselect()
    # ds.pre_process()

    dl = DataLoader(ds, 50)
    print(len(dl))

    batch = dl.get_batch_by_ix(100)
    # print(dl.map.values())
    print(batch)


@runstress.command()
def fd():
    ds = Dataset(ProjectPaths.data.test_msd)

    dl = DataLoader(ds, batch_size=20)

    # batch = dl.get_batch_by_ix(0)
    handle_batch(dl, 0)
