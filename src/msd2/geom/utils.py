from pathlib import Path

import shapely as sp
from dataframely import DataFrame
from polymap.geometry.ortho import FancyOrthoDomain
from polymap.json_interfaces import layout_to_model
from polymap.layout.interfaces import Layout
from utils4plans.io import write_json

from msd2.config import NUM_SAMPLES, PRECISION
from msd2.geom.interfaces import RoomData
from msd2.paths import DynamicPaths
from msd2.readin.access import access_sample_datasets
from msd2.readin.interfaces import MSDSchema


def msd_geom_to_shapely(geom: str) -> sp.Polygon:
    spgeo = sp.from_wkt(geom)
    spgeo_precise = sp.from_wkt(sp.to_wkt(spgeo, rounding_precision=PRECISION))
    assert isinstance(spgeo_precise, sp.Polygon)
    return spgeo_precise


def df_unit_to_room_data(df: DataFrame[MSDSchema]):
    # assuming has already been filtered to the unit id..
    # df = MSDSchema.validate(unit_df)
    rooms = [
        RoomData(
            row["entity_type"],
            row["entity_subtype"],
            row["height"],
            ix,
            msd_geom_to_shapely(row["geom"]),
        )
        for ix, row in enumerate(df.iter_rows(named=True))
    ]
    return rooms


def df_unit_to_layout(df: DataFrame[MSDSchema]):
    room_data = df_unit_to_room_data(df)
    doms = map(lambda x: FancyOrthoDomain(x.coords, x.name), room_data)
    return Layout(list(doms))


# def unit_id_to_file(id: int, path: Path):
#     id, df = access_one_sample_dataset(id)
#     layout = df_unit_to_layout(df.collect())
#     layout_str = dump_layout(layout)
#     write_json(layout_str, path)


def sample_unit_ids_to_files(
    num_samples: int = NUM_SAMPLES, path: Path = DynamicPaths.workflow_inputs
):

    df = access_sample_datasets(num_samples).collect()
    for name, data in df.group_by("unit_id"):
        d = MSDSchema.validate(data)
        layout = df_unit_to_layout(d)
        layout_str = layout_to_model(layout).model_dump()

        n = int(name[0])

        curr_path = path / f"{str(n)}.json"
        write_json(layout_str, curr_path, OVERWRITE=True)
        # logger.info(curr_path)
