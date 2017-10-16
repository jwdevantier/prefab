"""
Utility functions facilitating local administration.
"""
from fabric import api as f

@f.task
def new_ssh_key(tag, comment):
    """Generate new SSH key (new_ssh_key:tag=scaleway,comment=\"something insightful\""""
    date=f.local("date -I")
    f.local('ssh-keygen -t rsa -b 4096 -C "`date -I`: {comment}" -f ~/.ssh/id_{tag}'.format(date=date, tag=tag, comment=comment))

@f.task
def test():
    print([k in f.env.keys() if k.startswith('ssh')])