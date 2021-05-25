import pathlib
import math
from typing import Optional, Dict, cast
from gmcode.geom import Vector


class MachineError(RuntimeError):
    pass


PLANE_COMMANDS = {
    "XY": "G17",
    "ZX": "G18",
    "YZ": "G19",
}


class Machine:
    def __init__(self, outfile: pathlib.Path, accuracy=1e-4):
        self.outfile = open(outfile, "w")
        self.position = Vector()
        self.accuracy = accuracy
        self._feedrate: Optional[float] = None
        self._queue: Dict[str, float] = {}
        self._plane: Optional[str] = None
        self.tool_number: Optional[int] = None
        self._path_mode: Optional[str] = None

    @property
    def accuracy(self):
        return self._accuracy

    @accuracy.setter
    def accuracy(self, val: float):
        self.places = math.ceil(-math.log10(val))
        self._accuracy = val

    def _queue_state(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
    ):
        """
        Queues up a series of changes to the state of the machine.
        Args:
          x: absolute x coord
          y: absolute y coord
          z: absolute z coord
        """
        d = {"x": x, "y": y, "z": z}
        out = {k: v for k, v in d.items() if v is not None}
        self._queue.update(out)

    def _queue_apply(self):
        """
        Applies what was in the queue to self.position and clears it.
        """

        self.position = Vector(
            **{
                k: self._queue[k] if k in self._queue else getattr(self.position, k)
                for k in ["x", "y", "z"]
            }
        )

        self._queue = {}

    def std_init(self):
        """
        Adds a standard preamble.
        """
        self.comment("##### Start preamble #####")
        self.plane("xy")
        self.write("G21 ; mm")
        self.write("G92.1 ; cancel offsets")
        self.write("G40 ; cutter compensation off")
        self.write("M600 ; reset toolchange")
        self.toolchange(1)
        self.path_mode(p=0.05, q=0.05)

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
                self._queue_state(**{axis.lower(): request[axis]})

        if len(strings) > 1:  # ie. don't write an empty move
            self.write(" ".join(strings))

        self._queue_apply()

    def feedrate(self, f: float):
        """
        Set feedrate in units per minute.
        """

        if self._feedrate is None or abs(self._feedrate - f) > self.accuracy:
            self.write(f"F{self.format(f)}")
            self._feedrate = f

    def g1(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
    ):
        """
        Linear move. Axes inputs are absolute coords.

        Args:
          x: x coord
          y: y coord
          z: z coord
        """
        if self.feedrate is None:
            raise MachineError("Feedrate must be defined for a G1 command")

        request = {"X": x, "Y": y, "Z": z}
        strings = ["G1"]
        for axis, val in request.items():
            if val is not None:
                movement = abs(getattr(self.position, axis.lower()) - val)
                if movement > self.accuracy:
                    # move required
                    strings.append(f"{axis}{self.format(val)}")
                    self._queue_state(**{axis.lower(): val})

        if len(strings) > 1:  # ie. don't write an empty command
            self.write(" ".join(strings))

        self._queue_apply()

    def format(self, num: float) -> str:
        """
        Formats a number for gcode output.
        """
        return f"{num:.{self.places}f}"

    def plane(self, plane: str):
        """
        Selects a plane.

        Args:
          plane: Either XY (case insensitive) or G17, etc.
        """
        # Keys are XY, vals are G17
        if plane.upper() in PLANE_COMMANDS:
            plane_name = plane.upper()
        elif plane.upper()[::-1] in PLANE_COMMANDS:
            plane_name = plane.upper()[::-1]
        elif plane.upper() in PLANE_COMMANDS.values():
            plane_name = next(
                k for k, v in PLANE_COMMANDS.items() if v == plane.upper()
            )
        elif plane.upper()[::-1] in PLANE_COMMANDS.values():
            plane_name = next(
                k for k, v in PLANE_COMMANDS.items() if v == plane.upper()[::-1]
            )
        else:
            raise MachineError("{plane} is not a valid plane command")

        plane_command = PLANE_COMMANDS[plane_name]
        print(f"plane name is {plane_command}")
        if self._plane != plane_command:
            self.write(f"{plane_command} ; plane {plane_name}")
            print(f"wrote {plane_command} ; plane {plane_name}")
            self._plane = plane_command

    def write(self, line: str):
        if not line.endswith("\n"):
            line += "\n"
        self.outfile.write(line)

    def comment(self, line: str):

        if line.endswith("\n"):
            line = line[:-1]

        if "\n" in line:
            raise MachineError("No multiline comments")

        for char in ["\n", "(", ")"]:
            try:
                line.index(char)
                raise MachineError(f"{char} not allowed in comment")
            except ValueError:
                pass

        self.write("(" + line + ")")

    def toolchange(self, num: int):
        if self.tool_number != num:
            self.write(f"T{num} M6")
            self.tool_number = num

    def path_mode(
        self,
        exact_path: bool = False,
        exact_stop: bool = False,
        p: float = 0.0,
        q: Optional[float] = None,
    ):
        if exact_stop:
            command = "G61.1"
        elif exact_path:
            command = "G61"
        elif q is not None:
            command = f"G64 P{self.format(p)} Q{self.format(q)}"
        elif p != 0:
            command = f"G64 P{self.format(p)}"
        else:
            command = "G64"

        if self._path_mode != command:
            self.write(command)
            self._path_mode = command

    def std_close(self):
        """
        Adds a standard post-amble.
        """
        self.write("M2")

    def close(self):
        self.outfile.close()
        self.outfile = None
