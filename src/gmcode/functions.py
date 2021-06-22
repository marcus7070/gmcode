"""
Functions that operate on a Machine object.
"""

from gmcode import Machine, Vector, MachineError
from gmcode.geom import ArcXY
from itertools import cycle, product
from math import copysign, ceil, atan2


def spiral(
    m: Machine, centre: Vector, radius_end: float, doc: float = 0.2, cw: bool = True
):
    """
    Creates a spiral movement from the current position, around the centre,
    until the toolpath radius is at radius_end.

    Args:
      m: Machine object to act upon.
      centre: Centre point of the spiral. This should have the same z height as the centre.
      radius_end: The final radius of the spiral.
      doc: Depth of cut.
      cw: Clockwise?

    Used for pocketing/clearing material.
    """

    if (centre.z - m.position.z) > m.accuracy:
        raise MachineError("Can not handle centre and start point outside of XY plane")

    vec0 = m.position - centre
    radius_current = abs(vec0)
    doc = copysign(doc, radius_end - radius_current)  # negative for cutting inwards
    wobble = vec0.unit_vector() * doc / 4
    centres = [centre - wobble, centre + wobble]
    counter = 0
    m.arc(i=centre.x, j=centre.y, cw=cw)
    for c in cycle(centres):
        # make a 180 degree arc around c
        end = c - (m.position - c)
        a = ArcXY(start=m.position, end=end, centre=c, cw=cw)
        m.cut([a])
        distance_to_go = copysign(1, doc) * ((radius_end - doc) - a.radius())
        if distance_to_go <= m.accuracy:
            break

        counter += 1
        if counter > 10000:
            raise MachineError("Infinite loop in spiral")

    # final cut, a circle at end radius
    m.arc(i=centre.x, j=centre.y, cw=cw)
    end = centre + (m.position - centre).unit_vector() * radius_end
    m.g1(end.x, end.y)
    m.arc(i=centre.x, j=centre.y, cw=cw)


def helical_entry(
    m: Machine,
    centre: Vector,
    final_height: float,
    doc: float = 0.2,
    cw: bool = True,
):
    """
    Helix with a defined depth of cut.

    Args:
      m: Machine instance to act on.
      centre: Centre of the helix, z value doesn't matter.
      final_height: Helix will end at this height.
      doc: Helix will be close to this depth of cut, will not exceed it.
      cw: Clockwise?

    Will wind up at the same x and y position it started from.
    """

    m.comment("helical entry start")
    total_height = abs(m.position.z - final_height)
    loops = ceil(total_height / doc)
    m.arc(z=final_height, i=centre.x, j=centre.y, p=loops, cw=cw)


def rect_in(
    m: Machine,
    centre: Vector = Vector(),
    woc: float = 0.2,
    cw: bool = True,
):
    """
    Remove material with a rectangular x and y axis aligned pattern.

    Args:
      m: Machine instance to act on.
      centre: Centre of the pattern, z value doesn't matter.
      woc: Width of cut, postive value.
      cw: Clockwise?

    Useful for facing rectangular stock.
    """

    m.comment("rect_in start")

    # get 4 starting corners
    offset = m.position - centre
    corner_offsets = [
        (
            Vector(sign_x * offset.x, sign_y * offset.y),
            Vector(sign_x, sign_y),
        )  # a tuple of the actual offset and the 45 degree offset direction
        for sign_x, sign_y in product([-1, 1], repeat=2)
    ]

    # arrange them by CW or CCW
    corner_offsets.sort(key=lambda v: atan2(v[0].y, v[1].x))
    if not cw:
        corner_offsets.reverse()
    corners = cycle([(co[0] + centre, co[1]) for co in corner_offsets])

    # shift through the cycle until we are at the start point
    for c in corners:
        if all((c[0].x == m.position.x, c[0].y == m.position.y)):
            break

    # do the cuts
    total_woc = 0.0
    end_woc = min(offset.x, offset.y)
    for c in corners:
        total_woc += woc / 4
        end = c[0] - total_woc * c[1]
        m.g1(end.x, end.y)
        if total_woc > end_woc:
            break

    m.comment("rect_in end")
