# -*- encoding: utf-8 -*-
from __future__ import absolute_import, print_function
from setuptools import setup, find_packages

# try:
#     import numpy
#     import scipy
# except ImportError:
#     raise ImportError("pyEMIS requires numpy and scipy")

setup(
    name='pyEMIS',
    version='0.9.5',
    description='Python library for energy consumption data analysis',
    author='Graeme Stuart',
    author_email='ggstuart@gmail.com',
    url='https://github.com/ggstuart/pyEMIS',
    packages=find_packages('lib'),
    package_dir={'': 'lib'},
    install_requires=[
        'numpy',
        'scipy',
        'python-dateutil'
    ]
)
