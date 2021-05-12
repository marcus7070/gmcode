from gmcode.geom import Line, ArcXY, Vector
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


@pytest.mark.parametrize("d", ["x", "y", "z"])
def test_line_length(d):
    end = Vector(**{d: 1})
    l0 = Line(Vector(0, 0, 0), end)
    assert l0.length() == pytest.approx(1)


def test_line_length2():
    assert (
        pytest.approx(3.3)
        == Line(
            start=Vector(10, 10, 10),
            end=Vector(10, 13.3, 10),
        ).length()
    )


@pytest.mark.parametrize("d", ["x", "y", "z"])
def test_line_centre(d):
    assert (
        Vector(**{d: 2.2})
        == Line(
            Vector(),
            Vector(**{d: 4.4}),
        ).centre()
    )


def test_line_centre2():
    assert (
        Vector(-2, -2.0, -2)
        == Line(
            Vector(-1, -1.0, -1),
            Vector(-3, -3, -3),
        ).centre()
    )


def test_line_offset_z():
    l0 = Line(
        Vector(5, 5, 5),
        Vector(6, 6, 5),
    ).offset_z(2.5)
    assert l0.start.z == pytest.approx(7.5)
    assert l0.end.z == pytest.approx(7.5)
    assert l0.centre().z == pytest.approx(7.5)


# @pytest.mark.parametrize("r", [0.01, 0.1, 1, 10, 100, 1000])
# def test_arcxy_centre(r):
#
#     a0 = ArcXY(
#         start=Vector(0, r, 0),
#         end=Vector(r, 0, 0),
#         radius=r,
#     )
#     assert a0.centre() == Vector(0, 0, 0)
#
#     a1 = ArcXY(
#         start=Vector(r, 0, 0),
#         end=Vector(0, r, 0),
#         radius=r,
#     )
#     assert a1.centre() == Vector(r, r, 0)
#
#     a2 = ArcXY(
#         start=Vector(0, r, 0),
#         end=Vector(r, 0, 0),
#         radius=-r,
#     )
#     assert a2.centre() == Vector(r, r, 0)


def test_arcxy():

    a0 = ArcXY(
        start=Vector(0, 1, 0),
        end=Vector(1, 0, 0),
        centre=Vector(0, 0, 0),
    )
    a1 = ArcXY(
        start=Vector(1, 0, 0),
        end=Vector(0, 1, 0),
        centre=Vector(0, 0, 0),
    )
    assert a0 != a1

    a2 = ArcXY(
        start=Vector(0.0, 1.0, 0.0),
        end=Vector(1.0, 0.0, 0.0),
        centre=Vector(0.0, 0.0, 0.0),
    )
    assert a0 == a2

    # centre too close to end
    with pytest.raises(ValueError):
        ArcXY(
            start=Vector(0, 1, 0),
            end=Vector(1, 0, 0),
            centre=Vector(1, 0.01, 0),
        )

    # centre too close to start
    with pytest.raises(ValueError):
        ArcXY(
            start=Vector(0, 1, 0),
            end=Vector(1, 0, 0),
            centre=Vector(0.01, 1, 0),
        )

    # a cw arc is different to a ccw arc
    a3 = ArcXY(
        start=Vector(-3, -3, 0),
        end=Vector(-2, -3, 0),
        centre=Vector(-2.5, 1, 0),
        cw=True,
    )
    a4 = ArcXY(
        start=Vector(-3, -3, 0),
        end=Vector(-2, -3, 0),
        centre=Vector(-2.5, 1, 0),
        cw=False,
    )
    assert a3 != a4


@pytest.mark.parametrize("r", [0.01, 0.1, 1, 10, 100, 1000])
def test_arcxy_tangent(r):

    a0 = ArcXY(
        start=Vector(0, r, 0),
        end=Vector(r, 0, 0),
        centre=Vector(),
    )
    assert a0.tangent(0) == Vector(1, 0, 0)
    assert a0.tangent(1) == Vector(0, -1, 0)

    a1 = ArcXY(
        start=Vector(r, 0, 0),
        end=Vector(0, r, 0),
        centre=Vector(),
        cw=False,
    )
    assert a1.tangent(0) == Vector(0, 1, 0)
    assert a1.tangent(1) == Vector(-1, 0, 0)

    a2 = ArcXY(
        start=Vector(r, r, r),
        end=Vector(r, r, r),
        centre=Vector(0, 0, r),
    )
    assert a2.tangent(0) == a2.tangent(1)
