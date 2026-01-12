from msd2.geom.utils import df_unit_to_layout
from polymap.json_interfaces import dump_layout
from msd2.readin.access import access_one_sample_dataset


class TestConvert:
    ID = 65538

    @property
    def layout(self):
        id, df = access_one_sample_dataset(self.ID)
        layout = df_unit_to_layout(df.collect())
        return layout

    def test_convert_unit_to_layout(self):
        assert len(self.layout.domains) > 2

    def test_dump_layout(self):
        res = dump_layout(self.layout)
        assert res


if __name__ == "__main__":
    t = TestConvert()
    t.test_dump_layout()
