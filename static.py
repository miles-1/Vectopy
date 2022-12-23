from dataclasses import dataclass
from math import sin, cos, tan
import numpy as np
import json


with open("symbols.json") as f:
    full_symbols_dict = json.load(f)


default_attrs = {
    "svg": {
        "xmlns": "http://www.w3.org/2000/svg",
        "version": "1.1",
    },
    "defs" : {},
    "g" : {},
    "symbol" : {"overflow": "visible"},
    "use" : {},
    "path" : {"stroke": "none"},
    "ellipse" : {},
    "image" : {},
    "line" : {},
    "polygon" : {},
    "polyline" : {},
    "rect" : {},
    "marker" : {},
}


@dataclass
class _Tool:
    num_args: int
    func: str

draw_tools = {
    # tool: (num_args, func name)
    # smooth = using reflection of prev ctrl pt, or current point if none
    "Z": _Tool(0, "closePath"),         # Close Path: None
    "H": _Tool(1, "hLineTo"),           # Horizontal line to (draws): (x,)
    "h": _Tool(1, "hLineRel"),          # Horizontal line to, relative (draws): (dx,)
    "V": _Tool(1, "vLineTo"),           # Vertical line to (draws): (y,)
    "v": _Tool(1, "vLineRel"),          # Vertical line to, relative (draws): (dy,)
    "L": _Tool(2, "lineTo"),            # Line to (draws): (x,y)
    "l": _Tool(2, "lineRel"),           # Line to, relative (draws): (dx,dy)
    "M": _Tool(2, "moveTo"),            # Move to (doesn't draw): (x,y)
    "m": _Tool(2, "moveRel"),           # Move to, relative (doesn't draw): (dx,dy)
    "T": _Tool(2, "sQuadBezTo"),        # Smooth quadratic curve (bezier) to: (x, y)
    "t": _Tool(2, "sQuadBezRel"),       # Smooth quadratic bez to, relative: (dx, dy)
    "Q": _Tool(4, "quadBezTo"),         # Quadratic bez to: (cpx, cpy, x, y)
    "q": _Tool(4, "quadBezRel"),        # Quadratic bez to, relative: (dcpx, dcpy, dx, dy)
    "S": _Tool(4, "sCubeBezTo"),        # Smooth cubic bez to: (cpx2, cpy2, x, y)
    "s": _Tool(4, "sCubeBezRel"),       # Smooth cubic bez to, relative: (dcpx2, dcpy2, x, y)
    "C": _Tool(6, "cubeBezTo"),         # Cubic bez to: (cpx1, cpy1, cpx2, cpy2, x, y)
    "c": _Tool(6, "cubeBezRel"),        # Cubic bez to, relative: (dcpx1, dcpy1, dcpx2, dcpy2, dx, dy)
    # "A": _Tool(5, "arc"), # Arc: (x1, y1, x2, y2, radius)
}

end_row = (0, 0, 1)

translate_tools = {
    # tool: lambda to get matrix args
    "matrix":    lambda *x: np.array((x[:3], x[3:], end_row)),
    "translate": lambda tx, ty=0: np.array(((1, 0, tx), (0, 1, ty), end_row)),
    "scale":     lambda sx, sy=0: np.array(((sx, 0, 0), (0, sy, 0), end_row)),
    "rotate":    lambda a, cx=0, cy=0: np.array((
                        (cos(a), -sin(a), cx * (1 - cos(a)) + cy * sin(a)),
                        (sin(a), cos(a), cy * (1 - cos(a)) - cx * sin(a)),
                        end_row)),
    "skewX":     lambda a: np.array(((1, tan(a), 0), (0, 1, 0), end_row)),
    "skewy":     lambda a: np.array(((1, 0, 0), (tan(a), 1, 0), end_row)),
}