import pytest
from gmcode import geom
import math


@pytest.mark.parametrize("val", [1, 1.0, 0, 0.0, 7])
@pytest.mark.parametrize("d", ["x", "y", "z"])
def test_vector_abs(d, val):
    a = geom.Vector(1, 0, 0)
    a = geom.Vector(**{d: val})
    assert abs(a) == pytest.approx(val, abs=1e-6)


def test_vector_abs2():
    a = geom.Vector(1, 1, 1)
    assert abs(a) == math.sqrt(3)


def test_vector_eq():
    vec0 = geom.Vector(1, 2, 3)
    vec1 = geom.Vector(1.0, 2.0, 3.0)
    assert vec0 == vec1

    vec2 = geom.Vector(0, 0, 0)
    vec3 = geom.Vector(0.0, 0, 0.0)
    assert vec2 == vec3

    vec4 = geom.Vector(1 / 2, 1.0 / 2.0, 10 / 1.0)
    vec5 = geom.Vector(0.5, 1 / 2, 10)
    assert vec4 == vec5

    assert geom.Vector(1, 2, 3) in [vec0, vec1, vec2, vec3]


@pytest.mark.parametrize("d", ["x", "y", "z"])
def test_vector_add(d):
    a, b = 2, 5
    veca = geom.Vector(**{d: a})
    vecb = geom.Vector(**{d: b})
    vec_res = veca + vecb
    assert getattr(vec_res, d) == pytest.approx(a + b)
    assert vec_res == (vecb + veca)
    for attr in ["x", "y", "z"]:
        if attr != d:
            assert getattr(vec_res, attr) == pytest.approx(0, abs=1e-6)


def test_vector_mul():
    a, b = 3, 7
    veca = geom.Vector(a, a, a)
    for res in [veca * b, b * veca]:
        for attr in ["x", "y", "z"]:
            assert getattr(res, attr) == pytest.approx(a * b)
    


@pytest.mark.parametrize("d", ["x", "y", "z"])
def test_vector_sub(d):
    a, b = 2, 5
    veca = geom.Vector(**{d: a})
    vecb = geom.Vector(**{d: b})
    vec_res = veca - vecb
    assert getattr(vec_res, d) == pytest.approx(a - b)
    for attr in ["x", "y", "z"]:
        if attr != d:
            assert getattr(vec_res, attr) == pytest.approx(0, abs=1e-6)
