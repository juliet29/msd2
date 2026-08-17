from cyclopts import App
from icecream import ic
from polyfix.geometry.vectors import CardinalDirections

from msd2.geom.angle import RadianAngle, VectorPair

ag = App("ag")

cd = CardinalDirections


@ag.command
def fd():
    v1, v2 = cd.WEST.aligned_vector, cd.SOUTH.aligned_vector
    vp = VectorPair.from_geom_vectors(v1, v2)
    ic(vp.dot_prod)
    ic(RadianAngle(vp.clamped_angle))
    ic(RadianAngle(vp.directed_angle))
