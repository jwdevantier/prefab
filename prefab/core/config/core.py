"""
Functionality which deals with the loading, checking and
parsing of the configuration file.
"""
import os
import json
from json.decoder import JSONDecodeError
from . import parse

def fmt_json_err(exc):
    """Create string describing the JSON decoder error."""
    if not isinstance(exc, JSONDecodeError):
        raise ValueError("got a non JSON decoder err (type: {})".format(exc))

    return (
        "\tline {lineno}, column {colno}: {msg}"
        .format(msg=exc.msg, lineno=exc.lineno, colno=exc.colno)
    )

def read_config(cfg_path):
    """Read the json configuration file from disk.

    NOTE: consistency-checking and parsing are not handled in this function

    NOTE: use 'fmt_json_err' to format the json error message
    """
    with open(cfg_path, mode='r') as fp:
        return json.load(fp)

def parse_config(raw_conf):
    """Parse & transform config.

    Parses & checks the raw configuration file, transforming it
    into a form suitable for consumption by prefab.
    """
    var_env = parse.make_var_env(os.environ, prefix="__")
    return parse.normalize_roles(
        parse.normalize_hosts(
            parse.expand_vars(raw_conf, var_env)))
