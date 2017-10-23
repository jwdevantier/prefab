"""
Compatibility patches for fabric(3)
"""
# pylint: disable=W0611,C0103,W0212
from functools import wraps

import fabric
import fabric.tasks
import fabric.decorators

from voluptuous.error import Invalid
from funcy.colls import get_in

import prefab.schema as sc
from prefab.core.config import confparse as cp
from prefab.utils.decorators import run_once
from .config import schemas as scc
from .config import confparse as cp

# references to the functions we'll wrap
__fabric__execute = fabric.tasks._execute
__fabric_execute = fabric.tasks.execute
__fabric_hosts = fabric.decorators.hosts

# Wrap fabric.decorators.hosts
# ---
# The point is to provide a decorator which takes host labels
# (as defined in the configuration file) instead of host strings.
#
# Because there is no way to transparently delay computation of
# a dynamically attached property, we install a callable to
# delay the resolution of host labels => host strings. This
# allows the configuration file to be loaded (and with it,
# the hosts) before resolution is attempted.
#
# Actual resolution requires invoking the property once, after
# which the property is replaced by the computed host list,
# requiring no further invocation.
#
# the wrapped execute() function ensures this is done before
# passing off the function to fabric's execute implementation.
def __hosts(*args):
    def decorator(fn):
        """blah."""
        def do_resolve_hosts():
            """One-off resolving of host labels to host_strings."""
            host_list = __resolve_hosts(*args)
            setattr(fn, 'hosts', host_list)
            return getattr(fn, 'hosts')
        setattr(fn, 'hosts', do_resolve_hosts)
        return fn
    return decorator

def _init_wrap_fns():
    """wrap fabric functions as necessary for integration."""
    print("init wrap fns run")
    # wrap fabric's execute() function
    _wrap_execute.__doc__ = fabric.tasks.execute
    fabric.tasks.execute = _wrap_execute

    # wrap fabric's _execute() function (the internal work-horse)
    _wrap__execute.__doc__ = fabric.tasks._execute
    fabric.tasks._execute = _wrap__execute

    # wrap fabric's hosts decorator to automatically translate
    # host labels/aliases into host_strings which the rest of fabric uses
    __hosts.__doc__ = __fabric_hosts
    fabric.decorators.hosts = __hosts

def _init_enrich_fab_env(conf):
    """enrich fabric environment object.

    Installs reference to original configuration object and
    derives various fabric-specific data structures (passwords map,
    role definitions etc) from it."""
    # install refernce to configuration data structure
    # other functions in this compatibility layer relies on its presence
    fabric.api.env['__prefab_conf'] = conf

    fabric.api.env.roledefs = _compile_roledefs(conf)
    fabric.api.env.passwords = _compile_passwords(conf)

@run_once()
def initialize(conf):
    """
    Initalize prefab by hooking into fabric.

    Overrides functions in fabric where necessary and installs a refence
    to prefabs configuration inside fabric itself.

    NOTE: calling this from within fabric.context_managers.settings
          would break break initialization - leaving the config reference
          undefined afterwards.
    """
    print("init run")
    try:
        scc.config(conf)
    except Invalid as exc:
        msg = "'conf' configuration object is not valid - aborting initialization"
        import json
        print(json.dumps(conf, indent=2, sort_keys=True))
        sc.explain(scc.config, conf)
        raise ValueError(msg) from exc
    #_init_wrap_fns(fabric)
    _init_enrich_fab_env(conf)


def _host_str_to_label(host_str):
    return cp.host_label(_conf(), host_str)

def __config_ssh_env(host_str):
    """derive the env settings necessary to connect to host.

    Returns a dictionary of fabric.env settings which should be
    set given the host_entry's specification of the login method
    (password, key)."""
    label = cp.host_label(_conf(), host_str)
    host_entry = cp.host_entry(_conf(), label)
    method = host_entry.get('method', None)
    if method not in ('password', 'key'):
        raise Exception((
            "Expected a password/key method for host, '{}'"
            + "(label: '{}'), got method: '{}'").format(host_str, label, method))
    if host_entry['method'] == 'password':
        return {'no_agent': True, 'no_keys': True}
    else: # key login
        return {'no_agent': False, 'key_filename': None, 'keys': host_entry['keys']}

def __resolve_hosts(*args):
    """resolves one/more hosts into their corresponding host_strings."""
    host_list = __coerce_to_iterable(args)
    return [
        cp.host_string(cp.host_entry(_conf(), label))
        for label in host_list]

# wraps fabric's _execute function
# ---
# from the host string, this function determines the host label,
# examines the corresponding host entry, and determines if this is a ssh
# key- or password-based login, tweaking the fabric environment accordingly.
def _wrap__execute(*args, **kwargs):
    print("(wrapped) _execute")
    # https://github.com/mathiasertl/fabric/blob/master/fabric/tasks.py
    host_str = args[1] # host_string, as seen in source
    # NOTE: not using 'clean_revert=True' (see link) to allow user-level overriding
    # http://docs.fabfile.org/en/1.14/api/core/context_managers.html#fabric.context_managers.settings
    with fabric.context_managers.settings(**__config_ssh_env(host_str)):
        return __fabric__execute(*args, **kwargs)

# wraps fabric's execute function
# ---
# 1) resolves host_list from host labels (as used in the configuration file)
#    to host_strings, which fabric expects
# 2) execute() yields a map of responses, encoded as
#    host_string => return-value pairs.
#    We translate the host_strings back into host labels
def _wrap_execute(fn, *args, **kwargs):
    print("(wrapped) execute")
    host_list = kwargs.pop('hosts', None)
    if host_list:
        kwargs['hosts'] = __resolve_hosts(host_list)

    # Have to delay resolving host list until the configuration
    # file has been loaded - hence our @hosts decorator attaches
    # a function acting as a delayed computation.
    #
    # This checks for a callable property in 'hosts' and executes
    # it - the property itself is responsible for swapping the
    # callable out with the result of its computation
    # (to avoid repeated host resolution)
    try:
        hosts_attr = getattr(fn, 'hosts')
        if callable(hosts_attr):
            hosts_attr()
    except AttributeError:
        pass

    results = __fabric_execute(fn, *args, **kwargs)
    # (host_string => return-value) pairs to (host_label => return-value)
    return {
        cp.host_label(_conf(), k): v
        for (k, v) in results.items()
    }

def _conf():
    """retrieve the conf."""
    return fabric.api.env['__prefab_conf']

def __coerce_to_iterable(args):
    if (len(args) == 1
            and hasattr(args[0], '__iter__')
            and not isinstance(args[0], str)):
        return args[0]
    return args

def _compile_roledefs(conf):
    """Compile roledefs entry describing roles in fabric.

    NOTE: install into 'env.roledefs'."""
    def compile_role_entry(role_entry):
        """creates a roledef entry in fabric's format.

        Resolves the referenced host labels into actual host_strings (fabric)
        and merges in the environment values.
        """
        return {
            **role_entry.get('env', {}),
            'hosts': [
                cp.host_string(get_in(conf, ['hosts', label]))
                for label in role_entry['hosts']]
        }
    return {
        role: compile_role_entry(role_entry) for (role, role_entry) in conf['roles'].items()
    }

def _compile_passwords(conf):
    """Compile dictionary of pre-filled host_string => password mappings.

    Fabric allows passwords to be filled out ahead of time, but will prompt
    for missing entries, expanding this dictionary as execution progresses.

    NOTE: to be installed into 'env.passwords'.
    """
    return {
        cp.host_string(host_entry): host_entry['password']
        for (host_label, host_entry)
        in conf['hosts'].items()
        if host_entry['method'] == 'password' and host_entry.get('password')
    }
