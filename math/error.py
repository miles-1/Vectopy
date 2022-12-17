import numpy as np

def checkInput(info_tuple):
    """
    info_tuple structure:
    (
        (<expectedType>, <actual>),
        # or ...
        ("argName", <expectedType>, <actual>),
    )

    The following are shortcuts for expected type:

    {<Type1>: <Type2>} # Dictionary with keys of type Type1 and values of Type2
    (<Type>,)          # Tuple of elements of type Type
    [<Type>]           # List of elements of type Type
    nd.array([<Type>]) # np array of elements of type Type
    (<Type1>, <Type2>) # obj of type Type1 or Type2
    """
    error_msg = None
    if not isinstance(info_tuple[0], tuple):
        info_tuple = tuple(info_tuple)
    if len(info_tuple[0]) == 2:
        info_tuple = tuple(tuple(None, a, b) for a, b in info_tuple)
    for param_name, expd_type, actual in info_tuple:
        if isinstance(expd_type, (tuple, list, dict, np.ndarray)) \
        and len(expd_type) == 1:
            expd_outer = type(expd_type)
            expd_inner = list(expd_type.items())[0] if expd_outer == dict else tuple(expd_type)
            if type(actual) != expd_outer or \
            (type(actual) == "dict" and not \
            all(all(map(isinstance, list(actual)[i], expd_inner)) for i in range(len(actual)))) or \
            not all(isinstance(entry, expd_inner[0]) for entry in actual):
                
                inner_types = \
                " : ".join(
                    (", ".join(elem.__name__ for elem in pos_type) \
                        if isinstance(pos_type, tuple) else pos_type.__name__) \
                    for pos_type in expd_inner
                )
                error_msg = f"Expected type {expd_outer.__name__}, with inner type(s) {inner_types}."
        elif isinstance(expd_type, tuple) and len(expd_type) and not isinstance(actual, expd_type):
            inner_types = ', '.join(elem.__name__ for elem in expd_type)
            error_msg = f"Expected one of these types: {inner_types}."
        elif not isinstance(actual, expd_type):
            error_msg = f"Expected type {expd_type}."
        if error_msg:
            if param_name:
                error_msg = f"Bad input for parameter \"{param_name}\". {error_msg}"
            raise TypeError(error_msg)