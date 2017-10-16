"""
Test module for walk code.
"""
from collections import OrderedDict
import pytest
from .walk import prewalk, postwalk

def identity(x):
    """Identity function, returns its input value."""
    return x

def inc(x):
    """Increment input value by 1."""
    return x + 1


@pytest.mark.parametrize("data", [
    1, 3.14, "hello", None, False,
])
def test_walk_leaf(data):
    assert prewalk(identity, data) == data
    assert postwalk(identity, data) == data

@pytest.mark.parametrize("data", [
    1, 3.14
])
def test_walk_leaf_inc(data):
    assert prewalk(inc, data) == (data + 1)
    assert postwalk(inc, data) == (data + 1)

@pytest.mark.parametrize("data", [
    [1,2,3], (1,2,4), [], ()
])
def test_walk_seqs(data):
    def myinc(x):
        if isinstance(x, (int, float)):
            return x + 1
        return x
    def mapinc(data):
        res = [myinc(v) for v in data]
        if isinstance(data, tuple):
            return tuple(res)
        return res
    assert prewalk(myinc, data) == mapinc(data)
    assert postwalk(myinc, data) == mapinc(data)

@pytest.mark.parametrize("data", [
    set(), {1}, {1, 1}, {1, 2, 3, 4, 2}
])
@pytest.mark.parametrize("walkfn", [prewalk, postwalk])
def test_walk_sets(data, walkfn):
    def myinc(x):
        if isinstance(x, (int, float)):
            return x + 1
        return x
    assert walkfn(myinc, data) == {myinc(x) for x in data}

@pytest.mark.parametrize("data", [
    {}, {'one': 1}, {'four': 4, 'five': 5}
])
@pytest.mark.parametrize("walkfn", [prewalk, postwalk])
def test_walk_dicts_xform_vals(data, walkfn):
    def myinc(x):
        if isinstance(x, (int, float)):
            return x + 1
        return x
    assert walkfn(myinc, data) == {k: myinc(v) for (k, v) in data.items()}

@pytest.mark.parametrize("data", [
    {}, {'one': 1}, {'four': 4, 'five': 5}
])
@pytest.mark.parametrize("walkfn", [prewalk, postwalk])
def test_walk_dicts_xform_keys(data, walkfn):
    def exclaim(x):
        if isinstance(x, str):
            return x + "!"
        return x
    assert walkfn(exclaim, data) == {exclaim(k): v for (k, v) in data.items()}


@pytest.mark.parametrize("walkfn,data,order", [
    (
        prewalk,
        ["one", "two"],
        [["one", "two"], "one", "two"]
    ),
    (
        postwalk,
        ["one", "two"],
        ["one", "two", ["one", "two"]]
    )
])
def test_walk_order(walkfn, data, order):
    """
    Test order in which nodes are visited.
    
    """
    observed = []
    def observe(x):
        observed.append(x)
        return x
    walkfn(observe, data)
    assert observed == order
