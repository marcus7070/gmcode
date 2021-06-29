import pathlib
import math
from typing import Optional, Dict, List, cast
from gmcode.geom import Vector, Line, ArcXY, PathElement


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
        self._unitialised: Dict[str, bool] = {"X": True, "Y": True, "Z": True}

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

    def std_init(self, toolchange: bool = False):
        """
        Adds a standard preamble.

        Args:
          toolchange: Should we do an M600 and M6 T1 to set the tool length measurement?
        """
        self.comment("##### Start preamble #####")
        self.plane("xy")
        self.write("G21 ; mm")
        self.write("G92.1 ; cancel offsets")
        self.write("G40 ; cutter compensation off")
        self.write("G90 ; absolute distance mode")
        self.write("G90.1 ; arc centre absolute distance mode")
        self.write("G94 ; feed rate in units per minute")
        self.path_mode(p=0.05, q=0.05)
        if toolchange:
            self.write("M600 ; reset toolchange")
            self.toolchange(1)
        self.comment("##### End preamble #####")

    def _xyz_to_command(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
    ):
        """
        Used for g0 and g1 to replace the None in optional arguments with
        current positions. Updates self.position too.
        """
        arg_dict = {"X": x, "Y": y, "Z": z}
        out = []
        request = {
            k: v if v is not None else getattr(self.position, k.lower())
            for k, v in arg_dict.items()
        }

        for axis, val in request.items():
            movement = abs(getattr(self.position, axis.lower()) - val)
            if movement > self.accuracy or self._unitialised[axis]:
                out.append(f"{axis}{self.format(val)}")
                self._queue_state(**{axis.lower(): val})
                self._unitialised[axis] = False

        self._queue_apply()
        return out

    def g0(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
    ):
        """
        Rapid move. Inputs are absolute coords.

        Args:
          x: x coord
          y: y coord
          z: z coord
        """
        strings = ["G0"] + self._xyz_to_command(x, y, z)

        if len(strings) > 1:  # ie. don't write an empty move
            self.write(" ".join(strings))

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

        strings = ["G1"] + self._xyz_to_command(x, y, z)

        if len(strings) > 1:  # ie. don't write an empty command
            self.write(" ".join(strings))

    def arc(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
        i: Optional[float] = None,
        j: Optional[float] = None,
        cw: bool = True,
        p: int = 1,
    ):
        """
        Either a G3 or a G4 command.

        Args:
          x: x coord of the end of the arc. If None, then is equal to current x coord. Absolute coords.
          y: y coord of the end of the arc. If None, then is equal to current y coord. Absolute coords.
          z: z coord of the end of the arc. If None, then is equal to current z coord. Absolute coords.
          i: x coord of the arc centre. An error is raised if this is None. Absolute coords.
          j: y coord of the arc centre. An error is raised if this is None. Absolute coords.
          cw: Is the arc clockwise?
          p: number of turns.

          TODO: Handle non-XY planes.
          I always output axis words because it leaving them off can get
          confusing when you are trying to read and debug g-code.
        """

        if i is None or j is None:
            raise MachineError("arc centre must be specified")

        if x is None:
            x = self.position.x

        if y is None:
            y = self.position.y

        if z is None:
            z = self.position.z

        command_elms = [
            "G2" if cw else "G3",
            f"X{self.format(x)}",
            f"Y{self.format(y)}",
            f"Z{self.format(z)}" if abs(z - self.position.z) > self.accuracy else "",
            f"I{self.format(i)}",
            f"J{self.format(j)}",
            f"P{p}" if p != 1 else "",
        ]
        command = " ".join(command_elms)
        self.write(command)
        self.position = Vector(x, y, z)

    def cut(self, paths: List[PathElement]):
        """
        Cuts a series of lines or arcs (subclasses of PathElement).

        Args:
          paths: A list of paths to cut
        """
        for p in paths:
            if self.position != p.start:
                raise MachineError(
                    f"Current position ({self.position}) is not equal to path start position ({p.start})"
                )
            if isinstance(p, Line):
                self.g1(*p.end)
            elif isinstance(p, ArcXY):
                self.arc(p.end.x, p.end.y, p.end.z, i=p.centre.x, j=p.centre.y, cw=p.cw)
            else:
                raise MachineError(
                    f"cut method does not know how to handle type {type(p)}"
                )

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
        if self._plane != plane_command:
            self.write(f"{plane_command} ; plane {plane_name}")
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

    def dwell(self, time: float):
        self.write(f"G4 P{self.format(time)}")

    def pause(self):
        """
        Writes a M0 pause command.
        """
        self.write("M0")

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
