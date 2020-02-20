import os
import setuptools
import versioneer
import io

_my_dir = os.path.dirname(os.path.abspath(__file__))
_readme_path = os.path.join(_my_dir, "README.md")

# Use the readme file for a description
with io.open(_readme_path, 'r', encoding='utf-8') as readme_file:
    long_description = readme_file.read()

# Find the json files in the data dir and the schema dir
bse_package_data = ['pytest.ini']
data_dirs = ['data', 'schema',
             os.path.join('tests', 'sources'),
             os.path.join('tests', 'fakedata'),
             os.path.join('tests', 'curate_test_data'),
             os.path.join('tests', 'reader_test_data'),
             os.path.join('tests', 'validator_test_data')
]

for data_dir in data_dirs:
    for (path, _, filenames) in os.walk(os.path.join('basis_set_exchange', data_dir)):
        for filename in filenames:
            filepath = os.path.join(path, filename)
            bse_package_data.append(os.path.relpath(filepath, 'basis_set_exchange'))

if __name__ == "__main__":
    my_packages = setuptools.find_packages()

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
        entry_points={
            "console_scripts": ["bse=basis_set_exchange.cli:run_bse_cli",
                                "bsecurate=basis_set_exchange.cli:run_bsecurate_cli"]
        },
        install_requires=[
            'jsonschema',
            'argcomplete'
        ],
        extras_require={
            'docs': [
                'sphinx',
                'sphinxcontrib-programoutput',
                'sphinx_rtd_theme',
                'numpydoc',
                'graphviz'
            ],
            'tests': [
                'pytest>=4.0',
                'pytest-cov'
            ],
            'curate': [
                'graphviz'
            ]
        },

        python_requires='>=3',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8'
        ],

        package_data={'basis_set_exchange': bse_package_data},

        zip_safe=True,
    )
