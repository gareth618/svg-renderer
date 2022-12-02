"""This module contains functions working with complex numbers
in order to accomplish analytical tasks related to Bézier curves.
"""

def reflect(p1, p2):
    """This function returns the reflection of `p1` relative to `p2`."""
    return 2 * p2 - p1

def lerp(p1, p2, t):
    """This function performs linear interpolation between `p1` and `p2`
    with parameter `t` and returns the resulting point.
    """
    return p1 * (1 - t) + p2 * t

def quadratic_bezier(p11, p12, p13):
    """This function returns a polyline of `100` points approximating the
    quadratic Bézier curve with parameters `p11`, `p12` and `p13`.
    """
    points = [p11]
    for i in range(0, 100):
        t = i / 100
        p21 = lerp(p11, p12, t)
        p22 = lerp(p12, p13, t)
        p31 = lerp(p21, p22, t)
        points.append(p31)
    points.append(p13)
    return points

def cubic_bezier(p11, p12, p13, p14):
    """This function returns a polyline of `100` points approximating the
    cubic Bézier curve with parameters `p11`, `p12`, `p13` and `p14`.
    """
    points = [p11]
    for i in range(0, 100):
        t = i / 100
        p21 = lerp(p11, p12, t)
        p22 = lerp(p12, p13, t)
        p23 = lerp(p13, p14, t)
        p31 = lerp(p21, p22, t)
        p32 = lerp(p22, p23, t)
        p41 = lerp(p31, p32, t)
        points.append(p41)
    points.append(p14)
    return points

def smooth_quadratic_bezier(p0, p1, p3):
    """This function is used in rendering the SVG-path `T` command and
    returns the quadratic Bézier curve where the first parameter is `p1`,
    the second one is the reflection of `p0` relative to `p1`
    (or `p1` if `p0` is `None`) and the third one is `p3`.
    """
    p2 = reflect(p0 or p1, p1)
    return quadratic_bezier(p1, p2, p3)

def smooth_cubic_bezier(p0, p1, p3, p4):
    """This function is used in rendering the SVG-path `S` command and
    returns the cubic Bézier curve where the first parameter is `p1`,
    the second one is the reflection of `p0` relative to `p1`
    (or `p1` if `p0` is `None`), the third one is `p3` and the fourth one is `p4`.
    """
    p2 = reflect(p0 or p1, p1)
    return cubic_bezier(p1, p2, p3, p4)
