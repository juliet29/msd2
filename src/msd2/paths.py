from pathlib import Path

import pyprojroot

BASE_PATH = pyprojroot.find_root(pyprojroot.has_dir(".git"))

MSD_CONFIG_PATH = BASE_PATH / "msdconfig/test.yaml"

TEMP_PATH = "/scratch/users/jnwagwu/msd2"


class TempPaths:
    base = Path(TEMP_PATH)
    test_msd = base / "test_msd"


class ProjectPaths:
    data = TempPaths
