from setuptools import setup
setup(
    name='pyEMIS',
    version='0.9.1.dev0',
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
        'pyEMIS.data.adapters.british_gas',
        'pyEMIS.data.adapters.graeme_phd',
        'pyEMIS.models',
        'pyEMIS.analysis',
    ],
    package_dir = {'': 'lib', 'pyEMIS': 'lib'},
#    install_requires=['numpy', 'scipy'],
)
