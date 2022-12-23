import xml.etree.ElementTree as et
from typecheck import checkType, Op, Ex, Any
from static import default_attrs, full_symbols_dict
from etc import Path, Symbol, Group


class SVG:
    def __init__(self, width=200, height=100, viewbox=None):
        # check types
        checkType(
            ("width", Op(int, float), width),
            ("height", Op(int, float), height),
            ("viewbox", Op(Ex(None), str), viewbox)
        )
        if viewbox:
            if not all(i.replace("-","").replace(".","").isnum() for i in viewbox.split(" ")):
                raise TypeError("viewbox must be a string of four numbers separated by spaces")
        else:
            viewbox = f"0 0 {width} {height}"
        width, height = (f"{dim}pt" for dim in (width, height))
        # make document structure
        svg_attribs, defs_attribs, g_attribs = \
            (default_attrs[key] for key in ("svg","defs","g"))
        svg_attribs["width"], svg_attribs["height"], svg_attribs["viewBox"] = \
            width, height, viewbox
        svg = et.Element("svg", attrib=svg_attribs)
        defs = et.SubElement(svg, "defs", attrib=defs_attribs)
        g_defs = et.SubElement(defs, "g", attrib=g_attribs)
        g_attribs.update({"id": "surface1"})
        g_surf = et.SubElement(svg, "g", attrib=g_attribs)
        self.main_tags = {
            "svg": svg,
            "g_defs": g_defs,
            "g_surf": g_surf,
        }
        # prepare resources
        self.full_symbols_dict = full_symbols_dict
        self.defined_symbols = {}
    
    def defPath(self, symbol_id, draw="", overflow="visible", stroke="none"):
        # check input
        checkType(
            ("symbol_id", str, symbol_id),
            ("draw", str, draw),
            ("overflow", str, overflow),
            ("stroke", str, stroke)
        )
        if symbol_id in self.defined_symbols:
            raise ValueError(f"Symbol id {symbol_id} already in use.")
        elif symbol_id in self.full_symbols_dict and draw:
            raise ValueError(f"New draw instructions for symbol id {symbol_id} would override built-in symbol of the same name.")
        elif symbol_id in self.full_symbols_dict:
            draw = self.full_symbols_dict[symbol_id]
        # symbol tag
        symbol_attribs = {"overflow": overflow, "id": symbol_id}
        symbol_tag = et.SubElement(self.main_tags["g_defs"], "symbol", attrib=symbol_attribs)
        # path tag
        path_attribs = {"style": f"stroke:{stroke};", "d": draw}
        path = Path(symbol_tag, attrib=path_attribs, id=symbol_id)
        self.defined_symbols[symbol_id] = path
        return path
    
    def defPaths(self, symbol_dict, overflow="visible", stroke="none"):
        # check input
        checkType(
            ("symbol_dict", {str: str}, symbol_dict),
            ("overflow", str, overflow),
            ("stroke", str, stroke)
        )
        if not all(symbol_dict.values()):
            raise TypeError("All values of symbol_dict must have drawing instructions.")
        # make paths
        return {symbol_id: self.defPath(symbol_id, draw, overflow=overflow, stroke=stroke) \
            for symbol_id, draw in symbol_dict.items()}

    def usePath(self, symbol_id, x=0, y=0, fill=(0, 0, 0), stroke=0, opacity=1, **kwargs):
        # check input
        checkType(
            ("symbol_id", str, symbol_id),
            ("x", Op(int, float), x),
            ("y", Op(int, float), y),
            ("fill", (int, 3), fill),
            ("stroke", Op(int, float), stroke),
            ("opacity", Op(int, float), opacity),
        )
        if symbol_id not in self.defined_symbols:
            if symbol_id in self.full_symbols_dict:
                self.defPath(symbol_id)
            else:
                raise ValueError(f"Symbol id {symbol_id} has not been defined.")
        # g tag
        g_tag = et.SubElement(self.main_tags["g_surf"], "g")
        # use tag
        use_attribs = {
            "href":         f"#{symbol_id}", 
            "x":            f"{x}", 
            "y":            f"{y}",
            "fill":         f"rgb{fill}",
            "fill-opacity": f"{opacity}",
            "stroke":       f"{stroke}",
        }
        use_attribs.update(kwargs)
        return Use(g_tag, attrib=use_attribs)
    
    def usePaths(self, symbol_dict):
        # check input
        checkType("symbol_dict", {str: {str: Any()}}, symbol_dict)
        return {symbol_id: self.usePath(symbol_id, **attribs) \
            for symbol_id, attribs in symbol_dict.items()}
    
    def displaySymbols(self, symbol_id=None, show_handles=False, cursor=(5,5), rowsep=0, **kwargs):
        # check input
        checkType(
            ("symbol_id", Op(Ex(None), str), symbol_id),
            ("show_handles", bool, show_handles),
            ("cursor", (Op(int, float),), cursor),
            ("rowsep", Op(int, float), rowsep),
            ("kwargs", {str: str}, kwargs),
        )
        if symbol_id:
            if symbol_id not in self.defined_symbols:
                raise ValueError(f"Symbol id {symbol_id} not defined.")
        else:
            for i, (i_id, i_path) in enumerate(self.defined_symbols.items()):
                i_cursor = (cursor[0]+rowsep, cursor[1])
                self.displaySymbols(i_id, show_handles=show_handles, )
        self.usePath(symbol_id)

    def addText(self, text, x=0, y=0, xsep=0, ysep=0, \
                width=None, height=None, align="left", **kwargs):
        # check input
        checkType(
            ("text", str, text),
            ("x", Op(int, float), x),
            ("y", Op(int, float), y),
            ("xsep", Op(int, float), xsep),
            ("ysep", Op(int, float), ysep),
            ("width", Op(int, float), width),
            ("height", Op(int, float), height),
            ("align", Ex("left","right","center","justify"), align),
            ("kwargs", {str: str}, kwargs)
        )
        if width or height:
            pass # TODO: fix xsep and ysep etc etc
        cursor = (x, y)
        lines = text.split("\n")
        for line in lines:
            # TODO: define all required symbols, get bboxes
            for char in line:
                if char.isalnum():
                    pass # TODO: use letter, move cursor
                elif char == " ":
                    pass # TODO: add horizontal space to cursor
            pass # TODO: add vertical space to cursor (alignment sensitive)


    def __str__(self):
        return et.tostring(self.main_tags["svg"]).decode("utf8")
    
    def save(self, filename):
        with open(filename, "w") as f:
            f.write(str(self))





# svg = SVG(height=700)
# svg.usePaths(
#     {symbol: {"x":5, "y":num*10+5} \
#         for num, symbol in enumerate(svg.full_symbols_dictionary.keys())}
# )
# svg.save("test.svg")