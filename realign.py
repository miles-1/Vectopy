from funcs import getPointsFromD
from json import load, dump

def reflect(x, y, cx, cy):
    return  2*cx-x, 2*cy-y

with open("symbols_align.json") as f:
    j = load(f)

for symbol, d in j.items():
    getPointsFromD(d)