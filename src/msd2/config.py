from plan2eplus.ezcase.ez import AnalysisPeriod
from msd2.paths import DynamicPaths

# TODO: make this a real config.yaml => part of snakemake config.., can't be changed by calling files..
NUM_SAMPLES = 10
SEED = 12345
PRECISION = 2
ROOM_HEIGHT = 3  # m
WEATHER_FILE = DynamicPaths.weather_pa2024
ANALYSIS_PERIOD = AnalysisPeriod(
    name="testing", st_month=6, end_month=7, st_day=1, end_day=30
)
