from pathlib import Path
import polars as pl
from replan2eplus.ezcase.ez import EZ
from loguru import logger
from rich.pretty import pretty_repr
from replan2eplus.visuals.domains import compute_multidomain
import patito as pt


def calc_zones_and_area(case: EZ, in_afn: bool = False):
    if in_afn:
        zones = case.objects.airflow_network.zones
    else:
        zones = case.objects.zones
    areas = [i.domain.area for i in zones]  # TODO => calc area for ortho domain..
    return len(zones), sum(areas)


def calc_afn_surfaces(case: EZ):
    afn_surfaces = case.objects.airflow_network.afn_surfaces
    unique_surfaces = set([i.display_name for i in afn_surfaces])
    logger.debug(pretty_repr([i.display_name for i in afn_surfaces]))
    logger.debug(f"{len(afn_surfaces)}/ {len(unique_surfaces)}")
    return len(unique_surfaces)


def calc_bounding_aspect_ratio(case: EZ):
    zones = case.objects.zones
    multi_domain = compute_multidomain([i.domain for i in zones])
    # horz over vert
    aspect_ratio = multi_domain.horz_range.size / multi_domain.vert_range.size
    return aspect_ratio


class PlanMetrics(pt.Model):
    num_zones: int
    num_zones_afn: int
    area: float
    area_afn: float
    ratio_area_afn: float
    num_afn_surfaces: float
    bounding_aspect_ratio: float


def calc_plan_metrics(case: EZ):
    num_zones, area = calc_zones_and_area(case)
    num_zones_afn, area_afn = calc_zones_and_area(case, in_afn=True)
    ratio_area_afn = area_afn / area
    num_afn_surfaces = calc_afn_surfaces(case)
    bounding_aspect_ratio = calc_bounding_aspect_ratio(case)

    data = {
        "num_zones": num_zones,
        "num_zones_afn": num_zones_afn,
        "area": area,
        "area_afn": area_afn,
        "ratio_area_afn": ratio_area_afn,
        "num_afn_surfaces": num_afn_surfaces,
        "bounding_aspect_raio": bounding_aspect_ratio,
    }
    # logger.debug(data)

    return pl.DataFrame(data)


def calc_plan_metrics_from_path(path: Path):
    case = EZ(path, read_existing=True)
    return calc_plan_metrics(case)
