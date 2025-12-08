from dataframely import DataFrame
from polymap.geometry.ortho import FancyOrthoDomain
from polymap.layout.interfaces import Layout
from msd2.readin.interfaces import MSDSchema
from msd2.geom.interfaces import RoomData
import shapely as sp


def msd_geom_to_shapely(geom: str) -> sp.Polygon:
    spgeo = sp.from_wkt(geom)
    assert isinstance(spgeo, sp.Polygon)
    return spgeo


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

    pass


def df_unit_to_layout(df: DataFrame[MSDSchema]):
    room_data = df_unit_to_room_data(df)
    doms = map(lambda x: FancyOrthoDomain(x.coords, x.name), room_data)
    return Layout(list(doms))
