[![Build Status](https://travis-ci.org/MolSSI-BSE/basis_set_exchange.svg?branch=master)](https://travis-ci.org/MolSSI-BSE/basis_set_exchange)
[![codecov](https://codecov.io/gh/MolSSI-BSE/basis_set_exchange/branch/master/graph/badge.svg)](https://codecov.io/gh/MolSSI-BSE/basis_set_exchange)
[![PyPI version](https://img.shields.io/pypi/v/basis_set_exchange.svg)](https://pypi.org/project/basis_set_exchange/)

**Warning - This project is still under heavy development.**

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

## Documentation

Full user and developer documentation can be found at
https://molssi-bse.github.io/basis_set_exchange

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

## License

This project is released under the BSE 3-Clause license. See LICENSE for details.
