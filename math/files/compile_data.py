import xml.etree.ElementTree as et

svg_file_name = r"/Users/miles/Desktop/Vectopy/math/files/math_symbols_work.svg"

ns = "{http://www.w3.org/2000/svg}"
xlink = "{http://www.w3.org/1999/xlink}"

with open(svg_file_name, "r") as f:
    svg_content = f.read()

root = et.fromstring(bytes(svg_content, encoding="utf8"))
doc_symbols = root.findall(".//"+ns+"symbol")
symbols = {}

for doc_symbol in doc_symbols:
    name = doc_symbol.attrib["id"]
    data = doc_symbol.find(ns+"path").attrib["d"]
    symbols[name] = data

with open("symbols.py", "w") as f:
    f.write(str(symbols))

