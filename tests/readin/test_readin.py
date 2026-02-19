from msd2.examples.examples import UnitIds
from msd2.examples.paths import ExamplePaths
from msd2.readin.access import access_datasets_by_unit_ids, get_ids_by_indices


def test_get_ids():
    res = get_ids_by_indices(ExamplePaths.valid_ids_csv, 0, 500)
    assert len(res) == 500


def test_get_ids_by_indices():
    res = get_ids_by_indices(ExamplePaths.valid_ids_csv, 1, 3)
    assert max(res) < 5000


def test_access_datasets_by_unit_ids():
    res = access_datasets_by_unit_ids(UnitIds.valid_unit_ids).collect()
    assert len(res.unique("unit_id")) == len(UnitIds.valid_unit_ids)
