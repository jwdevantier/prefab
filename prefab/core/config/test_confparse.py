"""
Tests ability to parse configuration file and derive from it
some fabric-specific data structures.
"""
import pytest
from prefab.test import data as testdata
from . confparse import *

@pytest.mark.parametrize("host_lbl,expected", [
    ("vm3", {'swarm-workers', 'swarm-managers'}),
    ("vm1", {'swarm-workers'}),
    ("vm4", set())
])
def test_host_roles(host_lbl, expected):
    """test that 'host_roles' can lookup the roles in which the host participates."""
    assert set(host_roles(testdata.config, host_lbl)) == expected

@pytest.mark.parametrize('entry,expected', [
    ({'address': 'srv.example.com', 'port': 2200, 'user': 'appadmin'},
     'appadmin@srv.example.com:2200')])
def test_host_string(entry, expected):
    """Test ability to compile a fabric-style host_string from a host_entry dict."""
    assert host_string(entry) == expected

@pytest.mark.parametrize('host_label', [
    'vm1', 'vm2', 'vm3', 'vm4'
])
def test_host_entry(host_label):
    """Test ability to look up host."""
    assert host_entry(testdata.config, host_label) == testdata.config['hosts'][host_label]

@pytest.mark.parametrize("host_lbl,expected", [
    ("vm1", "root@51.15.210.243:22"),
    ("vm3", "appadmin@srv3.example.com:2202")
])
def test_host_string_entry_comp(host_lbl, expected):
    """Ensure compiled host strings follow format."""
    assert host_string(host_entry(testdata.config, host_lbl)) == expected

@pytest.mark.parametrize('label', [
    "vm1", "vm2", "vm3", "vm4"
])
def test_host_label_lookup(label):
    """test ability to resolve a host_string to a host_label."""
    host_str = host_string(host_entry(testdata.config, label))
    assert host_label(testdata.config, host_str) == label

@pytest.mark.parametrize('role,members', [
    ('swarm-workers', ['vm1', 'vm2', 'vm3']),
    ('swarm-managers', ['vm3']),
    ('bogus', [])
])
def test_role_host_strings(role, members):
    """test ability to resolve a role into the host_strings of
    the hosts participating in the role."""
    assert set(role_host_strings(testdata.config, role)) == set(
        [host_string(host_entry(testdata.config, member)) for member in members])