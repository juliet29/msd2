from polymap.process.process import process_layout

from msd2.geom.utils import df_unit_to_layout
from msd2.readin.access import access_one_sample_dataset


def try_process_layout():
    id, df_id = access_one_sample_dataset(sample_id=49943)

    layout = df_unit_to_layout(df_id.collect())
    res = process_layout(id, layout)  # pyright: ignore[reportArgumentType]
    return res


if __name__ == "__main__":
    try_process_layout()
