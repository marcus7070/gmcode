from gmcode.geom import Line, ArcXY, Vector
import pytest
import math


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


def test_arcxy_radius():

    a0 = ArcXY(
        start=Vector(1, 0, 0),
        end=Vector(0, 1, 0),
        centre=Vector(0, 0, 0),
    )
    assert a0.radius() == pytest.approx(1)

    a1 = ArcXY(
        start=Vector(10, 10, 0),
        end=Vector(14, 10, 0),
        centre=Vector(12, 10, 0),
    )
    assert a1.radius() == pytest.approx(2)

    a2 = ArcXY(
        start=Vector(-1, -1, -1),
        end=Vector(-1.5, -0.5, -1),
        centre=Vector(-1, -0.5, -1),
    )
    assert a2.radius() == pytest.approx(0.5)


def test_arcxy_radial_dir_centered():

    a0 = ArcXY(
        start=Vector(1, 0, 0),
        end=Vector(0, 1, 0),
        centre=Vector(0, 0, 0),
    )
    assert a0._radial_dir(0) == Vector(1, 0, 0)
    assert a0._radial_dir(1) == Vector(0, 1, 0)


def test_arcxy_radial_dir():

    a0 = ArcXY(
        start=Vector(1, 0, 0),
        end=Vector(0, 1, 0),
        centre=Vector(1, 1, 0),
    )
    assert a0._radial_dir(0) == Vector(0, -1, 0)
    assert a0._radial_dir(1) == Vector(-1, 0, 0)


@pytest.mark.parametrize("cw", [True, False])
def test_arcxy_offset_centered(cw):

    a0 = ArcXY(
        start=Vector(1, 0, 0),
        end=Vector(0, 1, 0),
        centre=Vector(0, 0, 0),
        cw=cw,
    )

    a1 = ArcXY(
        start=Vector(2, 0, 0),
        end=Vector(0, 2, 0),
        centre=Vector(0, 0, 0),
        cw=cw,
    )

    assert a0.offset_xy(1) == a1


@pytest.mark.parametrize("cw", [True, False])
@pytest.mark.parametrize("centre", [(1, 1), (2.5, -0.1), (-10, -10.1), (-0.1, 0.2)])
@pytest.mark.parametrize("radius", [0.1, 1.1, 10.3])
@pytest.mark.parametrize("angle_start", [30, 135, 181, 359])
@pytest.mark.parametrize("angle_end", [41, 146, 192, 348])
@pytest.mark.parametrize("offset", [0.1, 1.1, 10.1])
def test_arcxy_offset(cw, centre, radius, angle_start, angle_end, offset):

    centre_vec = Vector(*centre)
    start_vec = (
        Vector(
            math.cos(math.radians(angle_start)) * radius,
            math.sin(math.radians(angle_start)) * radius,
        )
        + centre_vec
    )
    end_vec = (
        Vector(
            math.cos(math.radians(angle_end)) * radius,
            math.sin(math.radians(angle_end)) * radius,
        )
        + centre_vec
    )
    a0 = ArcXY(
        start=start_vec,
        end=end_vec,
        centre=centre_vec,
        cw=cw,
    )
    a1 = a0.offset_xy(offset)

    def check(arc, offset):
        assert arc.radius() == pytest.approx(radius + offset)
        assert abs(arc.start - start_vec) == pytest.approx(abs(offset))
        assert abs(arc.end - end_vec) == pytest.approx(abs(offset))
        for val in [0, 1]:
            assert arc.tangent(val) == a0.tangent(val)

    check(a1, offset)

    new_offset = -radius / 2
    a2 = a0.offset_xy(new_offset)
    check(a2, new_offset)
