.. Basis Set Exchange documentation master file

Basis Set Exchange - Library
==============================================

This project is the data repository for basis sets found in quantum
chemistry, plus a library for reading and manipulating the basis sets.

With this library, you can obtain basis sets in various formats,
manipulate them (contract, uncontract), as well as convert
basis set files between formats. Reference information can also be queried.

The library also contains a command line interface. See :ref:`bse_cli`.

This library is a core part of the Basis Set Exchange
(https://www.basissetexchange.org) and is a collaboration between the
Molecular Sciences Software Institute (https://molssi.org) and the
Environmental Molecular Sciences Laboratory (https://www.emsl.pnl.gov)

The code for this project is located on GitHub at
https://github.com/MolSSI-BSE/basis_set_exchange


Citation
========

When publishing results obtained from use of the Basis Set Exchange software, please cite:

 * *A New Basis Set Exchange: An Open, Up-to-date Resource for the Molecular Sciences Community* Benjamin P. Pritchard, Doaa Altarawy, Brett Didier, Tara D. Gibson, and Theresa L. Windus *J. Chem. Inf. Model.* **2019**, 59(11), 4814-4820, doi:10.1021/acs.jcim.9b00725

For citing the previous EMSL/PNNL Basis Set Exchange, please cite the following references:

 * *The Role of Databases in Support of Computational Chemistry Calculations,* Feller, D., *J. Comp. Chem.* **1996**, 17(13), 1571-1586
 * *Basis Set Exchange: A Community Database for Computational Sciences Schuchardt,* K.L., Didier, B.T., Elsethagen, T., Sun, L., Gurumoorthi, V., Chase, J., Li, J., and Windus, T.L. *J. Chem. Inf. Model.* **2007**, 47(3), 1045-1052, doi:10.1021/ci600510j


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   bse_cli
   conversion
   minimal_sets
   augmentation
   calendarization
   bundling
   user_api
   developer
   bsecurate_cli
   web_api


License
==============================================

The code is released under the BSD 3-Clause license. See the `LICENSE <https://github.com/MolSSI-BSE/basis_set_exchange/blob/master/LICENSE>`_ file for details.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
