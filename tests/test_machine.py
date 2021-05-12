import pytest
from gmcode import Machine


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


@pytest.mark.parametrize("o", [0, 0.0])
def test_g0_no_move(tmp_machine, o):
    g, f = tmp_machine
    g.write("something")  # incase std_init does not produce any output
    g.g0(o, o, o)
    g.close()
    l0 = line(f, -1)
    assert "G0" not in l0


def test_g0_no_move_accuracy(tmp_machine):
    g, f = tmp_machine
    acc = g.accuracy * 0.9
    g.write("something")
    g.g0(z=acc)
    g.close()
    l0 = line(f, -1)
    assert "G0" not in l0
