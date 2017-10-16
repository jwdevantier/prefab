#!/usr/bin/env python3
from os import path, getcwd
from sys import exit
from json.decoder import JSONDecodeError
import click
from voluptuous.error import Invalid
import prefab.core.config as c


## Errorcodes
ERR_NO_CFG = -1
ERR_INVALID_CFG = -2


@click.group()
@click.option('--verbose', is_flag=True)
@click.option('--config-path', default=path.join(getcwd(), 'prefab.json'), type=str)
@c.pass_config
def cli(cctx, verbose, config_path):
    if verbose:
        cctx.verbose = verbose
    try:
        cctx.config = c.load(config_path)
    except JSONDecodeError as exc:
        click.echo("Failed to parse config file, invalid JSON:", err=True)
        click.echo(c.fmt_json_err(exc), err=True)
        exit(ERR_INVALID_CFG)
    except Invalid:
        exit(ERR_INVALID_CFG)

@cli.command()
@c.pass_config
def run(cctx):
    if not cctx.verbose:
        print("Not verbose...")
    else:
        print("verbose, yay!")
