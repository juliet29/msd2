from pathlib import Path

from polymap.pydantic_models import layout_to_model
from utils4plans.io import write_json

from msd2.config import NUM_SAMPLES
from msd2.paths import DynamicPaths
from msd2.readin.access import access_sample_datasets_areas_only
from msd2.readin.interfaces import MSDSchema
from msd2.geom.create import df_unit_to_layout


def sample_unit_ids_to_files_as_layouts(
    num_samples: int = NUM_SAMPLES, path: Path = DynamicPaths.workflow_inputs
):

    df = access_sample_datasets_areas_only(num_samples).collect()
    for name, data in df.group_by("unit_id"):
        d = MSDSchema.validate(data)
        layout = df_unit_to_layout(d)
        layout_str = layout_to_model(layout).model_dump()

        n = int(name[0])

        curr_path = path / f"{str(n)}.json"
        write_json(layout_str, curr_path, OVERWRITE=True)
        # logger.info(curr_path)
