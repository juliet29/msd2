import pyprojroot
from utils4plans.paths import StaticPaths

BASE_PATH = pyprojroot.find_root(pyprojroot.has_dir(".git"))
static_paths = StaticPaths("", BASE_PATH)

MSD_CONFIG_PATH = BASE_PATH / "msdconfig/test.yaml"

TEMP_PATH = "/scratch/users/jnwagwu/msd2"


class TempPaths:
    base = TEMP_PATH
    test_msd = base / "test_msd"


class ProjectPaths:
    data = TempPaths
