from cyclopts import App

from msd2.paths import ProjectPaths
from msd2.run.dataset import DataLoader, Dataset

# stress test for run module

runstress = App("rs")


@runstress.command()
def fc():
    p = 0
    ds = Dataset(ProjectPaths.data.test_msd)
    ds.downselect()
    ds.pre_process()

    dl = DataLoader(ds, 50)
    print(len(dl))
    batch = dl.get_batch_by_ix(0)
    print(batch)


# TODOs:
# add polyfix, utils4plans as editable imports
# try to run this, identify all the issues that arise. look for best analogues for broken mappings between polyfix, utils and here..
# focus is on geom, readin, and run modules
