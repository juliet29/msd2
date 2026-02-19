from utils4plans.paths import StaticPaths
import pyprojroot


BASE_PATH = pyprojroot.find_root(pyprojroot.has_dir(".git"))
static_paths = StaticPaths("", BASE_PATH)

MSD_CONFIG_PATH = BASE_PATH / "msdconfig/test.yaml"
