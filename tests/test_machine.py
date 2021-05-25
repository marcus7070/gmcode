import pytest
from gmcode import Machine, MachineError


@pytest.fixture
def tmp_machine(tmp_path_factory):
    fname = tmp_path_factory.mktemp("tmp_file")
    fname = fname / "test.ngc"
    g = Machine(fname)
    g.std_init()
    return g, fname


def line(filename, idx):
    with open(filename) as f0:
        lines = f0.readlines()

    return lines[idx]


def num_lines(filename, search_string: str) -> int:
    """
    Return the number of lines that search_string appears on.
    """
    with open(filename) as f0:
        entries = [search_string in l for l in f0.readlines()]
    return sum(entries)


def test_file_create(tmp_machine):
    g, f = tmp_machine
    g.close()
    assert f.exists()


def test_write(tmp_machine):
    g, f = tmp_machine
    s0 = "The write method takes any string or numbers [0-9] and sticks them in the file."
    g.write(s0)
    g.close()
    l0 = line(f, -1)
    assert s0 in l0


def test_std_close(tmp_machine):
    g, f = tmp_machine
    g.std_close()
    g.close()
    l0 = line(f, -1)
    assert "M2" in l0


def test_format(tmp_machine):

    g, f = tmp_machine
    s0 = g.format(1)
    assert len(s0.split(".")[-1]) == g.places

    s1 = g.format(1.0 + g.accuracy)
    assert s1 != s0

    assert g.accuracy != 1e-8
    g.accuracy = 1e-8
    assert g.places >= 8
    s2 = g.format(1)
    assert len(s2.split(".")[-1]) == g.places


# def test_format2(tmp_machine):


def test_g0(tmp_machine):
    g, f = tmp_machine
    g.g0(100, 200, 3)
    g.close()
    l0 = line(f, -1)
    assert "G0" in l0
    assert "X100" in l0
    assert "Y200" in l0
    assert "Z3" in l0


def test_set_feedrate(tmp_machine):
    g, f = tmp_machine
    g.feedrate(f=234)
    g.close()
    assert "F234" in line(f, -1)


@pytest.mark.parametrize("g_command", ["g0", "g1"])
@pytest.mark.parametrize("o", [0, 0.0])
def test_g_no_move(tmp_machine, o, g_command):
    g, f = tmp_machine
    if g_command == "g1":
        g.feedrate(100)
    g.write("something")  # incase std_init does not produce any output
    bound_method = getattr(g, g_command)
    bound_method(o, o, o)
    g.close()
    l0 = line(f, -1)
    assert g_command.lower() not in l0.lower()


def test_g0_no_move_accuracy(tmp_machine):
    g, f = tmp_machine
    acc = g.accuracy * 0.9
    g.write("something")
    g.g0(z=acc)
    g.close()
    l0 = line(f, -1)
    assert "G0" not in l0


def test_command_queue(tmp_machine):
    g, _ = tmp_machine
    g._queue_state(x=1)
    assert "x" in g._queue
    assert g._queue["x"] == 1


def test_lineends(tmp_machine):
    g, f = tmp_machine
    for idx in range(3):
        g.write(str(idx))

    g.close()

    assert "2" in line(f, -1)
    assert "1" not in line(f, -1)
    assert "1" in line(f, -2)


def test_comment(tmp_machine):
    g, f = tmp_machine
    s = "A simple comment"
    g.comment(s)
    g.close()
    assert "(" + s + ")" in line(f, -1)


def test_comment_exceptions(tmp_machine):
    g, f = tmp_machine
    with pytest.raises(MachineError):
        g.comment("(brackets are not allowed)")

    with pytest.raises(MachineError):
        g.comment("no mid string \n newlines")

    s = "Newlines on the end of strings are allowed"
    g.comment(s + "\n")
    g.close()
    assert s in line(f, -1)


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
def test_plane(tmp_machine, s, c):
    g, f = tmp_machine
    g.plane(s)
    g.close()
    # plane commands are not repeated, so need to scan the whole file not just the last line
    assert num_lines(f, c) == 1


@pytest.mark.parametrize(
    "s,c",
    [
        ("XY", "G17"),
        ("ZX", "G18"),
        ("G17", "G17"),
        ("g19", "G19"),
    ],
)
def test_plane_repeat(tmp_machine, c, s):
    g, f = tmp_machine
    s0 = "start of plane commands"
    g.comment(s0)
    g.plane(s)
    g.plane(s)
    g.close()
    assert num_lines(f, c) == 1


def test_plane_fail(tmp_machine):
    g, _ = tmp_machine
    with pytest.raises(MachineError):
        g.plane("AB")

    with pytest.raises(MachineError):
        g.plane("UV")


def test_toolchange(tmp_machine):
    g, f = tmp_machine
    # should start on tool #1
    g.toolchange(1)
    g.toolchange(2)
    g.toolchange(2)
    g.close()
    assert num_lines(f, "T1") == 1
    assert num_lines(f, "T2") == 1


@pytest.mark.parametrize(
    "kwargs,in_result,not_in_result",
    [
        ({"exact_path": True}, ["G61"], ["G61.1", "G64", "G61 P"]),
        ({"exact_stop": True}, ["G61.1"], ["G64", "G61.1 P"]),
        ({"p": 0.5}, ["G64 P0.5"], ["G61", "G64 P0.5 Q"]),
        ({"p": 0.2, "q": 0.3}, ["G64 P0.2", "Q0.3"], ["G61"]),
    ],
)
def test_path_mode(tmp_machine, kwargs, in_result, not_in_result):
    g, f = tmp_machine
    g.path_mode(**kwargs)
    g.close()
    with open(f) as f0:
        lines = f0.readlines()

    l0 = next(l for l in lines[::-1] if ("G61" in l) or ("G64" in l))
    for s in in_result:
        assert s in l0

    for s in not_in_result:
        assert s not in l0


def test_dwell(tmp_machine):
    g, f = tmp_machine
    g.dwell(3.145)
    g.dwell(3.145)
    g.close()
    assert "G4 P3.145" in line(f, -1)
    # there was two dwell commands
    assert "G4 P3.145" in line(f, -2)
