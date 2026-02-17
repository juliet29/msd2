from pathlib import Path
from omegaconf import OmegaConf
from plan2eplus.ezcase.ez import AnalysisPeriod
from dataclasses import dataclass

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
