.. _bse_cli:

The bse command line interface
==============================================

The basis set exchange package contains a command-line interface called
``bse``. This command can be used to obtain/print basis sets and references,
as well as query the library for information and metadata.


.. _cliinstall:

Installation
------------

The command line is automatically installed when the library is installed
via ``pip`` or similar python package managers.

Depending on how packages are installed, you may need to add the path to
the ``bse`` program to the PATH environment variable.


TAB completion
--------------

Tab completion is available for the bash interpreter and is tremendously useful.
If enabled, TAB autocompletion will be enabled for

  * Directories
  * Arguments (``--elements``, etc)
  * Basis set names
  * Basis set families
  * Roles
  * Basis set formats and reference formats

Autocompletion is implemented via the **argcomplete** library (https://argcomplete.readthedocs.io).
TAB completion can be enabled one of two ways:

  * Run ``eval "$(register-python-argcomplete bse)"`` on the command line
  * Enable globally by running ``activate-global-python-argcomplete`` and
    then sourcing ``~/.bash_completion.d/python-argcomplete.sh`` manually or in ``.bashrc``.

The first method must be run every time a new terminal is opened.
For the second method, you can change the path where the ``python-argcomplete.sh`` script is installed.

For more details, see the documentation for **argcomplete**
(particularly `here <https://argcomplete.readthedocs.io/en/latest/#synopsis>`__
and `here <https://argcomplete.readthedocs.io/en/latest/#global-completion>`__)

Note that both the ``register-python-argcomplete`` and ``activate-global-python-argcomplete`` are part
of the python **argcomplete** package and you may need to add the path manually to the PATH
environment variable.


General usage
--------------

The ``bse`` command is generally followed by a subcommand (see below). ``bse -h`` will display help
and ``bse -V`` will display the version and exit.

.. command-output:: bse -h


In general, values provided to options (such as basis set names, formats, and elements) are
not case sensitive.

There are two global options available to all subcommands. The first is an alternate
data directory can be specified with ``-d`` or ``--data-dir``. By default, the built-in
data directory will be used.

.. command-output:: bse -d ${HOME}/my_data_dir list-basis-sets

Also, output can be written to a file rather than to the terminal

.. command-output:: bse -o /tmp/my_out_file list-basis-sets
.. command-output:: cat /tmp/my_out_file
   :ellipsis: 3


Element strings
***************

Some subcommands take a string specifying which elements the subcommand will work with. This
string is a comma-separated list of element symbols and/or Z numbers. Ranges can also be used.

Symbols are not case sensitive and can be mixed with Z-numbers.

Examples:
    * ``H-Ne`` - for hydrogen through neon (inclusive)
    * ``1-10`` - same as above
    * ``C,8,p-17`` - carbon, oxygen, phosphorus through chlorine


Subcommands
-------------------

Below is a list of the available subcommands. All subcommands
can take the ``-h`` option to display help for that subcommand.

.. command-output:: bse get-basis -h
   :ellipsis: 8


list-formats
*******************

Lists the available output formats of basis sets.
With ``-n`` or ``--no-description``, the command will hide the description of the formats.

.. command-output:: bse list-formats
.. command-output:: bse list-formats -n


list-ref-formats
*******************

Lists the available output formats of references.
With ``-n`` or ``--no-description``, the command will hide the description of the formats.

.. command-output:: bse list-ref-formats
.. command-output:: bse list-ref-formats -n


list-writer-formats
*******************

Print a list of the formats that can be written to by the library

.. command-output:: bse list-writer-formats


list-reader-formats
*******************

Print a list of the formats that can be read by the library

.. command-output:: bse list-reader-formats


list-roles
*******************

Lists the available basis set roles. Takes no arguments

.. command-output:: bse list-roles


get-data-dir
*******************

Print the default data directory (built into the BSE package)

.. command-output:: bse get-data-dir


list-basis-sets
*******************

Lists the available basis sets.
This command respects the ``--data-dir`` option.
With ``-n`` or ``--no-description``, the command will hide the description of the basis set.

.. command-output:: bse list-basis-sets
   :ellipsis: 3

Basis sets can be filtered by role, family, or by arbitrary search string (case insensitive).
See `list-roles`_ and `list-families`.

.. command-output:: bse list-basis-sets -r jfit
   :ellipsis: 3

.. command-output:: bse list-basis-sets -f pople -s '31g'
   :ellipsis: 3


list-families
*******************

List all basis set families.
This command respects the ``--data-dir`` option.

.. command-output:: bse list-families
   :ellipsis: 5


lookup-by-role
*******************

Find the name of an auxiliary basis set given the primary basis and the desired role.

.. command-output:: bse lookup-by-role def2-tzvp jfit


get-basis
*******************

Print a formatted basis set from the library.
This command has several options. See ``bse get-basis -h`` for a complete list.

This subcommand takes two required arguments: the name of the basis set
and the format. See `list-basis-sets`_ and `list-formats`_.

The main popular option is ``--elements`` which takes an element string. See `Element strings`_.
By default, all elements for which the basis set is defined are included.

A version of the basis set can be specified with ``--version``.
See `get-versions`_ for how to list versions available for a basis set.

By default, a descriptive header is included. This may be disabled with ``--noheader``

Some examples:

.. command-output:: bse get-basis sto-3g nwchem
   :ellipsis: 20

.. command-output:: bse get-basis sto-3g gaussian94 --noheader
   :ellipsis: 20

.. command-output:: bse get-basis sto-3g gaussian94 --elements C,7,11-13 --noheader
   :ellipsis: 10

.. command-output:: bse get-basis cc-pvtz nwchem --noheader --version 0 --elements C --make-gen
   :ellipsis: 10


get-refs
*******************

Print formatted reference info for a basis set.

This subcommand takes two required arguments: the name of the basis set,
and the desired reference format. See `list-basis-sets`_ and `list-ref-formats`_. 

Elements can be restricted with ``--elements``. See `Element strings`_.
By default, all elements for which the basis set is defined are included.

A version of the basis set can be specified with ``--version``.
See `get-versions`_ for how to list versions available for a basis set.

.. command-output:: bse get-refs def2-tzvp --elements 1 bib


get-info
*******************

Print some metadata about a basis set.
This takes only one required argument (the name of the basis set).

.. command-output:: bse get-info cc-pvdz


get-notes
*******************

Print the notes about a basis set.
This takes only one required argument (the name of the basis set).

.. command-output:: bse get-notes sto-3g


get-family
*******************

Get the family of the basis set.
This takes only one required argument (the name of the basis set).

.. command-output:: bse get-family cc-pvtz-rifit


get-versions
*******************

Get the available versions of a basis set.
This takes only one required argument (the name of the basis set).

With ``-n`` or ``--no-description``, the command will hide the description of the version.

.. command-output:: bse get-versions aug-cc-pvtz
.. command-output:: bse get-versions aug-cc-pvtz -n


get-family-notes
*******************

Print the notes about a basis set family. This takes only one required argument (the basis set family).

.. command-output:: bse get-family-notes sto
   :ellipsis: 10


create-bundle
*******************

See :ref:`bundles`


convert-basis
*******************

See :ref:`conversion`
