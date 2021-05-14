import attr
import math
from typing import Literal


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

    def unit_vector(self) -> "Vector":
        return self.__truediv__(abs(self))


@attr.s(auto_detect=True, frozen=True, slots=True)  # type: ignore[call-overload]
class Path:
    start: Vector = attr.ib(Vector())
    end: Vector = attr.ib(Vector())

    def offset(self, val_xy: float, val_z: float = 0.0) -> "Path":
        """
        """
        raise NotImplementedError()

    def tangent(self, val: Literal[0, 1]) -> Vector:
        raise NotImplementedError()


@attr.s(auto_detect=True, frozen=True, slots=True)  # type: ignore[call-overload]
class Line(Path):

    def tangent(self, val: Literal[0, 1] = 0) -> Vector:
        return (self.end - self.start).unit_vector()

    def normal(self, val: Literal[0, 1] = 0) -> Vector:
        # already a unit vector, no need to normalise twice
        return self.tangent().cross(Vector(0, 0, 1))

    def offset_xy(self, val) -> "Line":
        offset_vec = val * self.normal()
        return self.__class__(self.start + offset_vec, self.end + offset_vec)

    def extend(self, pre: float = 0.0, post: float = 0.0) -> "Line":
        pass


@attr.s(auto_detect=True, frozen=True, slots=True)  # type: ignore[call-overload]
class ArcXY(Path):
    radius: float = attr.ib(0.0)

    def tangent(self, val: Literal[0, 1]) -> Vector:

