def reflect(p1, p2):
    return 2 * p2 - p1

def lerp(p1, p2, t):
    return p1 * (1 - t) + p2 * t

def quadratic_bezier(p11, p12, p13):
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
    p2 = reflect(p0 or p1, p1)
    return quadratic_bezier(p1, p2, p3)

def smooth_cubic_bezier(p0, p1, p3, p4):
    p2 = reflect(p0 or p1, p1)
    return cubic_bezier(p1, p2, p3, p4)
