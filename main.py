import os
import sys
import colorama
import renderer
import xml.etree.ElementTree

exe_path = sys.argv[0]
args = sys.argv[1:]
svg_path = None
png_path = None
show_option = False
show_all_option = False

error = lambda string: f'{colorama.Style.BRIGHT}{colorama.Fore.RED}{string}{colorama.Style.RESET_ALL}'
message = lambda string: f'{colorama.Style.BRIGHT}{colorama.Fore.BLUE}{string}{colorama.Style.RESET_ALL}'
keyword = lambda string: f'{colorama.Fore.GREEN}{string}{colorama.Style.RESET_ALL}'
option = lambda string: f'{colorama.Fore.YELLOW}{string}{colorama.Style.RESET_ALL}'

if args and not os.path.isfile(args[0]):
    print(error('error:'), 'file', keyword(args[0]), 'not found')
    sys.exit(1)
elif len(args) == 1:
    svg_path = args[0]
elif len(args) == 2 and args[1] in ['-s', '--show']:
    svg_path = args[0]
    show_option = True
elif len(args) == 2 and args[1] in ['-sa', '--show-all']:
    svg_path = args[0]
    show_all_option = True
elif len(args) == 3 and args[1] in ['-o', '--output']:
    svg_path = args[0]
    png_path = args[2]
elif len(args) == 4 and args[1] in ['-o', '--output'] and args[3] in ['-s', '--show']:
    svg_path = args[0]
    png_path = args[2]
    show_option = True
elif len(args) == 4 and args[1] in ['-o', '--output'] and args[3] in ['-sa', '--show-all']:
    svg_path = args[0]
    png_path = args[2]
    show_all_option = True
else:
    print(error('error:'), 'wrong command format')
    print(message('usage:'), 'python3', exe_path, '%s [{%s | %s} %s] [{%s | %s} | {%s | %s}]' % (keyword('svg-path'), option('-o'), option('--output'), keyword('png-path'), option('-s'), option('--show'), option('-sa'), option('--show-all')))
    sys.exit(1)

try:
    image = renderer.render(xml.etree.ElementTree.parse(svg_path))
except:
    print(error('error:'), 'file', keyword(svg_path), 'contains syntactic errors')
    sys.exit(1)

if png_path:
    image.save(png_path)
if show_all_option:
    os.system(f'open {svg_path}')
if show_option or show_all_option:
    if png_path:
        os.system(f'open {png_path}')
    else:
        image.show()
