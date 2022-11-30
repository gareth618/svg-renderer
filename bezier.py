def reflect(p1, p2):
    c1 = complex(*p1)
    c2 = complex(*p2)
    c3 = 2 * c2 - c1
    return (c3.real, c3.imag)

def lerp(c1, c2, t):
    return c1 * (1 - t) + c2 * t

def quadratic_bezier(p1, p2, p3):
    c11 = complex(*p1)
    c12 = complex(*p2)
    c13 = complex(*p3)
    points = [p1]
    for i in range(0, 100):
        t = i / 100
        c21 = lerp(c11, c12, t)
        c22 = lerp(c12, c13, t)
        c31 = lerp(c21, c22, t)
        points.append((c31.real, c31.imag))
    points.append(p3)
    return points

def cubic_bezier(p1, p2, p3, p4):
    c11 = complex(*p1)
    c12 = complex(*p2)
    c13 = complex(*p3)
    c14 = complex(*p4)
    points = [p1]
    for i in range(0, 100):
        t = i / 100
        c21 = lerp(c11, c12, t)
        c22 = lerp(c12, c13, t)
        c23 = lerp(c13, c14, t)
        c31 = lerp(c21, c22, t)
        c32 = lerp(c22, c23, t)
        c41 = lerp(c31, c32, t)
        points.append((c41.real, c41.imag))
    points.append(p4)
    return points

def smooth_quadratic_bezier(p0, p1, p3):
    p2 = reflect(p0 or p1, p1)
    return quadratic_bezier(p1, p2, p3)

def smooth_cubic_bezier(p0, p1, p3, p4):
    p2 = reflect(p0 or p1, p1)
    return cubic_bezier(p1, p2, p3, p4)
