#from distutils.core import setup
from setuptools import setup
setup(
    name='pyEMIS',
    version='0.1.2',
    description='Python library for energy consumption data analysis',
    author='Graeme Stuart',
    author_email='ggstuart@gmail.com',
    packages = [
        'pyEMIS', 
        'pyEMIS.ConsumptionModels', 
        'pyEMIS.DataCleaning', 
        'pyEMIS.EventDetection', 
        'pyEMIS.DataAccess',
        'pyEMIS.DataAccess.mySQL',
#        'pyEMIS.DataAccess.mySQL.Classic',
        'pyEMIS.DataAccess.mySQL.Native',
        'pyEMIS.DataAccess.DynamatPlus',
        'pyEMIS.DataAccess.Fake',
    ],
    package_dir = {'': 'lib', 'pyEMIS': 'lib'},
    install_requires=['numpy', 'scipy'],
)
