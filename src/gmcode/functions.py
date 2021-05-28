"""
Functions that operate on a Machine object.
"""

from gmcode import Machine, Vector, MachineError
from itertools import cycle
from math import copysign


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
    """

    if (centre.z - m.position.z) > m.accuracy:
        raise MachineError("Can not handle centre and start point outside of XY plane")
    vec0 = m.position - centre
    radius_start = abs(vec0)
    doc = copysign(doc, radius_start - radius_end)
    wobble = vec0.unit_vector() * doc / 2
    centres = [centre + wobble, centre - wobble]
    last_radius = radius_end - doc  # the last radius that the spiral out should cut
    counter = 0
    for c in cycle(centres):
        # make a 180 degree arc around c
        end = (c - m.position) + c
        m.arc(end.x, end.y, i=c.x, j=c.y, cw=cw)
        if abs(m.position - centre) - radius_end <= doc:
            break

        counter += 1
        if counter > 10000:
            raise MachineError("Infinite loop in spiral")

    # final cut, a circle at end radius
    m.arc(i=centre.x, j=centre.y, cw=cw)
    end = centre + vec0.unit_vector() * radius_end
    m.g1(end.x, end.y)
    m.arc(i=centre.x, j=centre.y, cw=cw)
