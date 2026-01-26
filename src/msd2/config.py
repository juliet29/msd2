from replan2eplus.ezcase.ez import AnalysisPeriod
from msd2.paths import DynamicPaths


NUM_SAMPLES = 10
SEED = 12345
PRECISION = 2
ROOM_HEIGHT = 3  # m
WEATHER_FILE = DynamicPaths.weather_pa2024
ANALYSIS_PERIOD = AnalysisPeriod(
    "testing", 6, 10, 6, 11
)  # TODO: this time period is longer than I thought!
