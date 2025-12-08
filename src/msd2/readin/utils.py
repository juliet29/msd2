# TODO use patito to verify schema!
# Set the path to the file you'd like to load


import kagglehub
from kagglehub import KaggleDatasetAdapter
from dataframely import LazyFrame
from msd2.readin.interfaces import MSDSchema


def access_dataset() -> LazyFrame[MSDSchema]:
    file_path = "mds_V2_5.372k.csv"

    # Load the latest version
    lf = kagglehub.dataset_load(
        KaggleDatasetAdapter.POLARS,
        "caspervanengelenburg/modified-swiss-dwellings",
        file_path,
    )
    # res = MSDSchema.validate(lf)

    return MSDSchema.cast(lf)
