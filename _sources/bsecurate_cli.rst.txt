The bsecurate command line interface
==============================================

In addition to the user-oriented command-line interface, the BSE also
contains a command-line interface for curation functions ``bsecurate``.
This can be used to query, add, or modify basis set data.


Installation and TAB completion
-------------------------------

See :ref:`cliinstall`

Note that some functionality will require installing the ``curate`` section
(ie, ``pip install basis_set_exchange[docs,tests,curate]``).

Rendering/Viewing graphs will require graphviz.


General usage
-------------------

The ``bsecurate`` command is generally followed by a subcommand (see below). ``bsecurate -h`` will display help
and ``bsecurate -V`` will display the version and exit.

.. command-output:: bsecurate -h


In general, values provided to options (such as basis set names, formats, and elements) are
not case sensitive.

There are two global options available to all subcommands. The first is an alternate
data directory can be specified with ``-d`` or ``--data-dir``.
Also, output can be written to a file rather than to the terminal with ``-o``.
This is similar to the ``bse`` command line program.


Subcommands
-------------------

Below is a list of the available subcommands. All subcommands
can take the ``-h`` option to display help for that subcommand.

.. command-output:: bsecurate elements-in-files -h
   :ellipsis: 8


elements-in-files
*******************

For a list of BSE JSON files, determine what elements the file contains data for.
This works on table, element, and component data files.

.. command-output:: DATADIR=`bse get-data-dir`; bsecurate elements-in-files ${DATADIR}/6-31G.0.table.json ${DATADIR}/dunning/*element*json
   :shell:


component-file-refs
*******************

.. command-output:: DATADIR=`bse get-data-dir`; bsecurate component-file-refs ${DATADIR}/dunning/cc-pVDZ.1.json
   :shell:


print-component-file
********************

Pretty prints data from a component file.


.. command-output:: DATADIR=`bse get-data-dir`; bsecurate print-component-file ${DATADIR}/dunning/cc-pVDZ.1.json
   :shell:
   :ellipsis: 10


make-diff
***************

Compute the difference between two groups of JSON files and store them in '.diff' files.

For each file specified with the ``-l``, subtract all the common shells in files specified
with ``-r``.

Multiple files are specified after the ``-r`` or ``-l`` flag. For example, ``-l file1 file2 -r file3 file3``.

For each file specified with ``-l``, an output file is created with the same name but with `.diff` appended to the filename.


compare-basis-sets
*******************

Compare two basis sets and print a report.
These are read/composed from a data directory. Versions can be specified

.. command-output:: bsecurate compare-basis-sets 6-31G 6-31G --version1 1 --version2 0
   :ellipsis: 8,-8


compare-basis-files
*******************

Compare two formatted basis sets files and print a report. For valid formats, use ``get-reader-formats``


view-graph-file
***************

Similar to ``make-graph-file``, but will instead create a temporary file,
render the PNG, and then call the default viewer.

Requires graphviz and a graphical viewer to be installed.


make-graph-file
******************

Make a graphviz DOT file (https://graphviz.org/documentation/) containing a graph
that describes what files go into a basis set. Optionally takes a version of the basis
set.

If ``--render`` is passed, a PNG file will also be created.

.. command-output:: bsecurate make-graph-file 6-31g graph_631g.dot
.. command-output:: cat graph_631g.dot
