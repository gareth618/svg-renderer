from PIL import Image, ImageDraw

def svg_to_png(ast):
    image = None
    image_w = 0
    image_h = 0
    x_offset = 0
    y_offset = 0

    def dfs(node):
        nonlocal image
        nonlocal image_w
        nonlocal image_h
        nonlocal x_offset
        nonlocal y_offset

        tag = node.tag[len('{http://www.w3.org/2000/svg}'):]
        if tag == 'svg':
            x_offset, y_offset, image_w, image_h = [float(val) for val in node.attrib['viewBox'].split()]
            x_offset = -x_offset
            y_offset = -y_offset
            image_w = int(image_w)
            image_h = int(image_h)
            image = Image.new('RGB', (image_w, image_h))

        if tag == 'line':
            x1 = x_offset + float(node.attrib['x1'])
            y1 = y_offset + float(node.attrib['y1'])
            x2 = x_offset + float(node.attrib['x2'])
            y2 = y_offset + float(node.attrib['y2'])
            ImageDraw.Draw(image).line([(x1, y1), (x2, y2)])

        if tag == 'rect':
            x = x_offset + float(node.attrib['x'])
            y = y_offset + float(node.attrib['y'])
            w = float(node.attrib['width'])
            h = float(node.attrib['height'])
            rx = 0
            ry = 0
            if 'rx' in node.attrib:
                rx = float(node.attrib['rx'])
                ry = float(node.attrib['rx'])
            if 'ry' in node.attrib:
                ry = float(node.attrib['ry'])
            ImageDraw.Draw(image).rounded_rectangle([(x, y), (x + w, y + h)], radius=(rx + ry) / 2)

        if tag == 'circle':
            cx = x_offset + float(node.attrib['cx'])
            cy = y_offset + float(node.attrib['cy'])
            r = float(node.attrib['r'])
            ImageDraw.Draw(image).ellipse([(cx - r, cy - r), (cx + r, cy + r)])

        if tag == 'ellipse':
            cx = x_offset + float(node.attrib['cx'])
            cy = y_offset + float(node.attrib['cy'])
            rx = float(node.attrib['rx'])
            ry = float(node.attrib['ry'])
            ImageDraw.Draw(image).ellipse([(cx - rx, cy - ry), (cx + rx, cy + ry)])

        if tag == 'polyline':
            points = [tuple(float(val) for val in point.split(',')) for point in node.attrib['points'].split()]
            for p1, p2 in zip(points[:-1], points[1:]):
                ImageDraw.Draw(image).line([
                    (x_offset + p1[0], y_offset + p1[1]),
                    (x_offset + p2[0], y_offset + p2[1])
                ])

        for son in node:
            dfs(son)

    dfs(ast.getroot())
    return image

__all__ = ['svg_to_png']
