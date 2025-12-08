from msd2.readin.scripts import DatasetSummary
from msd2.readin.utils import access_dataset
from msd2.readin.filters import (
    all_unit_ids,
    sufficient_areas_unit_ids,
    unique_unit_ids,
    valid_geom_only_unit_ids,
    sample_unit_ids,
)


def test_sample_ids():
    res = sample_unit_ids(10)
    print(res)
    assert len(res) == 10


def test_get_all_unit_ids():
    df = access_dataset()
    res = all_unit_ids(df)
    assert res


def test_valid_geom_only_unit_ids():
    df = access_dataset()
    res = valid_geom_only_unit_ids(df)
    assert res


def summarize_dataset():
    df = access_dataset()
    summary = list(
        map(
            lambda fx: len(fx(df)),
            [
                all_unit_ids,
                valid_geom_only_unit_ids,
                sufficient_areas_unit_ids,
                unique_unit_ids,
            ],
        )
    )
    ds = DatasetSummary(*summary)
    ds.print()
    return ds


if __name__ == "__main__":
    test_sample_ids()
