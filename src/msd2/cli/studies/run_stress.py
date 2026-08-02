from cyclopts import App

from msd2.paths import ProjectPaths
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
