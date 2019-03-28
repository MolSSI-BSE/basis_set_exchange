[![Build Status](https://travis-ci.org/MolSSI-BSE/basis_set_exchange.svg?branch=master)](https://travis-ci.org/MolSSI-BSE/basis_set_exchange)
[![codecov](https://codecov.io/gh/MolSSI-BSE/basis_set_exchange/branch/master/graph/badge.svg)](https://codecov.io/gh/MolSSI-BSE/basis_set_exchange)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/MolSSI-BSE/basis_set_exchange.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/MolSSI-BSE/basis_set_exchange/context:python)
[![PyPI version](https://img.shields.io/pypi/v/basis_set_exchange.svg)](https://pypi.org/project/basis_set_exchange/)

## Basis Set Exchange Website

If you are looking for the Basis Set Exchange website (which can be
used to browse and download this data in a more user-friendly way),
visit https://www.basissetexchange.org


## Overview

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

This library is used to form the backend of the new Basis Set Exchange
website.

This project is a collaboration between the Molecular Sciences Software
Institute (http://www.molssi.org) and the Environmental Molecular Sciences
Laboratory (https://www.emsl.pnl.gov)

## Citation

When publishing results obtained from use of the Basis Set Exchange software, please cite:

 * *A New Basis Set Exchange: An Open, Up-to-date Resource for the Molecular Sciences Community Pritchard*, Benjamin P. and Altarawy, Doaa and Windus, Theresa L. *Manuscript in Preparation*

For citing the previous EMSL/PNNL Basis Set Exchange, please cite the following references:

 * *The Role of Databases in Support of Computational Chemistry Calculations,* Feller, D., *J. Comp. Chem.* **1996**, 17(13), 1571-1586.
 * *Basis Set Exchange: A Community Database for Computational Sciences Schuchardt,* K.L., Didier, B.T., Elsethagen, T., Sun, L., Gurumoorthi, V., Chase, J., Li, J., and Windus, T.L. *J. Chem. Inf. Model.* **2007**, 47(3), 1045-1052, doi:10.1021/ci600510j.

## Documentation

Full user and developer documentation can be found at
https://molssi-bse.github.io/basis_set_exchange

An overview of the project and its design is also available at
https://molssi-bse.github.io/basis_set_exchange/project_doc.html

## Command line interface

This library also includes a command line interface.
See https://molssi-bse.github.io/basis_set_exchange/bse_cli.html for how to use it.

## Installation
This project can be installed via pip/PyPI.
```
pip install basis_set_exchange
```

If checking out from github, you can do a local install of the Python
directory,
```
pip install -e .
```

## Testing

Tests can be run using `py.test -v` once installed. Thorough (but very
long) tests can be run with `py.test --runslow`.

## Examples
```
import basis_set_exchange as bse

# Obtain the STO-3G basis set in nwchem format (as a string) for hydrogen and carbon
bse.get_basis('STO-3G', elements=[1,6], fmt='nwchem')

# Obtain the references for the above
bse.get_references('STO-3G', elements=[1,6], fmt='txt')
```

For more documentation, see https://molssi-bse.github.io/basis_set_exchange


## Command line

Same as above, but using the command line

``$ bse bse get-basis sto-3g nwchem --elements=1,6``

``$ bse get-refs sto-3g txt --elements=1,6``

## License

This project is released under the BSE 3-Clause license. See LICENSE for details.
