import setuptools

if __name__ == "__main__":
    setuptools.setup(
        name='basis_set_exchange',
        version="0.3.0",
        description='The Quantum Chemistry Basis Set Exchange',
        author='The Molecular Sciences Software Institute',
        author_email='bpp4@vt.edu',
        url="https://github.com/MolSSI/basis_set_exchange",
        license='BSD-3C',
        packages=setuptools.find_packages(),
        install_requires=[
            'jsonschema',
        ],
        extras_require={
            'docs': [
                'sphinx==1.2.3',  # autodoc was broken in 1.3.1
                'sphinxcontrib-napoleon',
                'sphinx_rtd_theme',
                'numpydoc',
            ],
            'tests': [
                'pytest',
                'pytest-cov',
                'pytest-pep8',
            ],
        },

        tests_require=[
            'pytest',
            'pytest-cov',
            'pytest-pep8',
        ],

        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3',
        ],
        zip_safe=True,
    )
