"""
Tests ability derive fabric-specific data structures from
prefab's configuration file.
"""
import pytest
from prefab.test import data as testdata
from .fabcompat import _compile_passwords, _compile_roledefs
from .config import confparse as cp

def test_compile_roledefs():
    """test ability to compile a fabric-style roledefs datastructure."""
    def __compile(host):
        """Resolves host label to a (fabric-style) host_string."""
        return cp.host_string(cp.host_entry(testdata.config, host))

    assert _compile_roledefs(testdata.config) == {
        "swarm-managers": {
            'hosts': [__compile("vm3")],
            'manager': True
        },
        'swarm-workers': {
            'hosts': [__compile("vm1"), __compile("vm2"), __compile("vm3")],
            'manager': False,
            'role': 'blue-collar'
        }
    }

def test_compile_passwds():
    """test ability to compile a fabric-style password lookup dict."""
    assert _compile_passwords(testdata.config) == {
        cp.host_string(cp.host_entry(testdata.config, 'vm4')): 's3cr3t!'
    }