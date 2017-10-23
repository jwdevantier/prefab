from . fabcompat import initialize, _init_wrap_fns
from prefab.utils.decorators import run_once

_init_wrap_fns()
from fabric.api import *