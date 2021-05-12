import attr
import math


@attr.s(auto_detect=True, frozen=True, slots=True)
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
