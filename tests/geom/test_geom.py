from msd2.examples.examples import SampleUnit
from msd2.geom.connectivity import extract_connectivity_graph
from msd2.geom.create import df_unit_to_room_and_connection_data
from msd2.geom.io import write_unit
from msd2.readin.access import access_datasets_by_unit_ids


# def test_write_unit():
#     pass
#
#
# def get_test_dataframe():
#     pass


class TestGenerateInitialData:
    @property
    def dataframe(self):
        return access_datasets_by_unit_ids([SampleUnit.unit_id]).collect()

    @property
    def get_room_data(self):
        rooms, connections = df_unit_to_room_and_connection_data(self.dataframe)
        return rooms, connections

    def test_df_to_room_data(self):
        rooms, connections = self.get_room_data
        assert len(rooms) == SampleUnit.num_rooms
        assert len(connections) == SampleUnit.num_connections

    def test_extract_connectivity(self):
        rooms, connections = self.get_room_data
        edges = extract_connectivity_graph(rooms, connections)
        assert len(edges) == SampleUnit.num_edges

    def test_write_unit(self, tmp_path):
        write_unit(
            SampleUnit.unit_id, tmp_path / "edges.json", tmp_path / "layout.json"
        )

    # def test_extract_conn_data():
    #     pass
