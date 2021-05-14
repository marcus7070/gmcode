from gmcode.geom import Line, Arc, Vector
import pytest


def test_line_tangent():
    l0 = Line(Vector(0, 0, 0), Vector(0, 0, 1))
    assert l0.tangent() == Vector(0, 0, 1)

    v0 = Vector(11, 12, 13)
    v_offset = Vector(1, 1, 1)
    l1 = Line(v0, v0 + v_offset)
    assert l1.tangent() == v_offset.unit_vector()


def test_line_offset():
    l0 = Line(Vector(0, 0, 0), Vector(1, 0, 0))
    offset = 1
    l1 = l0.offset_xy(offset)
    assert l1.tangent() == l0.tangent()
    assert l1.end == Vector(1, -1, 0)
