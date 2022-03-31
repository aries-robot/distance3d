import math
import numpy as np
from .utils import norm_vector


def point_to_line(point, line_point, line_direction):
    """Compute the shortest distance between point and line.

    Parameters
    ----------
    point : array, shape (3,)
        3D point.

    line_point : array, shape (3,)
        Point on line.

    line_direction : array, shape (3,)
        Direction of the line. This is assumed to be of unit length.

    Returns
    -------
    distance : float
        The shortest distance between point and line.

    contact_point_line : array, shape (3,)
        Closest point on line.
    """
    return _point_to_line(point, line_point, line_direction)[:2]


def _point_to_line(point, line_point, line_direction):
    diff = point - line_point
    t = np.dot(line_direction, diff)
    direction_fraction = t * line_direction
    diff -= direction_fraction
    point_on_line = line_point + direction_fraction
    return np.linalg.norm(diff), point_on_line, t


def point_to_line_segment(point, segment_start, segment_end):
    """Compute the shortest distance between point and line segment.

    Parameters
    ----------
    point : array, shape (3,)
        3D point.

    segment_start : array, shape (3,)
        Start point of segment.

    segment_end : array, shape (3,)
        End point of segment.

    Returns
    -------
    distance : float
        The shortest distance between point and line segment.

    contact_point_line_segment : array, shape (3,)
        Closest point on line segment.
    """
    segment_direction = segment_end - segment_start
    # Project point onto segment, computing parameterized position
    # s(t) = segment_start + t * (segment_end - segment_start)
    t = (np.dot(point - segment_start, segment_direction) /
         np.dot(segment_direction, segment_direction))
    # If outside segment, clamp t to the closest endpoint
    t = min(max(t, 0.0), 1.0)
    # Compute projected position from the clamped t
    contact_point = segment_start + t * segment_direction
    return np.linalg.norm(point - contact_point), contact_point


def line_to_line(line_point1, line_direction1, line_point2, line_direction2,
                 epsilon=1e-6):
    """Compute the shortest distance between two lines.

    Parameters
    ----------
    line_point1 : array, shape (3,)
        Point on the first line.

    line_direction1 : array, shape (3,)
        Direction of the first line. This is assumed to be of unit length.
        Otherwise, it will only be normalized internally when you set
        normalize_directions to True.

    line_point2 : array, shape (3,)
        Point on the second line.

    line_direction2 : array, shape (3,)
        Direction of the second line. This is assumed to be of unit length.
        Otherwise, it will only be normalized internally when you set
        normalize_directions to True.

    epsilon : float, optional (default: 1e-6)
        Values smaller than epsilon are considered to be 0.

    Returns
    -------
    distance : float
        The shortest distance between two lines.

    contact_point_line1 : array, shape (3,)
        Closest point on first line.

    contact_point_line2 : array, shape (3,)
        Closest point on second line.
    """
    return _line_to_line(
        line_point1, line_direction1, line_point2, line_direction2, epsilon)[:3]


def _line_to_line(line_point1, line_direction1, line_point2, line_direction2,
                  epsilon=1e-6):
    diff = line_point1 - line_point2
    a12 = -np.dot(line_direction1, line_direction2)
    b1 = np.dot(line_direction1, diff)
    c = np.dot(diff, diff)
    det = 1.0 - a12 * a12

    if abs(det) >= epsilon:
        b2 = -np.dot(line_direction2, diff)
        t1 = (a12 * b2 - b1) / det
        t2 = (a12 * b1 - b2) / det
        dist_squared = (
            t1 * (t1 + a12 * t2 + 2.0 * b1)
            + t2 * (a12 * t1 + t2 + 2.0 * b2) + c)
        contact_point2 = line_point2 + t2 * line_direction2
    else:  # parallel lines
        t1 = -b1
        t2 = 0.0
        dist_squared = b1 * t1 + c
        contact_point2 = line_point2

    contact_point1 = line_point1 + t1 * line_direction1

    return math.sqrt(abs(dist_squared)), contact_point1, contact_point2, t1, t2


def line_to_line_segment(
        line_point, line_direction, segment_start, segment_end, epsilon=1e-6):
    """Compute the closest point between line and line segment.

    Parameters
    ----------
    line_point : array, shape (3,)
        Point on line.

    line_direction : array, shape (3,)
        Direction of the line. This is assumed to be of unit length.

    segment_start : array, shape (3,)
        Start point of segment.

    segment_end : array, shape (3,)
        End point of segment.

    epsilon : float, optional (default: 1e-6)
        Values smaller than epsilon are considered to be 0.

    Returns
    -------
    dist : float
        The shortest distance between line and line segment.

    contact_point1 : array, shape (3,)
        Contact point on line.

    contact_point2 : array, shape (3,)
        Contact point on line segment.
    """
    return _line_to_line_segment(
        line_point, line_direction, segment_start, segment_end, epsilon)[:3]


# modified version of line segment to line segment
def _line_to_line_segment(
        line_point, line_direction, segment_start, segment_end,
        epsilon=1e-6):
    # Segment direction vectors
    d = segment_end - segment_start

    # Squared segment lengths, always nonnegative
    a = np.dot(d, d)
    e = np.dot(line_direction, line_direction)

    if a < epsilon and e < epsilon:
        # Both segments degenerate into points
        return (np.linalg.norm(line_point - segment_start),
                segment_start, line_point)

    r = segment_start - line_point
    f = np.dot(line_direction, r)

    if a < epsilon:
        # First segment degenerates into a point
        s = 0.0
        t = f / e
    else:
        c = np.dot(d, r)
        if e <= epsilon:
            # Second segment degenerates into a point
            t = 0.0
            s = min(max(-c / a, 0.0), 1.0)
        else:
            # General nondegenerate case
            b = np.dot(d, line_direction)
            denom = a * e - b * b  # always nonnegative

            if denom != 0.0:
                # If segements not parallel, compute closest point on line 1 to
                # line 2 and clamp to segment 1.
                s = min(max((b * f - c * e) / denom, 0.0), 1.0)
            else:
                # Parallel case: compute arbitrary s.
                s = 0.0

            t = (b * s + f) / e

    contact_point1 = line_point + t * line_direction
    contact_point2 = segment_start + s * d

    return np.linalg.norm(contact_point2 - contact_point1), contact_point1, contact_point2, t, s


def line_segment_to_line_segment(
        segment_start1, segment_end1, segment_start2, segment_end2, epsilon=1e-6):
    """Compute the shortest distance between two line segments.

    Implementation according to Ericson: Real-Time Collision Detection (2005).

    Parameters
    ----------
    segment_start1 : array, shape (3,)
        Start point of segment 1.

    segment_end1 : array, shape (3,)
        End point of segment 1.

    segment_start2 : array, shape (3,)
        Start point of segment 2.

    segment_end2 : array, shape (3,)
        End point of segment 2.

    epsilon : float, optional (default: 1e-6)
        Values smaller than epsilon are considered to be 0.

    Returns
    -------
    distance : float
        The shortest distance between two line segments.

    contact_point_segment1 : array, shape (3,)
        Closest point on first line segment.

    contact_point_segment2 : array, shape (3,)
        Closest point on second line segment.
    """
    # Segment direction vectors
    d1 = segment_end1 - segment_start1
    d2 = segment_end2 - segment_start2

    # Squared segment lengths, always nonnegative
    a = np.dot(d1, d1)
    e = np.dot(d2, d2)

    if a < epsilon and e < epsilon:
        # Both segments degenerate into points
        return (np.linalg.norm(segment_start2 - segment_start1),
                segment_start1, segment_start2)

    r = segment_start1 - segment_start2
    f = np.dot(d2, r)

    if a < epsilon:
        # First segment degenerates into a point
        s = 0.0
        t = min(max(f / e, 0.0), 1.0)
    else:
        c = np.dot(d1, r)
        if e <= epsilon:
            # Second segment degenerates into a point
            t = 0.0
            s = min(max(-c / a, 0.0), 1.0)
        else:
            # General nondegenerate case
            b = np.dot(d1, d2)
            denom = a * e - b * b  # always nonnegative

            if denom != 0.0:
                # If segements not parallel, compute closest point on line 1 to
                # line 2 and clamp to segment 1.
                s = min(max((b * f - c * e) / denom, 0.0), 1.0)
            else:
                # Parallel case: compute arbitrary s.
                s = 0.0

            t = (b * s + f) / e

            # If t in [0, 1] done. Else clamp t, recompute s.
            if t < 0.0:
                t = 0.0
                s = min(max(-c / a, 0.0), 1.0)
            elif t > 1.0:
                t = 1.0
                s = min(max((b - c) / a, 0.0), 1.0)

    contact_point1 = segment_start1 + s * d1
    contact_point2 = segment_start2 + t * d2

    return np.linalg.norm(contact_point2 - contact_point1), contact_point1, contact_point2


def point_to_plane(point, plane_point, plane_normal, signed=False):
    """Compute the shortest distance between a point and a plane.

    Parameters
    ----------
    point : array, shape (3,)
        3D point.

    plane_point : array, shape (3,)
        Point on the plane.

    plane_normal : array, shape (3,)
        Normal of the plane. We assume unit length.

    signed : bool, optional (default: False)
        Should the distance have a sign?

    Returns
    -------
    dist : float
        The shortest distance between two line segments. A sign indicates
        the direction along the normal.

    contact_point_plane : array, shape (3,)
        Closest point on plane.
    """
    t = np.dot(plane_normal, point - plane_point)
    contact_point_plane = point - t * plane_normal
    if not signed:
        t = abs(t)
    return t, contact_point_plane
