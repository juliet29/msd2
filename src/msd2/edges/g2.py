from itertools import combinations, product
from typing import NamedTuple

from loguru import logger

from msd2.geom.interfaces import ConnectionData, RoomData

PASSAGE_DISTANCE = 0.04
DOOR_DISTANCE = 0.05


class Edge(NamedTuple):
    a: str
    b: str  # TODO: should be direction
    data: dict


class ConnectionGroups(NamedTuple):
    doors: list[ConnectionData]
    windows: list[ConnectionData]


def split_connections(conns: list[ConnectionData]):
    doors = [i for i in conns if i.roomtype == "Door" or i.roomtype == "Entrance Door"]
    windows = [i for i in conns if i.roomtype == "Window"]
    return ConnectionGroups(doors, windows)


def extact_graph(rooms: list[RoomData], conns: list[ConnectionData]):

    def passage_connection(
        a: RoomData, b: RoomData, edges: list[Edge], distance: float = PASSAGE_DISTANCE
    ):
        ap, bp = a.poly, b.poly
        if ap.distance(bp) < distance:
            edges.append(Edge(a.name, b.name, {"conn": "Passage"}))

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
            edges.append(Edge(a.name, b.name, {"conn": door.roomtype}))
        return edges

    def window_connection(
        a: RoomData,
        window: ConnectionData,
        edges: list[Edge],
        distance: float = DOOR_DISTANCE,
    ):
        ap, wp = a.poly, window.poly
        if ap.distance(wp) < distance:
            # TODO: want to know the surface that it is on!
            edges.append(Edge(a.name, window.name, {"conn": window.roomtype}))
        return edges

    room_combos = combinations(rooms, 2)

    edges: list[Edge] = []
    conn_groups = split_connections(conns)
    logger.debug([i.roomtype for i in conns])

    for a, b in room_combos:
        edges = passage_connection(a, b, edges)

        for conn in conn_groups.doors:
            logger.debug(conn.roomtype)
            edges = door_connection(a, b, conn, edges)

    room_window_pairs = product(rooms, conn_groups.windows)

    for room, window in room_window_pairs:
        edges = window_connection(room, window, edges)

    return edges
