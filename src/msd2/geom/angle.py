import math
from fractions import Fraction
from typing import NamedTuple

from geom import Vector as GeomVector


class Vector(NamedTuple):
    x: float
    y: float

    @classmethod
    def from_geom_vector(cls, v: GeomVector):
        return cls(v[0], v[1])  # pyright: ignore[reportArgumentType]

    @property
    def rounded(self):
        return (round(self.x), round(self.y))

    @property
    def to_rounded_geom_vector(self):
        return GeomVector((*self.rounded, 0))

    @property
    def magnitude(self):
        x, y = self.x, self.y
        return math.sqrt(x**2 + y**2)


def translate_vector_pair(vs: tuple[GeomVector, GeomVector]):
    return [Vector.from_geom_vector(vs[0]), Vector.from_geom_vector(vs[1])]


class RadianAngle(NamedTuple):
    angle: float

    def __repr__(self) -> str:
        pi_coeff = self.angle / math.pi
        frac = Fraction(pi_coeff).limit_denominator(100)

        if frac.numerator == 0:
            return "0"
        num_str = f"{frac.numerator}*pi"

        return f"{num_str}/{frac.denominator}"

    def apply_to_vector(self, v: Vector):
        x, y = v.x, v.y
        a = self.angle
        sina = math.sin(a)
        cosa = math.cos(a)

        xp = x * cosa - y * sina
        yp = x * sina + y * cosa
        return Vector(xp, yp)


class VectorPair(NamedTuple):
    v1: Vector
    v2: Vector

    @classmethod
    def from_geom_vectors(cls, v1: GeomVector, v2: GeomVector):
        return cls(Vector.from_geom_vector(v1), Vector.from_geom_vector(v2))

    @property
    def dot_prod(self):
        v1, v2 = self.v1, self.v2
        return (v1.x * v2.x) + (v1.y * v2.y)

    @property
    def cross_prod(self):
        v1, v2 = self.v1, self.v2
        return (v1.x * v2.y) - (v1.y * v2.x)

    @property
    def clamped_angle(self):
        scale = self.dot_prod / (self.v1.magnitude * self.v2.magnitude)
        max_scale = min(1.0, scale)  # max alignment is one
        cos_angle = max(-1.0, max_scale)  #

        angle_value = math.acos(cos_angle)  # positive radians between 0 and pi
        return angle_value

    @property
    def directed_angle(self):
        if self.cross_prod < 0:
            return -1 * self.clamped_angle
        else:
            return self.clamped_angle


def angle_between_vectors(vs: tuple[GeomVector, GeomVector]):
    v1, v2 = translate_vector_pair(vs)
