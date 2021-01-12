#!/usr/bin/env python3

from distutils.core import setup

setup(name='cioos_yaml_to_erddap',
      version='0.1',
      description='Convery CIOOS YAML metadata to erddap',
      url='https://github.com/cioos-siooc/cioos-yaml-to-erddap',
      packages=['cioos_yaml_to_erddap'],
      install_requires=[
          'pyyaml'
      ]
      )
