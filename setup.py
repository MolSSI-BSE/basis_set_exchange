import os
import setuptools
import versioneer

_my_dir = os.path.dirname(os.path.abspath(__file__))
_readme_path = os.path.join(_my_dir, "README.md")
with open(_readme_path, 'r') as readme_file:
    long_description = readme_file.read()

long_description = '''
This project is a library containing basis sets for use in quantum
chemistry calculations.  In addition, this library has functionality
for manipulation of basis set data.

The goal of this project is to create a consistent, thoroughly curated
database of basis sets, and to provide a standard nomenclature for
quantum chemistry.

The data contained within this library is being thoroughly evaluated
and checked against relevant literature, software implementations, and
other databases when available. The original data from the PNNL Basis
Set Exchange is also available.

This project is a collaboration between the Molecular Sciences Software
Institute (http://www.molssi.org) and the Environmental Molecular Sciences
Laboratory (https://www.emsl.pnl.gov)

The source repo is available at https://github.com/MolSSI-BSE/basis_set_exchange

Documentation is available at https://molssi-bse.github.io/basis_set_exchange
'''
    
if __name__ == "__main__":
    my_packages=setuptools.find_packages()

    setuptools.setup(
        name='basis_set_exchange',
        version=versioneer.get_version(),
        cmdclass=versioneer.get_cmdclass(),
        description='The Quantum Chemistry Basis Set Exchange',
        long_description=long_description,
        long_description_content_type='text/markdown',
        author='The Molecular Sciences Software Institute',
        author_email='bpp4@vt.edu',
        url="https://github.com/MolSSI-BSE/basis_set_exchange",
        license='BSD-3C',
        packages=my_packages,
        install_requires=[
            'jsonschema',
        ],
        extras_require={
            'docs': [
                'sphinx',
                'sphinxcontrib-napoleon',
                'sphinx_rtd_theme',
                'numpydoc',
            ],
            'tests': [
                'pytest',
                'pytest-cov'
            ],
        },

        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3',
        ],

        package_data={'basis_set_exchange': ['data/*', 'data/*/*']},

        zip_safe=True,
    )
