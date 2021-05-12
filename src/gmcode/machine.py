import pathlib
from gmcode.geom import Vector


class Machine:

    def __init__(self, outfile: pathlib.Path):
        self.outfile = open(outfile)
        self.position = Vector()

    def std_init(self):
        """
        Adds a standard preamble.
        """
        pass

    def g0(self, x: float = 0, y: float = 0, z: float = 0):
        """
        Rapid move.

        Args:
          x: x coord
          y: y coord
          z: z coord
        """
        pass
