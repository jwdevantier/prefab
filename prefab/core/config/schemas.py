"""
Schema definitions collectively making up the config file
"""
# pylint: disable-msg=C0103
from os import path
import voluptuous as v
from prefab import schema as sc

port = v.All(int, v.Range(min=1, max=65535))
env = sc.dictof(str, v.Any(str, int, float, bool, None))

# Fields common to a parsed host entry
__host_common = sc.mapping({
    v.Required('address'): str,
    v.Required('port', default=22): port,
    v.Required('user', default='root'): str,
    'profile': str
})

# A parsed host entry
host = v.All(
    __host_common,
    v.Any(
        # SSH Key Login
        sc.mapping({
            v.Required('method'): 'key',
            v.Required('keys'): sc.non_empty(sc.seqof(sc.pred(path.isfile)))
        }),
        # Password Login
        sc.mapping({
            v.Required('method'): 'password',
            'password': str #if omitted, will be prompted @ runtime
        })
    )
)

# host entries as found in our json config
json_host = v.Any(
    host, # fully typed-out host
    # ... or some entry referring a profile to merge with
    sc.mapping({
        v.Required('address'): str,
        v.Required('profile'): str
    })
)

profile = sc.mapping({
    v.Required('connection'): sc.mapping({
        v.Required('method'): v.Any('key', 'password'),
        v.Required('user', default='root'): str,
        v.Required('port', default=22): port
    }),
    'env': env
})

role_entry = sc.mapping({
    v.Required('hosts'): sc.non_empty(sc.seqof(str)),
    'env': env
})

json_roles = sc.dictof(str, v.Any(
    #list of host labels
    sc.non_empty(sc.seqof(str)),
    # map containing host labels & a shared environment context
    role_entry
))

json_config = sc.mapping({
    'profiles': sc.dictof(str, profile),
    'hosts': sc.dictof(str, json_host),
    'roles': json_roles
})

config = sc.mapping({
    'profiles': sc.dictof(str, profile),
    'hosts': sc.dictof(str, host),
    'roles': sc.dictof(str, role_entry)
})
