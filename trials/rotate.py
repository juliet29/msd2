from polymap.rotate.rotate import rotate_layout
from polymap.visuals.visuals import plot_layout_comparison
from math import degrees

from msd2.geom.create import df_unit_to_layout
from msd2.readin.access import access_one_sample_dataset


def show_rotate():
    # id, layout = get_one_msd_layout()
    id, df_id = access_one_sample_dataset(sample_id=95904)
    layout = df_unit_to_layout(df_id.collect())

    angle, lay2 = rotate_layout(layout)
    plot_layout_comparison(
        [layout, lay2], names=[str(int(id)), f"r={degrees(angle):.2f}º"]
    )


if __name__ == "__main__":
    show_rotate()
