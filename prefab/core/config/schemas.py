"""
Schema definitions collectively making up the config file
"""
from os import path
from voluptuous import Schema, Required, All, Any, Range
from prefab import schema as S


# could define hosts
# could define groups
# could write ctx mgr to swap out host list
# => easier to compose longer flows involving multiple hosts

PORT = All(int, Range(min=1, max=65535))

__HOST_DEFAULTS = {
    'port': PORT,
    'user': str,
    'keys': S.seqof(S.pred(path.isfile)),
    'sudo_password': str
}

HOST = Schema({
    **__HOST_DEFAULTS,
    **{
        # hostname/ip of server
        Required('address'): str,
        # port number
        'port': PORT,
        'user': str
    }
})

CONFIG = Schema({
    'host_defaults': Schema(__HOST_DEFAULTS),
    'hosts': S.dictof(str, HOST),
    'groups': S.dictof(str, S.seqof(str))
})

################################################
# Parsed config - the structure after processing
################################################

P_HOST = Schema(
    All(
        Schema({
            Required('address'): str,
            Required('port'): PORT}),
        Any(
            Schema({
                Required('user'): str,
                Required('password'): str}),
            Schema({
                Required('keys'): S.seqof(S.pred(path.isfile))
            }))))

P_CONFIG = Schema({
    'hosts': P_HOST,
    'groups': S.dictof(str, S.seqof(str))
})
