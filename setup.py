from distutils.core import setup
setup(
    name='pyEMIS',
    version='0.1.2',
    description='Python library for energy consumption data analysis',
    author='Graeme Stuart',
    author_email='ggstuart@gmail.com',
    packages = ['ConsumptionModels', 'DataCleaning', 'EventDetection'],
    package_dir = {'': 'lib'},
    requires=['numpy', 'scipy'],
)
