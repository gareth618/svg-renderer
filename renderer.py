import re
import path
import colors
from PIL import Image, ImageDraw

def render(ast):
    """This function takes as input the AST of an SVG and returns
    a `PIL.Image` object containing the equivalent PNG image.
    """
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

        # updating the `context` based on the presentation attributes in the current node
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
            'outline': (*new_context['stroke'], new_context['opacity']) if new_context['stroke'] else None,
            'width': new_context['stroke-width']
        }

        # getting rid of the weird prefix of the SVG nodes generated using the `xml` package
        tag = node.tag[len('{http://www.w3.org/2000/svg}'):]
        # we draw each shape in its own overlay image that's going to be composed with the initial one
        # we can't take into account the opacity of the shape in any other way
        overlay = None if tag == 'svg' else Image.new('RGBA', image.size, (255, 255, 255, 0))

        def clean_string(string):
            commands = 'mlhvcsqtazMLHVCSQTAZ'
            string = string.replace(',', ' ')
            string = re.sub(r'(?<!e)\-', ' -', string)
            string = re.sub(r'(?<!e)\+', ' +', string)
            for command in commands:
                string = string.replace(command, f' {command} ')
            string = string.strip()
            string = re.sub(r' +', ' ', string)
            return string

        def draw_polyline(points):
            for p1, p2 in zip(points[:-1], points[1:]):
                ImageDraw.Draw(overlay).line([
                    (x_offset + p1[0], y_offset + p1[1]),
                    (x_offset + p2[0], y_offset + p2[1])
                ], **line_attrs)

        if tag == 'svg':
            x_offset, y_offset, image_w, image_h = [float(val) for val in clean_string(node.attrib['viewBox']).split()]
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
            draw_polyline([(x1, y1), (x2, y2)])

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
            args = [float(val) for val in clean_string(node.attrib['points']).split()]
            draw_polyline(list(zip(args[0::2], args[1::2])))

        if tag == 'polygon':
            args = [float(val) for val in clean_string(node.attrib['points']).split()]
            ImageDraw.Draw(overlay).polygon([(x_offset + x, y_offset + y) for x, y in zip(args[0::2], args[1::2])], **shape_attrs)

        if tag == 'path':
            parser = path.PathParser(clean_string(node.attrib['d']))
            shapes = [[]]
            while True:
                new_shape, points = parser.next_points()
                if points is None: break
                if not points: continue
                if new_shape and shapes[-1]:
                    shapes.append([])
                shapes[-1] += [(point.real, point.imag) for point in points]
            if new_context['fill']:
                for shape in shapes:
                    ImageDraw.Draw(overlay).polygon([(x_offset + x, y_offset + y) for x, y in shape], **shape_attrs)
            else:
                for shape in shapes:
                    draw_polyline(shape)

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
