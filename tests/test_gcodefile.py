from .utils import GcodeFile
import pytest


# Multiple gcodes per line is not tested since gmcode doesn't produce these
TEXT = """(##### Start preamble #####)
G17 ; plane XY
G21 ; mm
G92.1 ; cancel offsets
G40 ; cutter compensation off
G90 ; absolute distance mode
G90.1 ; arc centre absolute distance mode
G94 ; feed rate in units per minute
G64 P0.0500 Q0.0500
(##### End preamble #####)
G1 X1.0417 Y0.0000 Z0.0000
G2 X1.0417 Y0.0000  I0.0000 J0.0000 
G2 X-2.0729 Y0.0000  I-0.5156 J0.0000 
G2 X3.1042 Y0.0000  I0.5156 J0.0000 
G2 X-4.1354 Y0.0000  I-0.5156 J0.0000 
G2 X5.1667 Y0.0000  I0.5156 J0.0000 
G0 Z5.0000
M2
"""

@pytest.fixture(scope="session")
def textfile(tmp_path_factory):
    out = tmp_path_factory.mktemp("gcodefile_test") / "test.ngc";
    with open(out, "w") as f0:
        f0.write(TEXT)

    return out


@pytest.fixture
def gcodefile(textfile):
    return GcodeFile(textfile)


@pytest.mark.parametrize("gcode", ["G17", "G21", "G92.1", "G40", "G90", "G90.1", "G94", "G64", "G1", "G2", "G0", "M2"])
def test_gcode_in(gcodefile, gcode):
    assert gcodefile.contains_gcode(gcode)


def test_gcode_not_in(gcodefile):
    assert not gcodefile.contains_gcode("G99")


@pytest.mark.parametrize("gcode,count", [
    ("G17", 1),
    ("G21", 1),
    ("G90", 1),
    ("G90.1", 1),
    ("G1", 1),
    ("G2", 5),
    ("M2", 1),
    ("G99", 0),
    ("O0", 0),
])
def test_count_gcode(gcodefile, gcode, count):
    assert gcodefile.count_gcode(gcode) == count


@pytest.mark.parametrize("idx,gcode", [(1, "G17"), (2, "G21"), (-1, "M2"), (-2, "G0")])
def test_line_contains_gcode(gcodefile, idx, gcode):
    assert gcodefile.line_contains_gcode(idx, gcode)


@pytest.mark.parametrize("idx,gcode", [(0, "G17"), (1, "G0")])
def test_line_not_contains_gcode(gcodefile, idx, gcode):
    assert not gcodefile.line_contains_gcode(idx, gcode)
