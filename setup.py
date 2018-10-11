import os
import setuptools
import versioneer

_my_dir = os.path.dirname(os.path.abspath(__file__))
_bse_dir = os.path.join(_my_dir, 'basis_set_exchange')
_readme_path = os.path.join(_my_dir, "README.md")

# Use the readme file for a description
with open(_readme_path, 'r') as readme_file:
    long_description = readme_file.read()

# Find the json files in the data dir and the schema dir
bse_package_data = []
for data_dir in 'data', 'schema', os.path.join('tests', 'sources'):
    for (path, _, filenames) in os.walk(os.path.join('basis_set_exchange', data_dir)):
        for filename in filenames:
            filepath = os.path.join(path, filename)
            bse_package_data.append(os.path.relpath(filepath, 'basis_set_exchange'))

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

        package_data={'basis_set_exchange': bse_package_data},

        zip_safe=True,
    )
