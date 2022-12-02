# SVG renderer

This project implements a CLI for rendering an SVG to a PNG image. You can test it using the SVGs in the `examples` directory.

## Dependencies

```sh
pip install colorama Pillow
```

## Usage

```sh
python3 exe-path svg-path [{-o | --output} png-path] [{-s | --show} | {-sa | --show-all}]
```

The `--show[-all]` option tells the program whether it should open the file(s) after rendering or not.

## Author

Iulian Oleniuc (3B3)
