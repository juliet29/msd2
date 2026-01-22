from pathlib import Path

from polymap.pydantic_models import layout_to_model
from utils4plans.io import write_json

from msd2.geom.interfaces import RoomData, MSDEdgeModel, MSDEdgesModel

from polymap.geometry.ortho import FancyOrthoDomain
from polymap.layout.interfaces import Layout


from msd2.geom.connectivity import Edge


def write_connectivity_edges_to_json(edges: list[Edge], path: Path):
    msd_edges = MSDEdgesModel(
        edges=[MSDEdgeModel(a=edge.a, b=edge.b, conn=edge.conn) for edge in edges]
    )
    data = msd_edges.model_dump()
    write_json(data, path, OVERWRITE=True)


def room_data_to_layout(rooms: list[RoomData]):
    doms = map(lambda x: FancyOrthoDomain(x.coords, x.name), rooms)
    return Layout(list(doms))


def write_room_data_to_json_as_layout(rooms: list[RoomData], path: Path):
    layout = room_data_to_layout(rooms)
    data = layout_to_model(layout).model_dump()
    write_json(data, path, OVERWRITE=True)


# def sample_unit_ids_to_files_as_layouts(
#     num_samples: int = NUM_SAMPLES, path: Path = DynamicPaths.workflow_inputs
# ):
#
#     df = access_sample_datasets_areas_only(num_samples).collect()
#     for name, data in df.group_by("unit_id"):
#         d = MSDSchema.validate(data)
#         layout = df_unit_to_layout(d)
#         layout_str = layout_to_model(layout).model_dump()
#
#         n = int(name[0])
#
#         curr_path = path / f"{str(n)}.json"
#         write_json(layout_str, curr_path, OVERWRITE=True)
#         # logger.info(curr_path)
