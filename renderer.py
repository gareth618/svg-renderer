import re
import colors
import bezier
from PIL import Image, ImageDraw

def render(ast):
    image = None
    image_w = 0
    image_h = 0
    x_offset = 0
    y_offset = 0
    rgb = colors.CreateRGB()

    def dfs(node, context):
        nonlocal image
        nonlocal image_w
        nonlocal image_h
        nonlocal x_offset
        nonlocal y_offset

        new_context = context.copy()
        if 'stroke' in node.attrib:
            new_context['stroke'] = rgb.from_string(node.attrib['stroke'])
        if 'stroke-width' in node.attrib:
            new_context['stroke-width'] = int(float(node.attrib['stroke-width']))
        if 'fill' in node.attrib:
            new_context['fill'] = rgb.from_string(node.attrib['fill'])
        if 'opacity' in node.attrib:
            new_context['opacity'] = int(float(node.attrib['opacity']) * 255)

        line_attrs = {
            'fill': (*(new_context['stroke'] or (0, 0, 0)), new_context['opacity']),
            'width': new_context['stroke-width']
        }
        shape_attrs = {
            'fill': new_context['fill'] and (*new_context['fill'], new_context['opacity']),
            'outline': new_context['stroke'],
            'width': new_context['stroke-width']
        }

        tag = node.tag[len('{http://www.w3.org/2000/svg}'):]
        overlay = None if tag == 'svg' else Image.new('RGBA', image.size, (255, 255, 255, 0))

        def draw_lines(points):
            for p1, p2 in zip(points[:-1], points[1:]):
                ImageDraw.Draw(overlay).line([
                    (x_offset + p1[0], y_offset + p1[1]),
                    (x_offset + p2[0], y_offset + p2[1])
                ], **line_attrs)

        if tag == 'svg':
            x_offset, y_offset, image_w, image_h = [float(val) for val in node.attrib['viewBox'].split()]
            x_offset = -x_offset
            y_offset = -y_offset
            image_w = int(image_w)
            image_h = int(image_h)
            image = Image.new('RGBA', (image_w, image_h))
            ImageDraw.Draw(image).rectangle([(0, 0), (image_w, image_h)], fill=(255, 255, 255, 255))

        if tag == 'line':
            x1 = float(node.attrib['x1'])
            y1 = float(node.attrib['y1'])
            x2 = float(node.attrib['x2'])
            y2 = float(node.attrib['y2'])
            draw_lines([(x1, y1), (x2, y2)])

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
            ImageDraw.Draw(overlay).rounded_rectangle([(x, y), (x + w, y + h)], radius=(rx + ry) / 2, **shape_attrs)

        if tag == 'circle':
            cx = x_offset + float(node.attrib['cx'])
            cy = y_offset + float(node.attrib['cy'])
            r = float(node.attrib['r'])
            ImageDraw.Draw(overlay).ellipse([(cx - r, cy - r), (cx + r, cy + r)], **shape_attrs)

        if tag == 'ellipse':
            cx = x_offset + float(node.attrib['cx'])
            cy = y_offset + float(node.attrib['cy'])
            rx = float(node.attrib['rx'])
            ry = float(node.attrib['ry'])
            ImageDraw.Draw(overlay).ellipse([(cx - rx, cy - ry), (cx + rx, cy + ry)], **shape_attrs)

        if tag == 'polyline':
            points = [tuple(float(val) for val in point.split(',')) for point in node.attrib['points'].split()]
            draw_lines(points)

        if tag == 'path':
            path = node.attrib['d']
            path = path.replace(',', ' ')
            path = path.replace('-', ' -')
            for command in 'mlhvcsqtazMLHVCSQTAZ':
                path = path.replace(command, f' {command} ')
            path = path.strip()
            path = re.sub(r' +', ' ', path)
            tokens = path.split(' ')

            i, x, y = 0, 0, 0
            first_point = None
            last_point = None

            def next_relative_points(count):
                nonlocal i, tokens, x, y
                values = [float(token) for token in tokens[i + 1:i + 2 * count + 1]]
                i += 2 * count + 1
                xs = [x] + [x + cx for cx in values[0::2]]
                ys = [y] + [y + cy for cy in values[1::2]]
                x, y = xs[-1], ys[-1]
                return list(zip(xs, ys))

            def next_absolute_points(count):
                nonlocal i, tokens, x, y
                values = [float(token) for token in tokens[i + 1:i + 2 * count + 1]]
                i += 2 * count + 1
                xs = [x] + values[0::2]
                ys = [y] + values[1::2]
                x, y = xs[-1], ys[-1]
                return list(zip(xs, ys))

            while i < len(tokens):
                if tokens[i] not in ['m', 'M'] and first_point is None:
                    first_point = x, y
                if tokens[i] in ['z', 'Z']:
                    draw_lines([(x, y), first_point])
                    i += 1
                elif tokens[i] == 'm':
                    x += float(tokens[i + 1])
                    y += float(tokens[i + 2])
                    i += 3
                elif tokens[i] == 'M':
                    x = float(tokens[i + 1])
                    y = float(tokens[i + 2])
                    i += 3
                elif tokens[i] == 'l':
                    draw_lines(next_relative_points(1))
                elif tokens[i] == 'L':
                    draw_lines(next_absolute_points(1))
                elif tokens[i] == 'h':
                    dx = float(tokens[i + 1])
                    draw_lines([(x, y), (x + dx, y)])
                    x += dx
                    i += 2
                elif tokens[i] == 'H':
                    new_x = float(tokens[i + 1])
                    draw_lines([(x, y), (new_x, y)])
                    x = new_x
                    i += 2
                elif tokens[i] == 'v':
                    dy = float(tokens[i + 1])
                    draw_lines([(x, y), (x, y + dy)])
                    y += dy
                    i += 2
                elif tokens[i] == 'V':
                    new_y = float(tokens[i + 1])
                    draw_lines([(x, y), (x, new_y)])
                    x = new_y
                    i += 2
                elif tokens[i] in ['c', 'C']:
                    points = next_relative_points(3) if tokens[i] == 'c' else next_absolute_points(3)
                    draw_lines(bezier.cubic_bezier(*points))
                    last_point = points[-2]
                elif tokens[i] in ['s', 'S']:
                    points = next_relative_points(2) if tokens[i] == 's' else next_absolute_points(2)
                    draw_lines(bezier.smooth_cubic_bezier(last_point, *points))
                    last_point = points[-2]
                elif tokens[i] in ['q', 'Q']:
                    points = next_relative_points(2) if tokens[i] == 'q' else next_absolute_points(2)
                    draw_lines(bezier.quadratic_bezier(*points))
                    last_point = points[-2]
                elif tokens[i] in ['t', 'T']:
                    points = next_relative_points(1) if tokens[i] == 't' else next_absolute_points(1)
                    draw_lines(bezier.smooth_quadratic_bezier(last_point, *points))
                    last_point = points[-2]

        if overlay:
            image = Image.alpha_composite(image, overlay)
        for son in node:
            dfs(son, new_context)

    dfs(ast.getroot(), {
        'stroke': None,
        'stroke-width': 1,
        'fill': (0, 0, 0),
        'opacity': 255
    })
    return image
