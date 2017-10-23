#!/usr/bin/env python3
from os import path, getcwd
import sys
from json.decoder import JSONDecodeError
import click
from click import make_pass_decorator
from voluptuous.error import Invalid
import prefab.core as c
import prefab.core.api as fab

## Errorcodes
ERR_NO_CFG = -1
ERR_INVALID_CFG = -2

class Context:
    """Holds entire application context, passed around in the program."""
    def __init__(self):
        self._verbose = self._config = None

    @property
    def verbose(self):
        return self._verbose or False

    @property
    def config(self):
        return self._config or {}

    @config.setter
    def config(self, cfg):
        self._config = cfg

pass_cli_ctx = make_pass_decorator(Context, ensure=True)

@click.group()
@click.option('--verbose', is_flag=True)
@click.option('--config-path', default=path.join(getcwd(), 'prefab.json'), type=str)
@pass_cli_ctx
def cli(cctx, verbose, config_path):
    if verbose:
        cctx.verbose = verbose
    try:
        cctx.config = c.parse_config(c.read_config(config_path))
    except JSONDecodeError as exc:
        click.echo("Failed to parse config file, invalid JSON:", err=True)
        click.echo(c.fmt_json_err(exc), err=True)
        sys.exit(ERR_INVALID_CFG)
    except Invalid as exc:
        print("Unhandled error loading configuration")
        print(repr(exc))
        sys.exit(ERR_INVALID_CFG)
    c.initialize(cctx.config)

##
## Playground

#@fab.hosts("anton")
@fab.roles("cupcakes")
def hello():
    fab.run("cat /etc/issue")

@cli.command()
@pass_cli_ctx
def run(cctx):
    if not cctx.verbose:
        print("Not verbose...")
    else:
        print("verbose, yay!")
    fab.execute(hello)
    fab.execute(hello, hosts="anton")
    fab.local("cat /etc/issue")

@cli.command()
@pass_cli_ctx
def debug(cctx):
    import json
    def pp(obj):
        """format obj as a string for pretty-printing."""
        return json.dumps(obj, indent=2, sort_keys=True)

    print("Config parsed successfully, result:")
    print("---//---")
    print(pp(cctx.config))
    print("---//---")
    print("Config compiled into the following changes to fab env:")
    print("roledefs:")
    print("")
    print(pp(fab.env['roledefs']))
    print("passwords:")
    print("")
    print(pp(fab.env.passwords))
    print("---//---")
