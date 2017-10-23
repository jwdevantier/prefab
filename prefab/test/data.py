# a normalized (i.e. fully parsed) configuration structure
config = {
    'hosts': {
        'vm1': {
            'address': '51.15.210.243',
            'method': 'key',
            'port': 22,
            'user': 'root',
            'keys': ['/home/smth/.ssh/id_scaleway']
        },
        'vm2': {
            'address': '51.15.210.243',
            'method': 'key',
            'port': 24,
            'user': 'root',
            'keys': ['/home/smth/.ssh/id_scaleway']
        },
        'vm3': {
            'address': 'srv3.example.com',
            'port': 2202,
            'user': 'appadmin',
            'method': 'password',
        },
        'vm4': {
            'address': 'srv4.blah.example.com',
            'port': 25,
            'user': 'someuser',
            'method': 'password',
            'password': 's3cr3t!'
        }
    },
    'roles': {
        'swarm-workers': {
            'hosts': ['vm1', 'vm2', 'vm3'],
            'env': {
                'manager': False,
                'role': 'blue-collar'
            }
        },
        'swarm-managers': {
            'hosts': ['vm3'],
            'env': {
                'manager': True
            }
        }
    }
}