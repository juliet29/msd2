from rich import print
from msd2.readin.utils import access_dataset
from msd2.readin.filters import (
    all_unit_ids,
)


def test_get_all_unit_ids():
    df = access_dataset()
    res = all_unit_ids(df)
    print(res)


if __name__ == "__main__":
    test_get_all_unit_ids()
