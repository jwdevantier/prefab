"""
Provide ability to walk (& thus apply a transformation) to all
elements of a nested data structure.

Inspired by Clojure.walk (src/clj/clojure/walk.clj)
"""
def __identity(x):
    """identity function, returns its input."""
    return x

def _walk_dict(inner, outer, dct):
    """Apply 'inner' to all dictionary keys & values, apply 'outer' to resulting dict."""
    return outer({inner(k): inner(v) for (k, v) in dct.items()})

def _walk_list(inner, outer, lst):
    """Apply 'inner' to all list elements, apply 'outer' to the resulting list."""
    return outer([inner(v) for v in lst])

def _walk_tuple(inner, outer, tpl):
    """Apply 'inner' to all tuple elements, apply 'outer' to the resulting tuple."""
    return outer(tuple([inner(v) for v in tpl]))

def _walk_set(inner, outer, s):
    """Apply 'inner' to all set elements, apply 'outer' to the resulting set."""
    return outer({inner(v) for v in s})

def _walk_leaf(_, outer, leaf):
    """walk leaf element."""
    return outer(leaf)


def _walk(inner, outer, elem):
    """Function which dispatches to a concrete walk function depending on element type.

    Default walk function used in prewalk/postwalk - reimplement/wrap to support custom types.
    """
    if isinstance(elem, list):
        return _walk_list(inner, outer, elem)
    elif isinstance(elem, tuple):
        return _walk_tuple(inner, outer, elem)
    elif isinstance(elem, dict):
        return _walk_dict(inner, outer, elem)
    elif isinstance(elem, set):
        return _walk_set(inner, outer, elem)
    else:
        return _walk_leaf(inner, outer, elem)

def prewalk(fun, elem, walkfn=_walk):
    """Perform pre-order, depth-first traversal of the datastructure 'elem'."""
    inner = lambda elem: prewalk(fun, elem, walkfn)
    return walkfn(inner, __identity, fun(elem))

def postwalk(fun, elem, walkfn=_walk):
    """Perform post-order, depth-first traversal of the datastructure 'elem'."""
    inner = lambda elem: postwalk(fun, elem, walkfn)
    return walkfn(inner, fun, elem)
