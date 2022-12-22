import xml.etree.ElementTree as et
from etc import checkType
from static import default_attrs, draw_tools


class SVG:
    def __init__(self):
        svg = et.Element("svg", attrib=default_attrs["svg"])
        defs = et.SubElement(svg, "defs", attrib=default_attrs["defs"])
        g_defs = et.SubElement(defs, "g", attrib=default_attrs["g"])
        surf_attr = default_attrs["g"]
        surf_attr.update({"id": "surface1"})
        g_surf = et.SubElement(svg, "g", attrib=surf_attr)
        self.main_tags = {
            "svg": svg,
            "g_defs": g_defs,
            "g_surf": g_surf,
        }
    
    def definePath(self, symbol_id, draw, overflow="visible", stroke="none"):
        # check input

        # symbol tag
        symbol_attribs = {"overflow": overflow, "id": symbol_id}
        symbol_tag = et.SubElement(self.main_tags["g_defs"], "symbol", attrib=symbol_attribs)
        # path tag
        path_attribs = {"style": f"stroke:{stroke};", "d": draw}
        et.SubElement(symbol_tag, "symbol", attrib=path_attribs)

    def usePath(self, symbol_id, x=0, y=0, fill=(0, 0, 0), stroke=None, opacity=1):
        # check input

        # g tag
        g_tag = et.SubElement(self.main_tags["g_surf"], "g")
        # use tag
        use_attribs = {
            "href":         f"#{symbol_id}", 
            "x":            f"\"{x}\"", 
            "y":            f"\"{y}\"",
            "fill":         f"rgb({fill})",
            "fill-opacity": f"\"{opacity}\"",
            "stroke":       f""
        }
    def __str__(self):
        return et.tostring(self.main_tags["svg"]).decode("utf8")

class Shape(et.Element):
    def draw(self, tool, *nums):
        # Errors
        checkType((("tool", str, tool), ("nums", (float,), nums)))
        if tool not in draw_tools:
            raise TypeError(f"tool must be one of the following: {list(draw_tools)}")\
        # Add drawing command
        if "d" not in self.attrs:
            self.attrs["d"] = ""
        self.attrs["d"] += f"{tool} {' '.join(str(num) for num in nums)} "


SVG()


# ns = "{http://www.w3.org/2000/svg}"
# xlink = "{http://www.w3.org/1999/xlink}"

# with open(svg_file_name, "r") as f:
#     svg_content = f.read()

# root = et.fromstring(bytes(svg_content, encoding="utf8"))
# symbols = root.findall(".//"+ns+"symbol")
# old_names = {symbol.attrib["id"]: [] for symbol in symbols}
# uses = root.findall(".//"+ns+"use")
# for use in uses:
#     old_names[use.attrib[xlink+"href"][1:]].append(use)


# for symbol in symbols:
#     old_name = symbol.attrib["id"]
#     with open(svg_file_name, "wb") as f:
#         symbol.attrib["id"] = ""
#         f.write(et.tostring(root))
#     new_name = input(f"Old name: {old_name}. New name: ")
#     if new_name:
#         symbol.attrib["id"] = new_name
#         for elem in old_names[old_name]:
#             elem.attrib[xlink+"href"] = f"#{new_name}"
#         with open(svg_file_name, "wb") as f:
#             f.write(et.tostring(root))
#     else:
#         symbol.attrib["id"] = old_name


