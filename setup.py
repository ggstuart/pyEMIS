from setuptools import setup
setup(
    name='pyEMIS',
    version='0.8.5',
    description='Python library for energy consumption data analysis',
    author='Graeme Stuart',
    author_email='ggstuart@gmail.com',
    packages = [
        'pyEMIS', 
        'pyEMIS.ConsumptionModels', 
        'pyEMIS.DataCleaning', 
        'pyEMIS.EventDetection', 
        'pyEMIS.DataAccess',
        'pyEMIS.DataAccess.sources',
        'pyEMIS.DataAccess.adapters',
    ],
    package_dir = {'': 'lib', 'pyEMIS': 'lib'},
#    install_requires=['numpy', 'scipy'],
)
