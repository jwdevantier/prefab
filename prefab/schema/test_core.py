"""
Test module for schema code.
"""
import pytest
from voluptuous import Schema
from voluptuous.error import MultipleInvalid, Invalid
from .core import seqof, dictof, KeyInvalid, pred

# seqof Tests
##############

# Ensure compliant sequences are tolerated
@pytest.mark.parametrize("data", [
    [1, 2, 3], [5, 1, 1337]
])
def test_seqof_ok(data):
    s = Schema(seqof(int))
    assert s(data) == data

# Ensure empty sequences are tolerated
@pytest.mark.parametrize("data", [
    [], tuple()
])
def test_seqof_ok_empty(data):
    """Ensure empty sequences are accepted."""
    s = Schema(seqof(int))
    assert s(data) == data

@pytest.mark.parametrize("data", [
    {}, set(), "hello", 2
])
def test_seqof_err_type(data):
    s = Schema(seqof(str))
    with pytest.raises(Invalid) as exc:
        s(data)
    assert 'expected sequence' in str(exc.value)

# Ensure errors are detected & that first reported error
# matches with the first element which failed the schema check
@pytest.mark.parametrize("data,err_fragment", [
    ([1, 2], '@ data[0]'),
    (["hello", 1, "w"], '@ data[1]'),
    (["hi", "hey", 3, "what"], '@ data[2]')
])
def test_seqof_err_elem_type(data, err_fragment):
    """Ensure erroneous element(s) are detected."""
    s = Schema(seqof(str))
    with pytest.raises(Invalid) as exc:
        s(data) == data
    assert err_fragment in str(exc.value)


# dictof Tests
##############

def test_dictof_ok_empty():
    data = {}
    s = Schema(dictof(str, int))
    assert s(data) == data

@pytest.mark.parametrize("data", [
    tuple(), set(), [], "hello", 2
])
def test_dictof_err_type(data):
    """Ensure non-dictionary values are caught."""
    s = Schema(dictof(str,int))
    with pytest.raises(Invalid) as exc:
        s(data)
    assert 'expected dict' in str(exc.value)

def test_dictof_ok_elems():
    """Ensure valid dictionary value pass through."""
    s = Schema(dictof(str, int))
    data = {'one': 1, 'two': 2, 'three': 3}
    assert s(data) == data

def test_dictof_err_val():
    """Ensure invalid value(s) are detected."""
    s = Schema(dictof(str, int))
    data = {'one': 1, 'two': "sd", 'three': 3}
    with pytest.raises(Invalid) as exc:
        s(data)
    assert "@ data['two']" in str(exc.value)

def test_dictof_err_key():
    """Ensure invalid key(s) are detected (KeyInvalid)"""
    s = Schema(dictof(str, int))
    data = {'one': 1, 'two': 2, 3: 3}
    with pytest.raises(MultipleInvalid) as exc:
        s(data)
    assert isinstance(exc.value.errors[0], KeyInvalid)

@pytest.mark.parametrize("retval", [
    False, None, tuple(), set(), []
])
def test_pred_falsy(retval):
    """Ensure pred wrapper propegates failure."""
    def __myfn(_):
        return retval
    s = Schema(pred(__myfn))
    data = 1337
    with pytest.raises(Invalid):
        s(data)

@pytest.mark.parametrize("retval", [
    True, 1, "hello", 3.14
])
def test_pred_truthy(retval):
    """Ensure pred wrapper propegates failure."""
    def __myfn(_):
        return retval
    s = Schema(pred(__myfn))
    data = 1337
    assert s(data) == data