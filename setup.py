#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="prefab",
    version="0.1",
    license="MIT",
    description="Application for light, python-driven server administration",
    author="Jesper W. Devantier",
    author_email="github@pseudonymous.me",
    url="https://github.com/jwdevantier/prefab",
    packages=find_packages(exclude=['contrib', 'tests', 'docs']),
    install_requires = [
        'click', 'Fabric3', 'voluptuous' 
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5'
    ],
    entry_points='''
        [console_scripts]
        prefab=app:cli
    '''
)