import pytest
from gmcode import Machine


@pytest.fixture
def tmp_file(tmp_path_factory):
    fname = tmp_path_factory.mktemp("tmp_file")
    fname = fname / "test.ngc"
    return fname


@pytest.fixture
def tmp_machine(tmp_file):
    g = Machine(tmp_file)
    g.std_init()
    return g
