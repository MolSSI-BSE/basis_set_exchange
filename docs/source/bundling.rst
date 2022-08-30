.. _bundles:

Creating Basis Set Bundles
==============================================


About Bundles
-------------------

Bundles are archive files (zip or tar.bz2) that contain all the basis sets
in a given format. The archives also include references and notes for each basis
set, as well as notes for each basis set family.


Creating via python
--------------------

Bundles can be created with the :func:`bundle.create_bundle` function.
By default, the type of archive will be deduced from the extension, although
this can be overridden with the `archive_type` option. 

An alternate location of data to export can be specified with `data_dir`::

   >>> # Create /tmp/all_nwchem.zip from all basis sets
   >>> # in nwchem format. All references will be in bibtex
   >>> basis_set_exchange.create_bundle('/tmp/all_nwchem.zip', 'nwchem', 'bib')

   >>> # Create /tmp/all_g94.tar.bz2 from all basis sets
   >>> # in gaussian94 format. All references will be in json
   >>> basis_set_exchange.create_bundle('/tmp/all_g94.tar.bz2', 'gaussian94', 'json')



Creating via the command line
-----------------------------

The same functionality can be accessed via the command-line interface::

   bse create-bundle nwchem bib /tmp/all_nwchem.zip
