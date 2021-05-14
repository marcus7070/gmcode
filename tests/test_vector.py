import pytest
from gmcode.geom import Vector
import math


@pytest.mark.parametrize("val", [1, 1.0, 0, 0.0, 7])
@pytest.mark.parametrize("d", ["x", "y", "z"])
def test_vector_abs(d, val):
    a = Vector(1, 0, 0)
    a = Vector(**{d: val})
    assert abs(a) == pytest.approx(val, abs=1e-6)


def test_vector_abs2():
    a = Vector(1, 1, 1)
    assert abs(a) == math.sqrt(3)


def test_vector_eq():
    vec0 = Vector(1, 2, 3)
    vec1 = Vector(1.0, 2.0, 3.0)
    assert vec0 == vec1

    vec2 = Vector(0, 0, 0)
    vec3 = Vector(0.0, 0, 0.0)
    assert vec2 == vec3

    vec4 = Vector(1 / 2, 1.0 / 2.0, 10 / 1.0)
    vec5 = Vector(0.5, 1 / 2, 10)
    assert vec4 == vec5

    assert Vector(1, 2, 3) in [vec0, vec1, vec2, vec3]


@pytest.mark.parametrize("d", ["x", "y", "z"])
def test_vector_add(d):
    a, b = 2, 5
    veca = Vector(**{d: a})
    vecb = Vector(**{d: b})
    vec_res = veca + vecb
    assert getattr(vec_res, d) == pytest.approx(a + b)
    assert vec_res == (vecb + veca)
    for attr in ["x", "y", "z"]:
        if attr != d:
            assert getattr(vec_res, attr) == pytest.approx(0, abs=1e-6)


def test_vector_mul():
    a, b = 3, 7
    veca = Vector(a, a, a)
    for res in [veca * b, b * veca]:
        for attr in ["x", "y", "z"]:
            assert getattr(res, attr) == pytest.approx(a * b)
    


@pytest.mark.parametrize("d", ["x", "y", "z"])
def test_vector_sub(d):
    a, b = 2, 5
    veca = Vector(**{d: a})
    vecb = Vector(**{d: b})
    vec_res = veca - vecb
    assert getattr(vec_res, d) == pytest.approx(a - b)
    for attr in ["x", "y", "z"]:
        if attr != d:
            assert getattr(vec_res, attr) == pytest.approx(0, abs=1e-6)


@pytest.mark.parametrize("d", ["x", "y", "z"])
def test_vector_truediv(d):
    a, b = 11, 13
    veca = Vector(**{d: a})
    vec_res = veca / b
    assert getattr(vec_res, d) == pytest.approx(a / b)
    for attr in ["x", "y", "z"]:
        if attr != d:
            assert getattr(vec_res, attr) == pytest.approx(0)


def test_vector_truediv2():
    vec0 = Vector(0, 0, 0.0)
    assert vec0 / 2 == vec0

    vec1 = Vector(10, 11.0, 12)
    div = 3
    assert abs(vec1) / div == abs(vec1 / div)


@pytest.mark.parametrize("d", ["x", "y", "z"])
def test_vector_unit_vector(d):
    vec0 = Vector(**{d: 11})
    vec1 = vec0.unit_vector()
    assert getattr(vec1, d) == pytest.approx(1)


def test_vector_unit_vector2():
    vec0 = Vector(11, 12, 13)
    vec1 = vec0.unit_vector()
    assert abs(vec1) == pytest.approx(1)

    vec2 = 100 * vec0
    assert vec1 == vec2.unit_vector()


def test_vector_cross():
    v0 = Vector(1, 2, 3)
    v1 = Vector(4, 5, 6)
    v2 = v0.cross(v1)
    assert v2 == Vector(-3, 6, -3)


def test_vector_chaining():
    v0 = Vector(-1, -1, -1)
    v1 = v0 + Vector(0, 0, -1) + Vector() + Vector(0, 0, 1)
    assert v0 == v1
    v2 = Vector(1.0, 0, 0).unit_vector().cross(Vector(0, 0, 1.0))
    assert v2 == Vector(0, -1, 0)
