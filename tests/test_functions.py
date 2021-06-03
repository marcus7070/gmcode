import pytest
from gmcode import functions, Vector
from gmcode.geom import ArcXY
import re


def line(filename, idx):
    with open(filename) as f0:
        lines = f0.readlines()

    return lines[idx]


def count_lines(filename, string):
    with open(filename) as f0:
        lines = f0.readlines()

    return sum([string in l0 for l0 in lines])


@pytest.mark.parametrize("cw,command", [(True, "G2"), (False, "G3")])
def test_sprial_in(tmp_file, tmp_machine, cw, command):
    centre = Vector(1, 2, -3)
    radius_start = 4
    radius_end = radius_start / 2
    start = centre + radius_start * Vector(0, -1, 0)
    tmp_machine.feedrate(100)
    tmp_machine.g0(start.x, start.y)
    tmp_machine.g1(z=start.z)
    functions.spiral(tmp_machine, centre=centre, radius_end=radius_end, doc=0.22, cw=cw)

    assert abs(tmp_machine.position - centre) == pytest.approx(radius_end)
    tmp_machine.close()

    # last line should be G2 X1.0something Y4.0 or Y0.0
    s0 = line(tmp_file, -1)
    assert command in s0
    assert "X1.0" in s0
    assert "Y4.0" in s0 or "Y0.0" in s0


@pytest.mark.parametrize("cw,command", [(True, "G2"), (False, "G3")])
def test_sprial_out(tmp_file, tmp_machine, cw, command):
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
    s0 = line(tmp_file, -1)
    assert command in s0
    assert "Y2.0" in s0
    assert "X-5.0" in s0 or "X7.0" in s0

    # should be at least radius increase / doc
    assert count_lines(tmp_file, command) >= 4 * 3


@pytest.mark.parametrize("start_x", [1, 5])
@pytest.mark.parametrize("start_y", [1, 6])
@pytest.mark.parametrize("centre_x", [0, 2])
@pytest.mark.parametrize("centre_y", [0, 3])
@pytest.mark.parametrize("radius_end", [2, 10])
@pytest.mark.parametrize("woc", [0.1, 1])
def test_spiral_overshoot(
    tmp_file, tmp_machine, start_x, start_y, centre_x, centre_y, radius_end, woc
):
    tmp_machine.g0(start_x, start_y, z=0)
    centre = Vector(centre_x, centre_y, tmp_machine.position.z)
    functions.spiral(tmp_machine, centre=centre, radius_end=radius_end, doc=woc)
    tmp_machine.close()
    # how to catch an overshoot?
    radius_start = abs(Vector(start_x, start_y) - centre)

    x_pos = 0
    y_pos = 0
    for line in open(tmp_file):
        x_candidates = re.findall(r"X(\d+\.\d+)", line)
        assert len(x_candidates) <= 1
        x_pos = float(x_candidates[0]) if x_candidates else x_pos
        y_candidates = re.findall(r"Y(\d+\.\d+)", line)
        assert len(y_candidates) <= 1
        y_pos = float(y_candidates[0]) if y_candidates else y_pos
        if line.startswith("G2 "):
            end = Vector(x_pos, y_pos)
            radius_current = abs(end - centre)
            assert (
                min(radius_start, radius_end) - woc
                < radius_current
                < max(radius_start, radius_end) + woc
            )


@pytest.mark.parametrize("cw,command", [(True, "G2"), (False, "G3")])
def test_helical_entry(tmp_file, tmp_machine, cw, command):
    centre = Vector(-5, -6, -7)
    radius = 4
    radial_dir = Vector(4, 5, 0).unit_vector()
    start = centre + radius * radial_dir
    tmp_machine.g0(start.x, start.y)
    functions.helical_entry(
        tmp_machine,
        centre=centre,
        final_height=centre.z,
        doc=0.1,
        cw=cw,
    )
    assert tmp_machine.position == Vector(start.x, start.y, centre.z)
    tmp_machine.close()
    l0 = line(tmp_file, -1)
    assert command in l0
    assert "P" in l0
    assert f"Z{centre.z:.1f}" in l0
