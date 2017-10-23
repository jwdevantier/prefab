"""
Functionality used to parse and create a canonical representation of the entries defined
in the configuration file.
"""
from os import getcwd
from functools import reduce
from funcy.colls import get_in, update_in
from funcy.seqs import keep
from voluptuous.error import Invalid
from prefab.utils import walk
from prefab import schema as sc
from . import schemas as scc

class VarExpansionError(Exception):
    """Indicate string interpolation expansion error.

    Error which is raised if a config string references a variable
    (string interpolation) which isn't defined in the environment."""
    def __init__(self, env, varname, val):
        super().__init__("Error encountered while expanding the configuration file. Configuration refers to unbound variable '{varname}'.".format(varname=varname))

        self._env = env
        self._varname = varname
        self._value = val

    @property
    def env(self):
        """The environment used satisfying variables"""
        return self.env

    @property
    def varname(self):
        """configuration key whose value undefined variable references."""
        return self._varname

    @property
    def value(self):
        """string which raised the exception."""
        return self._value

def make_var_env(env, cwd=getcwd(), prefix='__'):
    """
    Given an environment (expressed as a dictionary), yield a environment for variable expansion.
    """
    def lstrip(strval, prefix):
        """strips provided prefix from the strings beginning."""
        return strval.split(prefix, 1)[-1]

    var_env = {
        lstrip(k, prefix).lower(): v
        for (k, v) in env.items()
        if k is str and k.startswith(prefix)
    }
    var_env['cwd'] = cwd
    var_env['home'] = env['HOME']
    return var_env

def expand_vars(conf, var_env):
    """
    Expand variables contained in configuration, with vars given from var_env.

    conf    - the configuration, can be a nested datastructure of dicts/sets/lists etc
    var_env - the environment used for expanding variables in strings
    """
    def __expand_var(val):
        """expand vars in val iff val is a string."""
        if isinstance(val, str):
            try:
                return val.format(**var_env)
            except KeyError as exc:
                # variable refers to undefined variables
                raise VarExpansionError(var_env, exc.args[0], val)
        return val
    return walk.prewalk(__expand_var, conf)

class HostEntryError(Exception):
    """Base error indicating a malformatted host entry."""
    def __init__(self, host_label, host_config, **kwargs):
        msg = (
            kwargs.pop('msg', None)
            or "host '{}': {}".format(
                host_label, kwargs.pop('reason', 'is incorrectly configured')))
        super().__init__(msg)
        self._error = kwargs.pop('error', None)
        self._host_label = host_label
        self._host_config = host_config

    @property
    def host_label(self):
        """Label identifying the host entry in the configuration."""
        return self._host_label

    @property
    def host_config(self):
        """Configuration describing the host connection settings."""
        return self._host_config

    @property
    def error(self):
        """Validation error (or None if unspecified)"""
        return self._error

# incomplete host entries referring to a missing profile
class HostEntryInvalidProfile(HostEntryError):
    """Raised when an incomplete host entry refers to a missing/undefined profile."""
    def __init__(self, host_label, host_config, msg=""):
        super().__init__(host_label, host_config)

#incomplete host entries need to refer to a profile
class HostEntryProfileMissing(HostEntryError):
    """Raised for incomplete entries whose referenced profile entry is undefined."""
    def __init__(self, host_label, host_config):
        super().__init__(
            host_label, host_config,
            reason="profile '{}' not defined in config".format(host_config['profile']))

    @property
    def profile(self):
        """get label identifying the referenced profile."""
        return self.host_config['profile']

def normalize_hosts(conf):
    """ Resolve the host entries of the configuration file."""
    def normalize_host(label, host_config):
        """Given a host entry, resolve it provided."""
        # already OK, skip
        if sc.valid(scc.host, host_config):
            return host_config

        # malformed entry, incomplete & missing required entries
        if not sc.valid(scc.json_host, host_config):
            if 'address' not in host_config:
                reason = "missing 'address' field"
            elif 'profile' not in host_config:
                reason = "missing 'profile' field. Incomplete entries must refer to a profile"
            else:
                reason = None # will offer a generic default msg
            raise HostEntryError(label, host_config, reason=reason)

        # fetch referenced profile
        profile = get_in(conf, ['profiles', host_config['profile']])
        if not profile:
            raise HostEntryProfileMissing(label, host_config)

        host_entry = {**profile['connection'], **host_config}
        try:
            return scc.host(host_entry)
        except Invalid as exc:
            raise HostEntryError(
                label, host_entry,
                reason=(
                    "merging entry with profile '{}' does not produce a valid host entry"
                    .format(host_config['profile'])),
                error=exc)
    return update_in(
        conf, ['hosts'],
        lambda hosts: {
            lbl: normalize_host(lbl, entry)
            for (lbl, entry) in hosts.items()})

class MissingHostsError(Exception):
    """Raised when configuration refers one or more hosts who lacks a corresponding definition."""
    def __init__(self, missing_hosts, **kwargs):
        msg = (
            kwargs.pop('msg', None) or
            "Hosts referenced in config, but undefined: {}".format(missing_hosts))
        super().__init__(msg)

def _check_role_refs(conf, role_entries):
    def undefined_host(host_label):
        """Returns input host label iff host could not be found in config."""
        if not get_in(conf, ['hosts', host_label]):
            return host_label
        return False
    def set_merge(myset, iterable):
        """update set with contents of iterable and return it.

        NOTE: in-place updates"""
        myset.update(iterable)
        return myset
    hosts = reduce(
        lambda acc, host_list: set_merge(acc, host_list),
        map(lambda r: r['hosts'], role_entries.values()),
        set())
    return keep(undefined_host, hosts)

def normalize_roles(conf):
    # check to see if the hosts referenced in
    # the roles actually exist.

    def normalize_role(role_entry):
        """normalize roles into the dict-style representation.

        roles may defined as a dictionary referencing hosts and an
        environment or simply be a list of hosts.
        To ease further processing, we normalize the entries, converting
        all to the dictionary-style representation."""
        if isinstance(role_entry, list):
            return {'hosts': role_entry, 'env': {}}
        return role_entry
    normalized_role_entries = {
        label: normalize_role(role)
        for (label, role)
        in conf.get('roles', {}).items()
    }
    _check_role_refs(conf, normalized_role_entries)
    return {
        **conf,
        **{'roles': normalized_role_entries}
    }
