import pytest
from gmcode import machine


@pytest.fixture(scope="session")
def tmp_file(tmp_path_factory):
    out = tmp_path_factory.mktemp("tmp_file")
    out = out / "test.ngc"
    return out


def tmp_machine(filename):
    out = machine.machine(filename)
    out.std_init()
    return out


def test_write(tmp_file):
    g = tmp_machine(tmp_file)
    g.close()
    assert tmp_file.exists()
