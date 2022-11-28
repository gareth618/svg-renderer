from PIL import Image, ImageDraw

def svg_to_png(_):
    image = Image.new('RGB', (100, 100))
    ImageDraw.Draw(image).line([(0, 0), (100, 100)])
    return image
