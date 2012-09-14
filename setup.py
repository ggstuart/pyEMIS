from setuptools import setup
setup(
    name='pyEMIS',
    version='0.9.0dev3',
    description='Python library for energy consumption data analysis',
    author='Graeme Stuart',
    author_email='ggstuart@gmail.com',
    packages = [
        'pyEMIS', 
        'pyEMIS.data',
        'pyEMIS.data.preparation',
        'pyEMIS.data.adapters',
        'pyEMIS.data.adapters.dynamat_plus',
        'pyEMIS.data.adapters.sustainable_advantage',
        'pyEMIS.models',
        'pyEMIS.analysis',
#        'pyEMIS.EventDetection', 
    ],
    package_dir = {'': 'lib', 'pyEMIS': 'lib'},
#    install_requires=['numpy', 'scipy'],
)
