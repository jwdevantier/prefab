"""
Core functionality for augmenting voluptuous schemas.
"""
from voluptuous.error import MultipleInvalid, Invalid, DictInvalid, ValueInvalid
from voluptuous import Schema, All, Length, ALLOW_EXTRA
from voluptuous.humanize import humanize_error

def seqof(validator):
    """Validate all elements in sequence against provided validator.
    
    NOTE: while callables can be validators, know that they must raise
    an 'Invalid' exception to register as failed."""
    if not isinstance(validator, Schema):
        validator = Schema(validator)

    def __inner(input):
        if not isinstance(input, (tuple, list)):
            raise Invalid("expected sequence")
        errs = MultipleInvalid()
        result = []
        for ndx, elem in enumerate(input):
            try:
                result.append(validator(elem))
            except Invalid as exc:
                exc.path.append(ndx)
                errs.add(exc)
        if errs.errors:
            raise errs
        if isinstance(input, tuple):
            result = tuple(result)
        return result
    return __inner

def non_empty(schema):
    """Stipulate that schema must contain a non-empty value.

    Note: uses Voluptuous.Length, will work with tuples, lists, strings and the like
    """
    return All(schema, Length(min=1))

def mapping(dct, **kwargs):
    """Map keys to values, yielding a schema with which to check dictionaries.

    NOTE: use because the default strategy in voluptuous (error'ing)
    """
    if not isinstance(dct, dict):
        raise ValueError("'dct': must be a dictionary")
    if kwargs.pop('extra', False):
        raise ValueError(
            "you MUST not use the 'extra' keyword - these "
            "policies lead to errors and ruin schema composition")
    return Schema(dct, **kwargs, extra=ALLOW_EXTRA)

def __schema_validate(validator, val):
    try:
        return (validator(val), None)
    except Invalid as exc:
        return (None, exc)

class KeyInvalid(Invalid):
    """Key value was found invalid by validator."""

def __wrap_err(WrapperType, err):
    if not isinstance(err, Invalid):
        raise ValueError("expected an instance of voluptuous.error.Invalid")
    msg = err.msg
    wrapped = WrapperType(err.msg)
    #equivalent to 'raise ... from cause_exc', see PEP3134
    wrapped.__cause__ = err 
    return wrapped

def dictof(key_validator, value_validator):
    """Validate entries against key & value validators
    
    NOTE: while callables can be validators, know that they must raise
    an 'Invalid' exception to register as failed."""
    if not isinstance(key_validator, Schema):
        key_validator = Schema(key_validator)
    if not isinstance(value_validator, Schema):
        value_validator = Schema(value_validator)

    def __inner(dct):
        if not isinstance(dct, dict):
            raise DictInvalid("expected dict")
        errs = MultipleInvalid()
        result = {}
        for k, v in dct.items():
            key, key_err = __schema_validate(key_validator, k)
            val, val_err = __schema_validate(value_validator, v)
            if not (key_err or val_err):
                result[key_validator(key)] = value_validator(val)
            else:
                if key_err:
                    # wrap in KeyInvalid to aid distinction
                    # between key- and value errors
                    err = __wrap_err(KeyInvalid, key_err)
                    errs.add(err)
                if val_err:
                    val_err.path.append(k)
                    errs.add(val_err)
        if errs.errors:
            raise errs
        return result
    return __inner

def pred(predfn, msg=None):
    """Generate validator fn which checks if a given value satisfies the supplied predicate function."""
    msg = msg or "predicate '{0}' failed".format(predfn.__name__)
    def _inner(val):
        if not predfn(val):
            raise ValueInvalid(msg)
        return val
    return _inner

def valid(schema, data):
    """Validate data against schema, True iff data conforms - False otherwise."""
    try:
        schema(data)
        return True
    except Invalid:
        return False

def explain(schema, data):
    """Explain why schema validation fails iff it fails, pass-through otherwise."""
    try:
        schema(data)
    except Invalid as exc:
        print(humanize_error(data, exc))