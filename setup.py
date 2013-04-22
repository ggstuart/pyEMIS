from setuptools import setup

try:
    import numpy
    import scipy
except ImportError:
    raise ImportError("pyEMIS requires numpy and scipy")
    
setup(
    name='pyEMIS',
    version='0.9.3.dev3',
    description='Python library for energy consumption data analysis',
    author='Graeme Stuart',
    author_email='ggstuart@gmail.com',
    packages = [
        'pyEMIS', 
        'pyEMIS.data',
        'pyEMIS.data.preparation',
        'pyEMIS.data.adapters',
        'pyEMIS.models',
        'pyEMIS.analysis',
    ],
    package_dir = {'': 'lib', 'pyEMIS': 'lib'},
)
