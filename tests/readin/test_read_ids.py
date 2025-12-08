from msd2.readin.filters import sample_unit_ids


def test_many_set_interesection():
    s1 = {1, 2, 3, 4, 5, 6}
    s2 = {2, 3}
    s3 = {3, 4, 5}
    res = s1.intersection(s2, s3)
    assert res == {3}


def test_sample_ids():
    res = sample_unit_ids(10)
    print(res)
    assert len(res) == 10


if __name__ == "__main__":
    test_sample_ids()
