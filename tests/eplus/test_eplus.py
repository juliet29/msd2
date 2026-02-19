from pathlib import Path

from msd2.eplus.main import layout_to_idf
from msd2.examples.examples import SampleUnit
from utils4plans.logconfig import logset
from msd2.geom.io import write_unit
from msd2.paths import MSD_CONFIG_PATH
import tempfile


def test_create_idf_no_polyfix(tmp_path):
    edges_loc = tmp_path / "edges.json"
    layout_loc = tmp_path / "layout.json"
    write_unit(SampleUnit.unit_id, edges_loc, layout_loc)

    case = layout_to_idf(
        edge_path=edges_loc,
        layout_path=layout_loc,
        out_directory=tmp_path,
        msd_config_path=MSD_CONFIG_PATH,
    )
    # logger.debug(case.objects.subsurfaces)
    # NOTE: since this layout has not been polyfixed, we should expect no subsurfaces, but the zones should be there
    assert not case.objects.subsurfaces
    assert case.objects.zones


if __name__ == "__main__":

    logset()
    with tempfile.TemporaryDirectory() as td:
        tmp_dir = Path(td)
        test_create_idf_no_polyfix(tmp_dir)
