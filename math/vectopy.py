import xml.etree.ElementTree as et
from error import checkInput
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
    
    def definePath(self):
        pass

    def usePath(self):
        pass
    
    def __str__(self):
        return et.tostring(self.main_tags["svg"], pretty_print=True).decode("utf8")

class Shape(et.Element):
    def draw(self, tool, *nums):
        # Errors
        checkInput((("tool", str, tool), ("nums", (float,), nums)))
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
#         f.write(et.tostring(root, pretty_print=True))
#     new_name = input(f"Old name: {old_name}. New name: ")
#     if new_name:
#         symbol.attrib["id"] = new_name
#         for elem in old_names[old_name]:
#             elem.attrib[xlink+"href"] = f"#{new_name}"
#         with open(svg_file_name, "wb") as f:
#             f.write(et.tostring(root, pretty_print=True))
#     else:
#         symbol.attrib["id"] = old_name


