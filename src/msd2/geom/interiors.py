from itertools import combinations

from icecream import ic

from msd2.geom.interfaces import ConnectionData, Edge, RoomData

PASSAGE_DISTANCE = 0.04
DOOR_DISTANCE = 0.05


def extract_interior_edges(rooms: list[RoomData], door_conns: list[ConnectionData]):
    # TODO: hangle passages differently.. may have larger interior doors which should be accounted for..

    def add_passage_connection_edges(
        a: RoomData, b: RoomData, edges: list[Edge], distance: float = PASSAGE_DISTANCE
    ):
        ap, bp = a.poly, b.poly

        if ap.distance(bp) < distance:
            new = Edge(a.name, b.name, "Passage")
            # ic(new)
            edges.append(new)

        return edges

    def door_connection(
        a: RoomData,
        b: RoomData,
        door: ConnectionData,
        edges: list[Edge],
        distance: float = DOOR_DISTANCE,
    ):
        ap, bp, dp = a.poly, b.poly, door.poly
        if ap.distance(dp) < distance and bp.distance(dp) < distance:
            new = Edge(a.name, b.name, conn=door.conn_type)
            edges.append(new)
        return edges

    edges: list[Edge] = []

    room_combos = list(combinations(rooms, 2))
    ic(len(rooms), len(room_combos), len(door_conns))
    for a, b in room_combos:
        # ic(a.name, b.name)
        edges = add_passage_connection_edges(a, b, edges)

        for conn in door_conns:
            edges = door_connection(a, b, conn, edges)

    # ic(edges)
    # breakpoint()
    return edges
