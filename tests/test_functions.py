import pytest
from gmcode import functions, Vector
import math
import pygcode


def line(filename, idx):
    with open(filename) as f0:
        lines = f0.readlines()

    return lines[idx]


def count_lines(filename, string):
    with open(filename) as f0:
        lines = f0.readlines()

    return sum([string in l0 for l0 in lines])


@pytest.mark.parametrize("cw,command", [(True, "G2 "), (False, "G3 ")])
def test_sprial_in(tmp_gcodefile, tmp_machine, cw, command):
    centre = Vector(1, 2, -3)
    radius_start = 4
    radius_end = radius_start / 2
    start = centre + radius_start * Vector(0, -1, 0)
    doc = 0.22
    tmp_machine.feedrate(100)
    tmp_machine.g0(start.x, start.y)
    tmp_machine.g1(z=start.z)
    functions.spiral(tmp_machine, centre=centre, radius_end=radius_end, doc=doc, cw=cw)

    assert abs(tmp_machine.position - centre) == pytest.approx(radius_end)
    tmp_machine.close()

    # last line should be G2 X1.0something Y4.0 or Y0.0
    assert tmp_gcodefile.line_contains_gcode(-1, command)
    assert tmp_gcodefile.line_contains_word(-1, "X1.0")
    y_correct = tmp_gcodefile.line_contains_word(-1, "Y4.0")
    y_correct += tmp_gcodefile.line_contains_word(-1, "Y0.0")
    assert y_correct
    # check we have the correct number of loops
    assert tmp_gcodefile.count_gcode(command) / 2 >= math.floor(
        (radius_start - radius_end) / doc
    )


@pytest.mark.parametrize("cw,command", [(True, "G2 "), (False, "G3 ")])
def test_sprial_out(tmp_gcodefile, tmp_machine, cw, command):
    centre = Vector(1, 2, -3)
    radius_start = 3
    radius_end = radius_start * 2
    start = centre + radius_start * Vector(-1, 0, 0)
    tmp_machine.feedrate(100)
    tmp_machine.g0(start.x, start.y)
    tmp_machine.g1(z=start.z)
    functions.spiral(tmp_machine, centre=centre, radius_end=radius_end, doc=0.25, cw=cw)

    assert abs(tmp_machine.position - centre) == pytest.approx(radius_end)
    tmp_machine.close()

    # last line should be G2 X-5.0something or X7.0,  Y2.0
    assert tmp_gcodefile.line_contains_gcode(-1, command)
    assert tmp_gcodefile.line_contains_word(-1, "Y2.0")
    x_correct = tmp_gcodefile.line_contains_word(-1, "X-5.0")
    x_correct += tmp_gcodefile.line_contains_word(-1, "X7.0")
    assert x_correct

    # should be at least radius increase / doc
    assert tmp_gcodefile.count_gcode(command) >= 4 * 3


@pytest.mark.parametrize("start_x", [1, 5])
@pytest.mark.parametrize("start_y", [1, 6])
@pytest.mark.parametrize("centre_x", [0, 2])
@pytest.mark.parametrize("centre_y", [0, 3])
@pytest.mark.parametrize("radius_end", [2, 10])
@pytest.mark.parametrize("woc", [0.1, 1])
def test_spiral_overshoot(
    tmp_file,
    tmp_gcodefile,
    tmp_machine,
    start_x,
    start_y,
    centre_x,
    centre_y,
    radius_end,
    woc,
):
    tmp_machine.g0(start_x, start_y, z=0)
    centre = Vector(centre_x, centre_y, tmp_machine.position.z)
    functions.spiral(tmp_machine, centre=centre, radius_end=radius_end, doc=woc)
    tmp_machine.close()
    # how to catch an overshoot?
    radius_start = abs(Vector(start_x, start_y) - centre)

    pos = {"X": 0, "Y": 0}
    for line in tmp_gcodefile.lines:

        # update position
        for k in pos:
            if line.gcodes and k in line.gcodes[0].params:
                pos[k] = line.gcodes[0].params[k].value

        # if G2, check radius
        if line.gcodes and line.gcodes[0].word == pygcode.Word("G2"):
            end = Vector(pos["X"], pos["Y"])
            radius_current = abs(end - centre)
            assert (
                min(radius_start, radius_end) - woc
                < radius_current
                < max(radius_start, radius_end) + woc
            )


@pytest.mark.parametrize("cw,command", [(True, "G2 "), (False, "G3 ")])
def test_helical_entry(tmp_gcodefile, tmp_machine, cw, command):
    centre = Vector(-5, -6, -7)
    radius = 4
    radial_dir = Vector(4, 5, 0).unit_vector()
    start = centre + radius * radial_dir
    tmp_machine.g0(start.x, start.y)
    doc = 0.1
    functions.helical_entry(
        tmp_machine,
        centre=centre,
        final_height=centre.z,
        doc=doc,
        cw=cw,
    )
    assert tmp_machine.position == Vector(start.x, start.y, centre.z)
    tmp_machine.close()
    assert tmp_gcodefile.line_contains_gcode(-1, command)
    returned_gcode = tmp_gcodefile.lines[-1].gcodes[0]
    assert "P" in returned_gcode.params
    assert returned_gcode.params["P"].value >= math.floor(centre.z / doc)
    assert "Z" in returned_gcode.params
    assert returned_gcode.params["Z"].value == pytest.approx(centre.z)


@pytest.mark.parametrize("centre", [None, Vector(10, 10), Vector(-1, -1)])
def test_rect_in(tmp_gcodefile, tmp_machine, centre):
    centre_vec = centre if centre else Vector()
    start_vec = centre_vec + Vector(20, 10)
    tmp_machine.g0(start_vec.x, start_vec.y)
    tmp_machine.g1(z=-5)
    args = {"m": tmp_machine, "woc": 1}
    if centre:
        args.update(centre=centre)
    functions.rect_in(**args)
    tmp_machine.close()
    # that should have made 10 loops, each with 4 g1 commands + 1 for the inital
    assert tmp_gcodefile.count_gcode("G1") == pytest.approx(10 * 4 + 1, abs=1)
