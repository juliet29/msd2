from utils4plans.paths import StaticPaths
import pyprojroot


BASE_PATH = pyprojroot.find_root(pyprojroot.has_dir(".git"))
static_paths = StaticPaths("", BASE_PATH)


class DynamicPaths:
    msd_unit_ids = static_paths.temp / "msd_unit_ids.json"
