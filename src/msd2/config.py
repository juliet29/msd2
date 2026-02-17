from pathlib import Path
from omegaconf import OmegaConf
from plan2eplus.ezcase.ez import AnalysisPeriod
from dataclasses import dataclass
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

# resolve msd conf to inform runs..
# TODO: think about, should this be part of snakemake? or we will that just be for handling folders?


@dataclass
class MSDConfigSchema:
    room_height: int  # meters
    weather_file: Path
    analysis_period: AnalysisPeriod


@dataclass
class MSDConfig:
    path_to_config: Path

    def __post_init__(self):
        schema = OmegaConf.structured(MSDConfigSchema)
        input_config = OmegaConf.load(self.path_to_config)
        config = OmegaConf.merge(schema, input_config)
        self.config: MSDConfigSchema = OmegaConf.to_object(
            config
        )  # pyright: ignore[reportAttributeAccessIssue]
