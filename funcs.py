from etc import draw_tools
import re
import numpy as np
import xml.etree.ElementTree as et
from typecheck import checkType, Num, Array, Op, Ex, Callable

re.count = lambda pattern, string: len(re.findall(pattern, string))

def setAttribs(elem, **kwargs):
    """Set multiple attributes with one function"""
    checkType(
        ("elem", et.Element, elem),
        ("kwargs", {str: str}, kwargs)
    )
    for key, value in kwargs.items():
        elem.set(key, value)

def reflect(x, y, cx, cy):
    """Get reflection of point (x,y) about center point (cx, cy)"""
    checkType(
        ("x", Num(), x),
        ("y", Num(), y),
        ("cx", Num(), cx),
        ("cy", Num(), cy),
    )
    return  2*cx-x, 2*cy-y

def getTransforms(self, transform_string):
    transform_lst = re.split(
                "(?<=\))", 
                re.sub("\s+"," ", self.attrib["transform"])
            )
    transform_lst = (i for i in transform_lst if i)

def getPointsFromD(d, steps=101):
    """
    Convert `d` attribute from SVG `path` tag to an approximate list of points
    """
    points = []
    tool_letters = ''.join(draw_tools.keys())
    commands = (cmd for cmd in re.split(f"(?=[{tool_letters}])", d) if cmd)
    current_point, prev_ctrl = (0, 0), None
    for command in commands:
        args = command.strip().split(" ")
        tool_letter = args[0]
        is_rel = tool_letter.islower()
        nums = tuple(float(i) for i in args[1:])
        # H or V: one arg
        if tool_letter.lower() == "h":
            current_point = iteradd(current_point, (nums[0], 0)) if is_rel else (nums[0], current_point[1])
            prev_ctrl = None
            points.append(current_point)
        elif tool_letter.lower() == "v":
            current_point = iteradd(current_point, (0, nums[0])) if is_rel else (current_point[0], nums[1])
            prev_ctrl = None
            points.append(current_point)
        # M or L: two args
        elif tool_letter.lower() in ("m", "l"): 
            current_point = iteradd(current_point, nums) if is_rel else nums
            prev_ctrl = None
            points.append(current_point)
        # T, Q, S or C (beziers): 2, 4 or 6 args
        elif tool_letter.lower() in ("t", "q", "s", "c"):
            nums = iteradd(nums, current_point) if is_rel else nums
            if tool_letter.lower() in ("t", "s"):
                nums = nums[:2] + \
                        reflect(prev_ctrl, current_point) if prev_ctrl else current_point + \
                        nums[:2]
            current_point = nums[-2:]
            prev_ctrl = nums[-4:-2]
            nums = tuple(zip(nums[::2], nums[1::2]))
            points.extend(getBezier(nums, steps=steps)[1:])
    return points

def getBezier(corners, steps=101):
    """
    Get a `steps`-long sequence of bezier points from given `corners`.
    Uses adjusted code from https://stackoverflow.com/a/2292690/13597979
    """
    corner_types = ((Num(),2),)
    checkType(
        ("corners", corner_types, corners),
        ("steps", int, steps),
    )
    n = len(corners) - 1
    combinations, points, x, numerator = [1], [], 1, n
    for denominator in range(1, n // 2 + 1):
        combinations.append(x * numerator / denominator)
        numerator -= 1
    combinations.extend(reversed(combinations[:-1 if not n % 2 else None]))
    for t in np.linspace(0, 1, steps):
        tpowers = (t**i for i in range(n+1))
        upowers = reversed([(1-t)**i for i in range(n+1)])
        coefs = [c*a*b for c, a, b in zip(combinations, tpowers, upowers)]
        points.append(tuple(sum([coef*p for coef, p in zip(coefs, ps)]) for ps in zip(*corners)))
    return points

def iterop(iter1, iter2, op):
    """
    perform operations on tuples, lists and dictionaries.
    len(iter1) must be multiple of len(iter2)
    """
    # check iterables
    NUM = Op(int, float)
    op_str = Ex("add", "sub", "mult", "div")
    checkType(
        ("iter1", Op((NUM,), [NUM,]), iter1),
        ("iter2", Op((NUM,), [NUM,], NUM), iter2),
        ("op", Op(Ex("add", "sub", "mult", "div"), Callable()), op)
    )
    if op in op_str:
        indx = op_str.index(op)
        op = (lambda a, b: a + b, lambda a, b: a - b, lambda a, b: a * b, lambda a, b: a / b)[indx]
    if isinstance(iter2, (int, float)):
        return type(iter1)(op(i, iter2) for i in iter1)
    elif not len(iter1) % len(iter2) and len(iter1) and len(iter2):
        num_repeats = int(len(iter1) / len(iter2))
        return type(iter1)(op(j, k) for j, k in zip(iter1, iter2 * num_repeats))
    else:
        raise TypeError("If using lists or tuples, len(iter1) must be multiple of len(iter2), and both positive.")
             
def iteradd(x, y):
    return iterop(x, y, "add")

def getBbox(points):
    """Convert list of 2-tuples or list of bboxes to [[xmin ymin],[xmax ymax]]"""
    type1 = [(Num(),2),]
    type2 = (Array(2,2),)
    checkType(
        (points, Op(type1, type2), points)
    )
    if points:
        x_vals, y_vals = (tuple(point[i] for point in points) for i in range(2))
        return np.array(tuple(tuple(func(val_lst) for val_lst in (x_vals, y_vals)) for func in (min, max)))
    else:
        return np.zeros((2, 2))

def getDims(bbox):
    checkType("bbox", Array(2,2), bbox)
    return (bbox[1][indx] - bbox[0][indx] for indx in range(2))

def getCloseBracket(string, brackets, start_indx):
    checkType(
        ("string", str, string),
        ("brackets", (str, 2), brackets),
        ("start_indx", int, start_indx),
    )
    open_bracket, close_bracket = brackets
    depth, indx = 1, start_indx
    while depth:
        open_indx, close_indx = \
            (string.find(bracket, indx+1) for bracket in (open_bracket, close_bracket))
        if open_indx < 0 or close_indx < open_indx:
            depth -= 1
            indx = close_indx
        elif close_indx < 0 or open_indx < close_indx:
            depth += 1
            indx = open_indx
    return indx + 1

def getArgs(string):
    pipes = tuple(i.start() for i in re.finditer("\|", string))
    top_level_pipes = []
    for indx in pipes:
        render_brackets = ("\"", "$", "`")
        all_render_brackets = tuple(f"(?<!{bracket})" + bracket*num + f"(?!{bracket})" \
                                for bracket in render_brackets for num in range(1,4))
        other_brackets = (("[", "]"), ("{", "}"))
        if not any(re.count(bracket_regex, string[:indx]) % 2 for bracket_regex in all_render_brackets) and \
            all(string[:indx].count(brac[0]) == string[:indx].count(brac[1]) for brac in other_brackets):
                top_level_pipes.append(indx)
    return tuple(string[i:j] for i, j in zip([None]+top_level_pipes, top_level_pipes+[None]))

def getMathObj(string):
    checkType("string", str, string)
    string = string.strip()
    pattern = f"\\\\[A-Za-z][A-Za-z0-9]*"
    cmnd_indices = {i.start(): i.end() for i in re.finditer(pattern, string)}
    i = 0
    math_obj = []
    while i < len(string):
        if i in cmnd_indices:
            new_i = cmnd_indices[i]
            math_block = {"name": string[i+1: new_i]}
            for brackets, key in ((("[", "]"), "options"), (("{", "}"), "contents")):
                if string[new_i] == brackets[0]:
                    end = getCloseBracket(string, brackets, new_i)
                    args = string[new_i: end]
                    new_i = end
                    math_block[key] = 1 # TODO
        math_obj.append(math_block)
            


            


practice_str = "\\sum^n_{i=5} abcdne^n + (1 + 2)^2 + x\\alpha\\beta e^{10x}\\log_10(50)/\\ln(e)" \
            " - x^2 - 5x^4 +5*3 + \\edef[waw | elem=1 | sys='uh oh' | bah=[1|1|2]]" \
            " - \\enef{ Wakka wakka | nakka nakka } + \\frac{1 | 2} - \\beh[1 | tik]{uhh}" \
            " \\underbrace{ 111e^5}_{\"A $\\beta$ thing\"}"
getMathObj(practice_str)