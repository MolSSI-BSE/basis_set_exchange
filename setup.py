import setuptools
import versioneer

if __name__ == "__main__":
    my_packages=setuptools.find_packages()

    setuptools.setup(
        name='basis_set_exchange',
        version=versioneer.get_version(),
        cmdclass=versioneer.get_cmdclass(),
        description='The Quantum Chemistry Basis Set Exchange',
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
