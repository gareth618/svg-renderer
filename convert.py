import re
import json
from PIL import Image, ImageDraw

color_codes = json.load(open('color-codes.json', 'r'))

def string_to_rgb(string):
    if re.match(r'#[0-9a-fA-F]{6}', string):
        r = string[1:3]
        g = string[3:5]
        b = string[5:7]
        return int(r, 16), int(g, 16), int(b, 16)
    match = re.match(r'rgb *\((?P<r>\d{1,3}), *(?P<g>\d{1,3}), *(?P<b>\d{1,3})\)', string)
    if match:
        return (
            int(match.groupdict()['r']),
            int(match.groupdict()['g']),
            int(match.groupdict()['b'])
        )
    if string in color_codes:
        return string_to_rgb(color_codes[string])

def svg_to_png(ast):
    image = None
    image_w = 0
    image_h = 0
    x_offset = 0
    y_offset = 0

    def dfs(node, context):
        nonlocal image
        nonlocal image_w
        nonlocal image_h
        nonlocal x_offset
        nonlocal y_offset

        new_context = context.copy()
        if 'stroke' in node.attrib:
            new_context['stroke'] = string_to_rgb(node.attrib['stroke'])
        if 'stroke-width' in node.attrib:
            new_context['stroke-width'] = int(float(node.attrib['stroke-width']))
        if 'fill' in node.attrib:
            new_context['fill'] = string_to_rgb(node.attrib['fill'])
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

        if tag == 'svg':
            x_offset, y_offset, image_w, image_h = [float(val) for val in node.attrib['viewBox'].split()]
            x_offset = -x_offset
            y_offset = -y_offset
            image_w = int(image_w)
            image_h = int(image_h)
            image = Image.new('RGBA', (image_w, image_h))
            ImageDraw.Draw(image).rectangle([(0, 0), (image_w, image_h)], fill=(255, 255, 255, 255))

        if tag == 'line':
            x1 = x_offset + float(node.attrib['x1'])
            y1 = y_offset + float(node.attrib['y1'])
            x2 = x_offset + float(node.attrib['x2'])
            y2 = y_offset + float(node.attrib['y2'])
            ImageDraw.Draw(overlay).line([(x1, y1), (x2, y2)], **line_attrs)

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
            for p1, p2 in zip(points[:-1], points[1:]):
                ImageDraw.Draw(overlay).line([
                    (x_offset + p1[0], y_offset + p1[1]),
                    (x_offset + p2[0], y_offset + p2[1])
                ], **line_attrs)

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

__all__ = ['svg_to_png']
