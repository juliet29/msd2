from pathlib import Path

from loguru import logger
from polyfix.geometry.ortho import FancyOrthoDomain
from polyfix.layout.interfaces import Layout
from polyfix.pydantic_models import layout_to_model
from utils4plans.io import write_json

from msd2.geom.connectivity import Edge, extract_connectivity_graph
from msd2.geom.create import df_unit_to_room_and_connection_data
from msd2.geom.interfaces import MSDEdgeModel, MSDEdgesModel, RoomData
from msd2.readin.access import (
    access_one_sample_dataset,
)


def write_connectivity_edges_to_json(edges: list[Edge], path: Path):
    msd_edges = MSDEdgesModel(
        edges=[MSDEdgeModel(a=edge.a, b=edge.b, conn=edge.conn) for edge in edges]
    )
    data = msd_edges.model_dump()
    write_json(data, path, OVERWRITE=True)


def write_room_data_to_json_as_layout(rooms: list[RoomData], path: Path):
    def room_data_to_layout(rooms: list[RoomData]):
        doms = map(lambda x: FancyOrthoDomain(x.coords, x.name), rooms)
        return Layout(list(doms))

    layout = room_data_to_layout(rooms)
    data = layout_to_model(layout).model_dump()
    write_json(data, path, OVERWRITE=True)


# def write_units(df: LazyFrame[MSDSchema], edge_path: Path, layout_path: Path):
#     for name, data in df.collect().group_by("unit_id"):
#         d = MSDSchema.validate(data)
#         rooms, connections = df_unit_to_room_and_connection_data(d)
#         edges = extract_connectivity_graph(rooms, connections)
#
#         n = str(int(name[0]))
#
#         # layout_path = path / n / "init_geom" / "out.json"
#         # edge_path = path / n / "edges" / "out.json"
#
#         write_room_data_to_json_as_layout(rooms, layout_path)
#         write_connectivity_edges_to_json(edges, edge_path)
#
#         logger.success(f"Finished writing layout and edges to {path /n} ")
#


def write_unit(unit_id: float, edge_path: Path, layout_path: Path):
    df = access_one_sample_dataset(unit_id).collect()

    rooms, connections = df_unit_to_room_and_connection_data(df)
    edges = extract_connectivity_graph(rooms, connections)

    write_room_data_to_json_as_layout(rooms, layout_path)
    write_connectivity_edges_to_json(edges, edge_path)

    logger.success(f"Finished writing layout and edges for {unit_id} ")


# def sample_unit_ids_to_files_as_layouts(
#     num_samples: int = NUM_SAMPLES, path: Path = DynamicPaths.workflow_inputs
# ):
#
#     df = access_random_sample_datasets(num_samples).collect()
#
#
# def generate_data_for_unit_ids(unit_ids: list[float], path: Path):
#     df = access_datasets_by_unit_ids(unit_ids)
