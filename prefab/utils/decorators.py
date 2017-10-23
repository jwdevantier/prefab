"""
Decorators of a general nature
"""
from functools import wraps

class RunOnceArgsChangedError(Exception):
    """Raised in the event that a @run_once function is subsequently invoked with different args."""
    def __init__(self, fn, orig_args, new_args, orig_kwargs, new_kwargs):
        self._fn = fn
        self._orig_args = orig_args
        self._orig_kwargs = orig_kwargs
        self._new_args = new_args
        self._new_kwargs = new_kwargs

    @property
    def fn_name(self):
        return self._fn.__name__

    @property
    def orig_args(self):
        return self._orig_args

    @property
    def orig_kwargs(self):
        return self._orig_kwargs

    @property
    def new_args(self):
        return self._new_args

    @property
    def new_kwargs(self):
        return self._new_kwargs

def run_once(skip_exc=False):
    """Annotate function to ensure it is run exactly once."""
    def decorator(fn):
        def wrapper(*args, **kwargs):
            if hasattr(wrapper, 'has_run'):
                if args != wrapper.args or kwargs != wrapper.kwargs:
                    raise RunOnceArgsChangedError(fn, wrapper.args, args, wrapper.kwargs, kwargs)
                return wrapper.result

            # first (& only) invocation
            if not skip_exc:
                wrapper.has_run = True

            wrapper.args = args
            wrapper.kwargs = kwargs
            wrapper.result = fn(*args, **kwargs)
            wrapper.has_run = True
            return wrapper.result
        return wrapper
    return decorator

class lazyprop:
    """wrap around a function to define a lazy property."""
    def __init__(self, propfn):
        print("asddsa")
        self._propfn = propfn

    def __get__(self, parent, parentcls):
        print("GET")
        value = self._propfn(parent)
        setattr(parent, self._propfn.__name__, value)
        return value

def prop(name, thunk):
    def decorator(fn):
        setattr(fn, name, lazyprop(thunk))
        return fn
    return decorator


#def myprop(name, thunk):
#    attr_name = '_lazy_' + name
#    def decorator(target):
#        setattr(target, name, lazyprop(thunk))
#        return target