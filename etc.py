import xml.etree.ElementTree as et
from typecheck import checkType, Op, Ex, Num
from static import draw_tools, translate_tools
import numpy as np
from misc import getBezier, iteradd
import re

def reflect(x, y, cx, cy):
    return  2*cx-x, 2*cy-y

class Group:
    """
    Collection of uses
    """
    def __init__(self, *use_lst):
        checkType(
            ("use_lst", (Use,), use_lst),
        )
        self.use_lst = use_lst
    
    def getBbox(self):
        bboxes = tuple(use.bbox for use in self.use_lst)
        return np.array(
            tuple(func(mat[row,col] for mat in bboxes) for col in range(2)) \
            for row, func in enumerate((min, max))
        )
    
    def transform(self, dx=0, dy=0, transform=""):
        checkType(
            ("dx", Num(), dx),
            ("dy", Num(), dy),
            ("transform", str, transform),
        )
        for use in self.use_lst:
            use.transform(dx, dy, transform)
    
    def linearSet(self, x, y, xsep=0.1, ysep=0.1, space=10, width=None, height=None, **kwargs):
        checkType(
            ("x", Num(), x),
            ("y", Num(), y),
            ("xsep", Num(), xsep),
            ("ysep", Num(), ysep),
            ("width", Op(Num(0, None), Ex(None)), width),
            ("height", Op(Num(0, None), Ex(None)), height),
        )
        cursor = (x, y)
        baseline = x
        for use in self.use_lst:
            if isinstance(use, Use):
                width, height = use.width, use.height
                cursor = iteradd(cursor, (width+xsep, 0))
                use.set(x=cursor[0], y=cursor[1])
            elif use == " ":
                cursor = iteradd(cursor, (space, 0))
            elif use == "\n":
                cursor = iteradd(cursor, (-baseline, height+ysep))


class Use(et.Element):
    """
    Extracts necessary information from a path object and makes use tag
    """
    def __init__(self, elem, path_obj, *args, **kwargs):
        super().__init__("use", *args, **kwargs)
        elem.append(self)
        self.symbol_id = path_obj.getSymbolId()
        self.bbox = path_obj.getBbox()
        self.d_bbox = self.bbox.copy()
        self.d_width, self.d_height = (self.d_bbox[1][indx] - self.d_bbox[0][indx] for indx in range(2))
        self.width, self.height = self.d_width, self.d_height
        self.transform_mat = np.eye(3)
        self.pos_mat = np.eye(3)
        self._updateBbox()
    
    def set(self, x=None, y=None, **kwargs):
        self.attrib.update(kwargs)
        for string, variable in (("x", x), ("y", y)):
            if variable:
                self.attrib[string] = str(variable)
        self._updateBbox()
    
    def _updateBbox(self):
        has_transform = "transform" in self.attrib
        has_x_y = "x" in self.attrib and "y" in self.attrib
        if has_transform:
            transform_lst = re.split(
                "(?<=\))", 
                re.sub("\s+"," ", self.attrib["transform"])
            )
            for transform in transform_lst:
                t_info = tuple(i.strip() for i in re.split("[(,)]", transform) if i)
                t_type = t_info[0]
                t_args = tuple(float(i) for i in t_info[1:])
                self.transform_mat = translate_tools[t_type](t_args) @ self.transform_mat 
            if has_x_y:
                for row, comp in enumerate(("x", "y")):
                    self.pos_mat[row, 2] = float(self.attrib[comp])
            temp_bbox = np.eye(3)
            temp_bbox[:2, :2] = np.transpose(self.d_bbox)
            self.bbox = np.transpose((self.pos_mat @ self.transform_mat @ temp_bbox)[:2, :2])
        self._updateDims()
    
    def getBbox(self):
        return self.bbox
        
    def _updateDims(self):
        self.width, self.height = (self.bbox[1][indx] - self.bbox[0][indx] for indx in range(2))
    
    def transform(self, dx=0, dy=0, transform=""):
        for key, change in (("x",dx), ("y",dy), ("transform",transform)):
            if change:
                self.attrib[key] += change
        self._updateBbox()


class Path(et.Element):
    """
    Used to draw paths and collect path information
    """
    def __init__(self, elem, *args, **kwargs):
        # Errors
        checkType(
            ("elem", et.Element, elem),
        )
        # initialize
        if "id" in kwargs:
            self.symbol_id = kwargs.pop("id")
        super().__init__("path", *args, **kwargs)
        elem.append(self)
        for tool_name, tool in draw_tools.items():
            func = tool.func
            num_args = tool.num_args
            setattr(self, func, lambda *args: self._makeTools(num_args, tool_name, args))
        self.attrib["d"] = re.sub("\s+", " ", self.attrib["d"])

    def getD(self):
        return self.attrib["d"]
    
    def getBbox(self):
        # [[xmin, ymin], [xmax, ymax]]
        point_lst = self.getApproxPoints()
        if point_lst:
            x_vals, y_vals = (tuple(point[i] for point in point_lst) for i in range(2))
            return np.array(tuple(tuple(func(val_lst) for func in (min, max)) for val_lst in (x_vals, y_vals)))
        else:
            return np.zeros((2, 2))

    def getSymbolId(self):
        return self.symbol_id

    def getApproxPoints(self):
        points = []
        tool_letters = ''.join(draw_tools.keys())
        commands = (cmd for cmd in re.split(f"(?=[{tool_letters}])", self.getD()) if cmd)
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
                points.extend(getBezier(nums)[1:])
        return points

    def draw(self, tool, *nums):
        # Errors
        checkType(
            ("tool", Ex(*tuple(draw_tools.keys())), tool), 
            ("nums", (Op(int, float),), nums),
            (f"For tool \"{tool}\", len(nums)", Ex(draw_tools[tool].num_args), len(nums)),
        )
        # Add drawing command
        if "d" not in self.attrs:
            self.attrib["d"] = ""
        self.attrib["d"] += f"{tool} {' '.join(str(num) for num in nums)} "
    
    def _makeTools(self, num_arg, tool_name, args):
        # Errors
        checkType(
            ("num_arg", int, num_arg), 
            ("tool_name", Ex(*tuple(draw_tools.keys())), tool_name),
            ("args", Op((float, num_arg), Ex(tuple([]))), args),
        )
        return self.draw(tool_name, *args)

    def clearDraw(self):
        self.attrib["d"] = ""
