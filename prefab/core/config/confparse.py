"""
Functionality for integrating with fabric(3)
"""
from funcy.colls import omit, get_in
from fabric import network as fnw

def host_string(host_entry):
    """compile host string from a (parsed) host_entry."""
    return fnw.join_host_strings(
        host_entry['user'], host_entry['address'], host_entry['port'])

def host_entry(conf, label):
    """Retrieve entry defining the host identified by 'label'."""
    return conf['hosts'][label]

def host_roles(conf, label):
    """given a host label, return the roles in which it participates."""
    roles = conf.get('roles', {})
    return [
        role for role in roles
        if label in roles[role]['hosts']]

def host_label(conf, host_str):
    """given a host label, return a single host-label (or fail)."""
    user, address, port = fnw.normalize(host_str)
    labels = {
        k: v for (k, v) in conf['hosts'].items()
        if v['user'] == user
        and v['address'] == address
        and v['port'] == int(port)}.keys()
    assert len(labels) == 1
    return next(iter(labels))

def role_host_strings(conf, role_label):
    """xx"""
    return [
        host_string(get_in(conf, ['hosts', label]))
        for label in get_in(conf, ['roles', role_label, 'hosts'], [])]


