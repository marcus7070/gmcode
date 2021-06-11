import attr
import math
from typing import Literal


TOLERANCE = 1e-6


@attr.s(auto_detect=True, frozen=True, slots=True)  # type: ignore[call-overload]
class Vector:
    x: float = attr.ib(default=0.0)
    y: float = attr.ib(default=0.0)
    z: float = attr.ib(default=0.0)

    def __iter__(self):

        for val in [self.x, self.y, self.z]:
            yield val

    def xy_tuple(self):
        """
        Returns:
          X and Y coords

        Use tuple(a_vector) to convert to a 3-tuple
        """
        return (self.x, self.y)

    def __abs__(self) -> float:

        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def __neg__(self) -> "Vector":

        return self.__mul__(-1)

    def __add__(self, o: "Vector") -> "Vector":

        return self.__class__(self.x + o.x, self.y + o.y, self.z + o.z)

    def __mul__(self, o: float) -> "Vector":

        return self.__class__(o * self.x, o * self.y, o * self.z)

    def __rmul__(self, o: float) -> "Vector":

        return self.__mul__(o)

    def __sub__(self, o: "Vector") -> "Vector":

        return self.__add__(o.__mul__(-1))

    def __truediv__(self, o: float) -> "Vector":

        return self.__mul__(1.0 / o)

    def cross(self, o: "Vector") -> "Vector":

        x = self.y * o.z - self.z * o.y
        y = -self.x * o.z + self.z * o.x
        z = self.x * o.y - self.y * o.x
        return self.__class__(x, y, z)

    def dot(self, o: "Vector") -> float:

        return sum([a * b for a, b in zip(self, o)])

    def unit_vector(self) -> "Vector":

        length = abs(self)
        if length < TOLERANCE:
            raise ValueError("Can not get unit vector of 0 vector")

        return self.__truediv__(length)

    def __eq__(self, o):

        if all([abs(x) < TOLERANCE for x in [self, o]]):
            # two zero vectors
            return True

        if abs(self - o) >= TOLERANCE:
            return False

        direction = self.unit_vector().dot(o.unit_vector())
        if abs(direction - 1) > TOLERANCE:
            return False

        return True


@attr.s(auto_detect=True, frozen=True, slots=True)  # type: ignore[call-overload]
class PathElement:
    start: Vector = attr.ib(Vector())
    end: Vector = attr.ib(Vector())

    def tangent(self, val: Literal[0, 1]) -> Vector:

        raise NotImplementedError()


@attr.s(auto_detect=True, frozen=True, slots=True)  # type: ignore[call-overload]
class Line(PathElement):
    def tangent(self, val: Literal[0, 1] = 0) -> Vector:

        return (self.end - self.start).unit_vector()

    def normal(self, val: Literal[0, 1] = 0) -> Vector:

        return self.tangent().cross(Vector(0, 0, 1)).unit_vector()

    def offset_xy(self, val: float) -> "Line":

        offset_vec = val * self.normal()
        return self.__class__(self.start + offset_vec, self.end + offset_vec)

    def offset_z(self, val) -> "Line":

        offset_vec = Vector(0, 0, val)
        return self.__class__(self.start + offset_vec, self.end + offset_vec)

    def extend(self, pre: float = 0.0, post: float = 0.0) -> "Line":

        pass

    def length(self) -> float:

        return abs(self.end - self.start)

    def centre(self) -> Vector:

        return (self.start + self.end) / 2.0


@attr.s(auto_detect=True, frozen=True, slots=True)  # type: ignore[call-overload]
class ArcXY(PathElement):
    centre: Vector = attr.ib(Vector())
    cw: bool = attr.ib(True)
    # these attributes might seem redundant, but need to handle the case of
    # start == end by providing the centre and direction

    def __attrs_post_init__(self):

        r0 = abs(self.start - self.centre)
        r1 = abs(self.end - self.centre)
        if abs(r0 - r1) > TOLERANCE:
            raise ValueError(
                f"start({self.start}), end({self.end}) and centre({self.centre}) do not form an arc"
            )

    # TODO: class method for making an arc from start, end and radius, for
    # which the following old code might be useful:
    # def centre(self) -> Vector:
    #     # https://math.stackexchange.com/a/87374
    #     l0 = Line(self.start, self.end)
    #     h_unsigned = math.sqrt(self.radius ** 2 - (l0.length() / 2) ** 2)
    #     h = math.copysign(h_unsigned, self.radius)
    #     return l0.centre() + h * l0.normal()

    def tangent(self, val: Literal[0, 1]) -> Vector:

        point = self.end if val else self.start
        if self.cw:
            line = Line(self.centre, point)
        else:
            line = Line(point, self.centre)
        return line.normal()

    def radius(self) -> float:
        """
        Average the two radii for that tiny bit better accuracy.
        """
        return (abs(self.start - self.centre) + abs(self.end - self.centre)) / 2
