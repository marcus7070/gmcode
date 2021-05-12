import pathlib
import math
from gmcode.geom import Vector


class Machine:
    def __init__(self, outfile: pathlib.Path, accuracy=1e-4):
        self.outfile = open(outfile, "w")
        self.position = Vector()
        self.accuracy = accuracy

    @property
    def accuracy(self):
        return self._accuracy

    @accuracy.setter
    def accuracy(self, val: float):
        self.places = math.ceil(-math.log10(val))
        self._accuracy = val

    def std_init(self):
        """
        Adds a standard preamble.
        """
        pass

    def g0(self, x: float = 0, y: float = 0, z: float = 0):
        """
        Rapid move. Inputs are absolute coords.

        Args:
          x: x coord
          y: y coord
          z: z coord
        """
        request = {"X": x, "Y": y, "Z": z}
        strings = ["G0"]
        for axis in request:
            movement = abs(getattr(self.position, axis.lower()) - request[axis])
            if movement > self.accuracy:
                # move required
                strings.append(f"{axis}{self.format(request[axis])}")

        if len(strings) > 1:  # ie. don't write an empty move
            self.write(" ".join(strings))

    def format(self, num: float) -> str:
        """
        Formats a number for gcode output.
        """
        return f"{num:.{self.places}f}"

    def write(self, line: str):
        self.outfile.write(line)

    def std_close(self):
        """
        Adds a standard post-amble.
        """
        self.write("M2")

    def close(self):
        self.outfile.close()
        self.outfile = None
