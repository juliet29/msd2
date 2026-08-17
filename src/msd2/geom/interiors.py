from itertools import combinations

from msd2.geom.interfaces import ConnectionData, Edge, RoomData

PASSAGE_DISTANCE = 0.04
DOOR_DISTANCE = 0.05


def extract_interior_edges(rooms: list[RoomData], door_conns: list[ConnectionData]):
    # TODO: hangle passages differently.. may have larger interior doors which should be accounted for..

    def passage_connection(
        a: RoomData, b: RoomData, edges: list[Edge], distance: float = PASSAGE_DISTANCE
    ):
        ap, bp = a.poly, b.poly
        if ap.distance(bp) < distance:
            edges.append(Edge(a.name, b.name, "Passage"))

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
            edges.append(Edge(a.name, b.name, conn=door.conn_type))
        return edges

    edges: list[Edge] = []

    room_combos = combinations(rooms, 2)
    for a, b in room_combos:
        edges = passage_connection(a, b, edges)

        for conn in door_conns:
            edges = door_connection(a, b, conn, edges)

    return edges
