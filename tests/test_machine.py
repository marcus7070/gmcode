import pytest
from gmcode import MachineError, Vector, Machine
from gmcode.geom import Line, ArcXY
import math


def line(filename, idx):
    with open(filename) as f0:
        lines = f0.readlines()

    return lines[idx]


def in_file(filename, string):
    with open(filename) as f0:
        if string in f0.read():
            return True

    return False


def num_lines(filename, search_string: str) -> int:
    """
    Return the number of lines that search_string appears on.
    """
    with open(filename) as f0:
        entries = [search_string in l for l in f0.readlines()]
    return sum(entries)


def test_file_create(tmp_file, tmp_machine):
    tmp_machine.close()
    assert tmp_file.exists()


def test_write(tmp_file, tmp_machine):
    s0 = "The write method takes any string or numbers [0-9] and sticks them in the file."
    tmp_machine.write(s0)
    tmp_machine.close()
    l0 = line(tmp_file, -1)
    assert s0 in l0


def test_std_close(tmp_file, tmp_machine):
    tmp_machine.std_close()
    tmp_machine.close()
    l0 = line(tmp_file, -1)
    assert "M2" in l0


def test_format(tmp_machine):

    s0 = tmp_machine.format(1)
    assert len(s0.split(".")[-1]) == tmp_machine.places

    s1 = tmp_machine.format(1.0 + tmp_machine.accuracy)
    assert s1 != s0

    assert tmp_machine.accuracy != 1e-8
    tmp_machine.accuracy = 1e-8
    assert tmp_machine.places >= 8
    s2 = tmp_machine.format(1)
    assert len(s2.split(".")[-1]) == tmp_machine.places


@pytest.mark.parametrize("accuracy", [1, 1e-1, 1e-6, 1e-8])
def test_accuracy(tmp_machine, accuracy):
    tmp_machine.accuracy = accuracy
    assert tmp_machine.format(math.pi) != tmp_machine.format(math.pi + accuracy)
    assert tmp_machine.format(math.pi) != tmp_machine.format(math.pi - accuracy)
    # don't test for changes < accuracy causing no change in output
    # low accuracy is just about reducing file size, so it doesn't matter if
    # small changes do change output


def test_g0(tmp_file, tmp_machine):
    tmp_machine.g0(100, 200, 3)
    tmp_machine.close()
    l0 = line(tmp_file, -1)
    assert "G0" in l0
    assert "X100" in l0
    assert "Y200" in l0
    assert "Z3" in l0


def test_set_feedrate(tmp_file, tmp_machine):
    tmp_machine.feedrate(f=234)
    tmp_machine.close()
    assert "F234" in line(tmp_file, -1)


@pytest.mark.parametrize("g_command", ["g0", "g1"])
@pytest.mark.parametrize("o", [0, 0.0])
def test_g_no_move(tmp_file, tmp_machine, o, g_command):
    if g_command == "g1":
        tmp_machine.feedrate(100)
    bound_method = getattr(tmp_machine, g_command)
    # first move will always produce output and initialise CNC position
    bound_method(o, o, o)
    tmp_machine.write("something")
    bound_method(o, o, o)
    tmp_machine.close()
    l0 = line(tmp_file, -1)
    assert g_command.lower() not in l0.lower()


def test_g0_no_move_accuracy(tmp_file, tmp_machine):
    acc = tmp_machine.accuracy * 0.9
    tmp_machine.g0(0, 0, 0)
    tmp_machine.write("something")
    tmp_machine.g0(z=acc)
    tmp_machine.close()
    l0 = line(tmp_file, -1)
    assert "G0" not in l0


def test_command_queue(tmp_machine):
    tmp_machine._queue_state(x=1)
    assert "x" in tmp_machine._queue
    assert tmp_machine._queue["x"] == 1


def test_lineends(tmp_file, tmp_machine):
    for idx in range(3):
        tmp_machine.write(str(idx))

    tmp_machine.close()

    assert "2" in line(tmp_file, -1)
    assert "1" not in line(tmp_file, -1)
    assert "1" in line(tmp_file, -2)


def test_comment(tmp_file, tmp_machine):
    s = "A simple comment"
    tmp_machine.comment(s)
    tmp_machine.close()
    assert "(" + s + ")" in line(tmp_file, -1)


def test_comment_exceptions(tmp_file, tmp_machine):
    with pytest.raises(MachineError):
        tmp_machine.comment("(brackets are not allowed)")

    with pytest.raises(MachineError):
        tmp_machine.comment("no mid string \n newlines")

    s = "Newlines on the end of strings are allowed"
    tmp_machine.comment(s + "\n")
    tmp_machine.close()
    assert s in line(tmp_file, -1)


@pytest.mark.parametrize(
    "s,c",
    [
        ("XY", "G17"),
        ("ZX", "G18"),
        ("YZ", "G19"),
        ("YX", "G17"),
        ("XZ", "G18"),
        ("ZY", "G19"),
        ("G17", "G17"),
        ("G18", "G18"),
        ("G19", "G19"),
        ("g17", "G17"),
        ("g18", "G18"),
        ("g19", "G19"),
    ],
)
def test_plane(tmp_file, tmp_machine, s, c):
    tmp_machine.plane(s)
    tmp_machine.close()
    # plane commands are not repeated, so need to scan the whole file not just the last line
    assert num_lines(tmp_file, c) == 1


@pytest.mark.parametrize(
    "s,c",
    [
        ("XY", "G17"),
        ("ZX", "G18"),
        ("G17", "G17"),
        ("g19", "G19"),
    ],
)
def test_plane_repeat(tmp_file, tmp_machine, c, s):
    s0 = "start of plane commands"
    tmp_machine.comment(s0)
    tmp_machine.plane(s)
    tmp_machine.plane(s)
    tmp_machine.close()
    assert num_lines(tmp_file, c) == 1


def test_plane_fail(tmp_machine):
    with pytest.raises(MachineError):
        tmp_machine.plane("AB")

    with pytest.raises(MachineError):
        tmp_machine.plane("UV")


def test_toolchange(tmp_file, tmp_machine):
    # should start on tool #1
    tmp_machine.toolchange(1)
    tmp_machine.toolchange(2)
    tmp_machine.toolchange(2)
    tmp_machine.close()
    assert num_lines(tmp_file, "T1") == 1
    assert num_lines(tmp_file, "T2") == 1


@pytest.mark.parametrize(
    "kwargs,in_result,not_in_result",
    [
        ({"exact_path": True}, ["G61"], ["G61.1", "G64", "G61 P"]),
        ({"exact_stop": True}, ["G61.1"], ["G64", "G61.1 P"]),
        ({"p": 0.5}, ["G64 P0.5"], ["G61", "G64 P0.5 Q"]),
        ({"p": 0.2, "q": 0.3}, ["G64 P0.2", "Q0.3"], ["G61"]),
    ],
)
def test_path_mode(tmp_file, tmp_machine, kwargs, in_result, not_in_result):
    tmp_machine.path_mode(**kwargs)
    tmp_machine.close()
    # find the last G61 or G64 line, which might be in the preamble
    with open(tmp_file) as f0:
        lines = f0.readlines()

    l0 = next(l for l in lines[::-1] if ("G61" in l) or ("G64" in l))
    for s in in_result:
        assert s in l0

    for s in not_in_result:
        assert s not in l0


def test_dwell(tmp_file, tmp_machine):
    tmp_machine.dwell(3.145)
    tmp_machine.dwell(3.145)
    tmp_machine.close()
    assert "G4 P3.145" in line(tmp_file, -1)
    # there was two dwell commands
    assert "G4 P3.145" in line(tmp_file, -2)


def test_std_init(tmp_file, tmp_machine):
    tmp_machine.close()
    codes = [
        "G17",  # set the plane
        "G21",  # units
        "G92.1",  # offsets
        "G40",  # cancel cutter comp
        "G90",  # absolute dist mode
        "G90.1",  # arc centre mode
        "G94",  # feed rate mode
        "G64",  # path blending mode
    ]
    for code in codes:
        assert num_lines(tmp_file, code) >= 1


def test_position_g0(tmp_machine):
    # see if Machine.position follows a bunch of g0 moves
    tmp_machine.g0(100)
    assert tmp_machine.position == Vector(100, 0, 0)
    tmp_machine.g0(12, 13)
    assert tmp_machine.position == Vector(12, 13, 0)
    tmp_machine.g0(14, 15, -5)
    assert tmp_machine.position == Vector(14, 15, -5)
    tmp_machine.g0(z=1)
    assert tmp_machine.position == Vector(14, 15, 1)
    tmp_machine.g0(y=10)
    assert tmp_machine.position == Vector(14, 10, 1)


def test_position_g1(tmp_machine):
    # see if Machine.position follows a bunch of g1 moves
    tmp_machine.g0(10, 10)
    tmp_machine.g1(z=-5)
    assert tmp_machine.position == Vector(10, 10, -5)
    tmp_machine.g1(x=11)
    assert tmp_machine.position == Vector(11, 10, -5)
    tmp_machine.g1(y=12)
    assert tmp_machine.position == Vector(11, 12, -5)
    tmp_machine.g1(11, 12, 13)
    assert tmp_machine.position == Vector(11, 12, 13)


@pytest.mark.parametrize("command,cw", [("G2", True), ("G3", False)])
def test_arc(tmp_file, tmp_machine, command, cw):
    tmp_machine.g0(100, 200)
    tmp_machine.g0(z=-1)
    current_pos = tmp_machine.position
    centre = current_pos + Vector(0, 5, 0)
    end = current_pos + Vector(0, 10, 0)
    tmp_machine.arc(y=end.y, i=centre.x, j=centre.y, cw=cw)
    tmp_machine.close()
    assert command in line(tmp_file, -1)
    assert "X100" in line(tmp_file, -1)
    assert "Y210" in line(tmp_file, -1)
    assert "I100" in line(tmp_file, -1)
    assert "J205" in line(tmp_file, -1)
    assert "Z" not in line(tmp_file, -1)
    assert "P" not in line(tmp_file, -1)


@pytest.mark.parametrize("cw", [True, False])
def test_position_arc(tmp_machine, cw):
    # see if Machine.position follows a bunch of arc moves
    tmp_machine.g0(11, 12)
    tmp_machine.g1(-1)
    start = tmp_machine.position
    radius = 3
    centre = start + Vector(1, 1, 0).unit_vector() * radius
    end = centre + Vector(-1, -1, 0).unit_vector() * radius
    tmp_machine.arc(end.x, end.y, i=centre.x, j=centre.y, cw=cw)
    assert tmp_machine.position == end
    start = tmp_machine.position
    radius = 10
    centre = start + Vector(1, 0, 0).unit_vector() * radius
    end = centre + Vector(1, 1, 0).unit_vector() * radius
    tmp_machine.arc(end.x, end.y, i=centre.x, j=centre.y, cw=cw)
    assert tmp_machine.position == end


@pytest.mark.parametrize("command,cw", [("G2", True), ("G3", False)])
def test_arc_full_circle(tmp_file, tmp_machine, command, cw):
    tmp_machine.g0(10, 11, 12)
    tmp_machine.arc(i=15, j=11, p=1, cw=cw)
    assert tmp_machine.position == Vector(10, 11, 12)
    tmp_machine.close()
    assert command in line(tmp_file, -1)


def test_cut_lines(tmp_file, tmp_machine):

    point0 = Vector(1, 1, 0)
    point1 = Vector(2, 2, 0)
    point2 = Vector(3, 1, 0)
    lines = [
        Line(point0, point1),
        Line(point1, point2),
        Line(point2, point0),
    ]
    tmp_machine.g0(point0.x, point0.y)
    tmp_machine.feedrate(100)
    tmp_machine.g1(z=point0.z)
    tmp_machine.cut([lines[0]])
    assert tmp_machine.position == lines[0].end

    tmp_machine.g0(point0.x, point0.y)
    tmp_machine.cut(lines)
    assert tmp_machine.position == point0
    tmp_machine.close()
    assert f"G1 X{tmp_machine.format(point0.x)}" in line(tmp_file, -1)
    assert (
        f"G1 X{tmp_machine.format(point2.x)} Y{tmp_machine.format(point2.y)}"
        in line(tmp_file, -2)
    )
    assert (
        f"G1 X{tmp_machine.format(point1.x)} Y{tmp_machine.format(point1.y)}"
        in line(tmp_file, -3)
    )


def test_cut_arcs(tmp_file, tmp_machine):

    point0 = Vector(0, 0, 0)
    centre0 = Vector(1, 0, 0)
    point1 = Vector(2, 0, 0)
    centre1 = point1 + Vector(1, 0, 0)
    point2 = centre1 + Vector(1, 0, 0)
    arcs = [
        ArcXY(start=point0, end=point1, centre=centre0),
        ArcXY(start=point1, end=point2, centre=centre1, cw=False),
    ]
    tmp_machine.g0(*point0)
    tmp_machine.cut(arcs)
    assert tmp_machine.position == point2
    tmp_machine.close()

    assert f"G3 X{tmp_machine.format(point2.x)}" in line(tmp_file, -1)
    assert f"G2 X{tmp_machine.format(point1.x)}" in line(tmp_file, -2)


@pytest.mark.parametrize("command", ["g0", "g1"])
@pytest.mark.parametrize("px", [None, 0, 1])
@pytest.mark.parametrize("py", [None, 0, 2])
@pytest.mark.parametrize("pz", [None, 0, 3])
def test_initial_position(tmp_file, tmp_machine, command, px, py, pz):
    """
    Machine.g0 and .g1 do not print out axis words unless needed. Machine
    initialises position as (0, 0, 0), but it's pretty common for the CNC
    machine to start the program at a random point. So if the machine starts at
    (201.5654, 172.345435, 42.009234), and we do Machine.g0(0, 0, -1), it will
    output G0 Z-1 and we will be nowhere near what we expect.
    """
    inputs = {"x": px, "y": py, "z": pz}
    pos_dict = {k: v for k, v in inputs.items() if v is not None}
    if not pos_dict:
        return
    point = Vector(**pos_dict)
    bound_method = getattr(tmp_machine, command)
    bound_method(x=point.x, y=point.y, z=point.z)
    tmp_machine.close()
    l0 = line(tmp_file, -1)
    # since machine was unitialised, every axis should be in last line
    for k, v in zip(["X", "Y", "Z"], point):
        assert f"{k.upper()}{tmp_machine.format(v)}" in l0


@pytest.mark.parametrize("px", [None, 0, 1])
@pytest.mark.parametrize("py", [None, 0, 2])
def test_initial_position_arc(tmp_file, tmp_machine, px, py):
    end = Vector(
        x=px if px is not None else tmp_machine.position.x,
        y=py if py is not None else tmp_machine.position.y,
        z=0,
    )
    centre = tmp_machine.position + (end - tmp_machine.position) / 2
    tmp_machine.arc(x=end.x, y=end.y, i=centre.x, j=centre.y)
    tmp_machine.close()
    assert (
        f"X{tmp_machine.format(tmp_machine.position.x)} Y{tmp_machine.format(tmp_machine.position.y)}"
        in line(tmp_file, -1)
    )


@pytest.mark.parametrize("toolchange", [False, True])
def test_std_init_toolchange(tmp_file, toolchange):
    g = Machine(tmp_file)
    g.std_init(toolchange=toolchange)
    g.close()
    assert (in_file(tmp_file, "M600")) == toolchange
