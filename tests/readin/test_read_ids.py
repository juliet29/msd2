from msd2.readin.access import get_ids_by_indices, sample_unit_ids
from msd2.paths import DynamicPaths


def test_many_set_interesection():
    s1 = {1, 2, 3, 4, 5, 6}
    s2 = {2, 3}
    s3 = {3, 4, 5}
    res = s1.intersection(s2, s3)
    assert res == {3}


def test_sample_ids():
    res = sample_unit_ids(DynamicPaths.valid_ids_json, 10)

    print(res)
    assert len(res) == 10


def test_get_ids_by_indices():
    res = get_ids_by_indices(DynamicPaths.valid_ids_csv, 1, 3)
    assert max(res) < 5000


if __name__ == "__main__":
    test_sample_ids()
