from plan2eplus.ezcase.ez import EZ
import networkx as nx
from loguru import logger
from rich.pretty import pretty_repr


def assess_surface_relations(case: EZ):
    surfaces = case.objects.surfaces
    walls = [i for i in surfaces if i.surface_type == "wall"]
    edges = []
    G = nx.DiGraph()
    for wall in walls:

        if wall.boundary_condition == "surface":
            e = (wall.display_name, wall.neighbor_name)
        # elif wall.boundary_condition == "outdoors":
        #     try:
        #         e = (wall.display_name, wall.direction.name)
        #     except ValueError as e:
        #         logger.error(f"Invalid wall_direction for {wall.surface_name}: {e}")
        #         continue
        else:
            continue

        G.add_edge(*e)
        edges.append(e)
    # logger.info(pretty_repr(sorted([i for i in G.edges])))
    logger.info(pretty_repr(edges))
