import lxml.etree as et

svg_file_name = r"C:/Users/miles/Desktop/vectopy/math/files/math_symbols_work.svg"

ns = "{http://www.w3.org/2000/svg}"
xlink = "{http://www.w3.org/1999/xlink}"

with open(svg_file_name, "r") as f:
    svg_content = f.read()

root = et.fromstring(bytes(svg_content, encoding="utf8"))
symbols = root.findall(".//"+ns+"symbol")
old_names = {symbol.attrib["id"]: [] for symbol in symbols}
uses = root.findall(".//"+ns+"use")
for use in uses:
    old_names[use.attrib[xlink+"href"][1:]].append(use)


for symbol in symbols:
    old_name = symbol.attrib["id"]
    with open(svg_file_name, "wb") as f:
        symbol.attrib["id"] = ""
        f.write(et.tostring(root, pretty_print=True))
    new_name = input(f"Old name: {old_name}. New name: ")
    if new_name:
        symbol.attrib["id"] = new_name
        for elem in old_names[old_name]:
            elem.attrib[xlink+"href"] = f"#{new_name}"
        with open(svg_file_name, "wb") as f:
            f.write(et.tostring(root, pretty_print=True))
    else:
        symbol.attrib["id"] = old_name

