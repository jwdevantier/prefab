"""
"""
import json
from json.decoder import JSONDecodeError
from os import environ, getcwd

from click import make_pass_decorator, echo
from voluptuous.error import MultipleInvalid
from voluptuous.humanize import humanize_error
from prefab.utils import walk
from prefab.core.config import schemas
from prefab import schema

class Context:
    def __init__(self):
        self.verbose = False
        self.config = {}

pass_config = make_pass_decorator(Context, ensure=True)

class VarExpansionError(Exception):
    def __init__(self, ctx, config, varname):
        super().__init__("Error encountered while expanding the configuration file. Configuration refers to unbound variable '{varname}'.".format(varname=varname))

        self.config = config
        self.env = ctx
        self.varname = varname

def merge_conf_defaults(conf):
    """

    """
    

    # determine if entry already valid -- SKIP IF SO
    # --else--
    # determine what backup login info we have
    # => write it into this host entry
    #try schemas.P_HOST
    for host in [x for x in conf["hosts"] if not schema.valid(schemas.P_HOST, x)]:
        print("no pass")
        print(repr(host))
        pass
    pass


def load(cfg_path, prefix="__"):
    """Load & process configuration.

    Loads the configuration, validates its generaly structure
    and transforms it into a consumable form (merging in defaults,
    expand variables ...)"""
    raw_cfg = None
    with open(cfg_path, mode='r') as fp:
        raw_cfg = json.load(fp)

    def lstrip(strval, prefix):
        """strips provided prefix from the strings beginning."""
        return strval.split(prefix, 1)[-1]

    ctx_vars = {
        lstrip(k, prefix).lower(): v
        for (k, v) in environ.items()
        if k is str and k.startswith(prefix)
    }
    ctx_vars['cwd'] = getcwd()
    ctx_vars['home'] = environ['HOME']

    def expand_vars(x):
        """Expand variables contained input iff input is a string."""
        if isinstance(x, str):
            try:
                return x.format(**ctx_vars)
            except KeyError as exc:
                # variable refers to undefined variables
                raise VarExpansionError(ctx_vars, raw_cfg, exc.args[0])
        return x

    try:
        data = walk.prewalk(expand_vars, raw_cfg)
        return schemas.CONFIG(data)
    except MultipleInvalid as exc:
        echo("Errors found validating your config:", err=True)
        for err in exc.errors:
            echo("   * {}".format(humanize_error(data, err), err=True))
            echo("", err=True)
        raise exc

def fmt_json_err(exc):
    """Create string describing the JSON decoder error."""
    if not isinstance(exc, JSONDecodeError):
        raise ValueError("got a non JSON decoder err (type: {})".format(exc))
    
    return (
        "\tline {lineno}, column {colno}: {msg}"
        .format(msg=exc.msg, lineno=exc.lineno, colno=exc.colno)
    )
        