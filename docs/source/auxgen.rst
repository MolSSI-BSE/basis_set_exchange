.. _auxgen:

Automatic auxiliary basis set generation
========================================

The :mod:`basis_set_exchange.auxgen` subpackage implements the
pivoted-Cholesky procedure for automatically generating a primitive
auxiliary (density-fitting / resolution-of-the-identity) basis set
from a given orbital basis, following

* S. Lehtola, *Straightforward and accurate automatic auxiliary basis
  set generation for molecular calculations with atomic orbital basis
  sets*, J. Chem. Theory Comput. **17**, 6886 (2021),
  https://doi.org/10.1021/acs.jctc.1c00607.
* S. Lehtola, *Automatic generation of accurate and cost-efficient
  auxiliary basis sets*, J. Chem. Theory Comput. **19**, 6242 (2023),
  https://doi.org/10.1021/acs.jctc.3c00670.

The closed-form one-center Coulomb integrals are taken from R. M. Pitzer,
*Atomic self-consistent-field program by the basis set expansion
method: Columbus version*, Comput. Phys. Commun. **170**, 239 (2005),
https://doi.org/10.1016/j.cpc.2005.04.003.

The generated basis is written in the standard BSE component-format
schema; any of the format writers available in the rest of the library
can therefore be used to emit the result.


Algorithm overview
------------------

For each element the orbital basis is decontracted to primitives
:math:`\chi_\mu(r) = r^{n_\mu} Y_{l_\mu m_\mu}(\hat r)\,e^{-\alpha_\mu r^2}`.
Spherical and Cartesian shells are both accepted: a Cartesian shell of
nominal angular momentum :math:`L` contributes spherical components at
:math:`l = L, L-2, \ldots,` all sharing the same radial power
:math:`n = L`.  ECP entries on the element are ignored.

For every unordered pair of primitives :math:`(\mu, \nu)` (with the
diagonal :math:`\mu = \nu` included) and every
angular momentum :math:`L \in \{|l_\mu - l_\nu|, |l_\mu - l_\nu| + 2,
\ldots, l_\mu + l_\nu\}` (real-Gaunt parity), a candidate auxiliary
function is generated.  The product radial form
:math:`r^{n_\mu + n_\nu} e^{-(\alpha_\mu + \alpha_\nu) r^2}` is mapped
to a standard primitive :math:`r^L e^{-\alpha_{\rm eff} r^2}` using the
``<r>``-matching transformation of the 2021 paper (Appendix II eq 16),

.. math::

   \alpha_{\rm eff} = \left[
     \frac{\Gamma(L+2)\,\Gamma(n_{\rm rad}+\tfrac{3}{2})}
          {\Gamma(L+\tfrac{3}{2})\,\Gamma(n_{\rm rad}+2)}
   \right]^2 (\alpha_\mu + \alpha_\nu),

with :math:`n_{\rm rad} = n_\mu + n_\nu`.  The candidates are then
gathered per :math:`L` into a Coulomb-overlap metric (paper eq 7),
normalized to unit diagonal, and thinned by pivoted Cholesky.

Two variants of the four-index pre-screening are supported:

* ``scheme='basic'``: every primitive pair is taken as a candidate.
* ``scheme='reduced'`` *(default)*: shell-pair-driven pivoted Cholesky
  of the four-index ``(μν|ρσ)`` tensor is performed first to thin the
  list of contributing orbital shell-pairs.  Within a chosen
  shell-pair, all m-resolved components are added together as in the
  ERKALE implementation.

To make the most of the unit-diagonal candidate metric (where the
first pivot is degenerate), each :math:`L` block runs pivoted Cholesky
under three ordering families and keeps the shortest pivot set:

1. linear order (insertion order of the candidates),
2. increasing off-diagonal-norm presort (paper Sect. 3),
3. ``n_random`` independent random permutations (the Note Added in
   Proof of the 2021 paper).

The drop tolerance ``τ`` is applied directly to the residual diagonal
of the Cholesky factorisation (absolute threshold).

Two optional refinements from the 2023 paper are available (both on by
default):

* ``contract=True`` applies the SVD-based general contraction
  (Section 2.1 of the 2023 paper).  Per :math:`l`, the three-index
  integrals :math:`I_{\mu\nu, A} = (\mu\nu | A)` and the two-index
  Coulomb metric :math:`V_{AB} = (A|B)` are formed; the primitives are
  Coulomb-normalized (so the work is done in the well-conditioned
  unit-diagonal metric :math:`S = D^{-1} V D^{-1}` rather than the
  ill-conditioned raw metric), :math:`S` is symmetrically
  orthogonalized, and :math:`W = I^T I` is diagonalized in that basis.
  Eigenvectors with eigenvalue above the threshold ``ε`` define general
  contractions, written in the overlap-normalized primitive convention
  used by basis-set libraries via ERKALE's
  :math:`c = \mathrm{Wvec} \cdot \sqrt{z}` rescaling.
* ``prune_lmax=True`` drops shells above the
  :math:`l_{\rm keep} = \max(2 l_{\rm occ}^{\max},
  l_{\rm occ}^{\max} + l_{\rm OBS}^{\max} + l_{\rm inc})` cap of the
  2023 paper, eq 9.  The default :math:`l_{\rm occ}^{\max}` follows
  the row-based table of the paper (0 for H/He, 1 for
  :math:`Z \le 18`, 2 for :math:`Z \le 54`, 3 otherwise).

The ``size`` argument selects the standard accuracy presets of the 2023
paper, overriding ``contract_threshold`` (``ε``) and ``linc``:
``verylarge`` = :math:`(\epsilon, l_{\rm inc}) = (10^{-6}, 1)`,
``large`` = :math:`(10^{-5}, 1)`, ``small`` = :math:`(10^{-4}, 0)`.

Two further options control how each candidate orbital product is mapped
to a standard auxiliary primitive, and how the orbital basis itself is
fed into the selection candidate pool:

* ``mapping`` selects the criterion for the
  :math:`(n_{\rm rad}, \alpha_{\rm rad}) \to \alpha_{\rm eff}`
  transformation in the candidate pool: ``'moment'`` *(default)*
  preserves the radial expectation value :math:`\langle r \rangle`
  (the 2021 paper, Appendix II); ``'selfrepulsion'`` preserves the
  Coulomb self-energy :math:`(i|i)` of the (overlap-normalized) candidate
  and standard primitive.  Both reduce to :math:`\alpha_{\rm eff} =
  \alpha_{\rm rad}` when :math:`n_{\rm rad} = L`.

* ``collapse_contractions`` *(opt-in, default ``False``)* replaces each
  contracted orbital function by a single primitive before building the
  candidate pool (free primitives are kept; the contraction step still
  uses the true contracted AOs).  Values: ``'moment'`` matches the
  radial expectation value of the contracted function;
  ``'selfrepulsion'`` matches its orbital Coulomb self-energy
  :math:`(\chi\chi|\chi\chi)`.  Both have closed-form solutions and
  reduce to :math:`\beta = \alpha` for a single-primitive contraction.


Command-line interface
----------------------

The ``bse autogen-aux`` subcommand reads an orbital basis from a file
and writes the generated auxiliary basis to a file::

    bse autogen-aux <input_file> <output_file>
        [--in-fmt FMT] [--out-fmt FMT]
        [--threshold 1e-7]
        [--scheme {basic,reduced}]
        [--n-random 100] [--seed 0]
        [--mapping {moment,selfrepulsion}]
        [--collapse-contractions {moment,selfrepulsion}]
        [--size {small,large,verylarge}]
        [--contract | --no-contract] [--contract-threshold 1e-5]
        [--prune-lmax | --no-prune-lmax] [--linc 1]

Input and output formats are auto-detected from the file extension
unless overridden.  All standard BSE writers (NWChem, Molcas, Psi4,
Turbomole, JSON, ...) are accepted on the output side.

Example: build an auxiliary basis for hydrogen, carbon, and oxygen
from cc-pVDZ at a tight :math:`\tau = 10^{-7}` tolerance::

    bse get-basis cc-pVDZ nwchem --elements H,C,O > /tmp/ccpvdz.nw
    bse autogen-aux /tmp/ccpvdz.nw /tmp/ccpvdz_aux.nw --threshold 1e-7

Contraction and lmax pruning are applied by default; build the
``small`` standard preset instead::

    bse autogen-aux /tmp/ccpvdz.nw /tmp/ccpvdz_aux_small.nw --size small

or generate the uncontracted primitive auxiliary basis::

    bse autogen-aux /tmp/ccpvdz.nw /tmp/ccpvdz_aux_prim.nw \
        --no-contract --no-prune-lmax


Python API
----------

The high-level entry point produces a BSE component-format basis dict:

.. code-block:: python

    import basis_set_exchange as bse
    from basis_set_exchange.auxgen import generate_auxiliary_basis

    orbital = bse.get_basis('cc-pVDZ', elements=[1, 6, 8])

    aux = generate_auxiliary_basis(
        orbital,
        threshold=1.0e-7,
        scheme='reduced',
        n_random=100,
        # contract and prune_lmax default to True; pass False to disable.
    )

    # `aux` is a dict in the BSE component schema; emit any format:
    print(bse.write_formatted_basis_str(aux, 'nwchem'))

The size presets can also be reached straight from
:func:`basis_set_exchange.get_basis` via the ``get_aux`` integer code,
which goes through the same code path:

.. code-block:: python

    aux_small     = bse.get_basis('cc-pVDZ', elements=[6], get_aux=3)
    aux_large     = bse.get_basis('cc-pVDZ', elements=[6], get_aux=4)
    aux_verylarge = bse.get_basis('cc-pVDZ', elements=[6], get_aux=5)

(``get_aux=1`` and ``2`` remain the legacy AutoAux / Auto-ABS variants.)
Modes ``3-5`` require ``numpy`` at runtime, plus ``wignernj`` (preferred)
or ``sympy`` for the Gaunt evaluator; the rest of the package has no
optional-import requirements.

A per-element entry point is also exported for use cases that already
have an element dict to hand:

.. code-block:: python

    from basis_set_exchange.auxgen.auxgen import (
        generate_auxiliary_basis_for_element,
    )

    aux_c = generate_auxiliary_basis_for_element(
        orbital['elements']['6'],
        threshold=1.0e-7,
        scheme='reduced',
    )


Parameters
----------

.. list-table::
   :header-rows: 1
   :widths: 22 12 66

   * - Parameter
     - Default
     - Description
   * - ``threshold``
     - ``1e-7``
     - Pivoted-Cholesky drop tolerance :math:`\tau` (absolute, applied
       to the residual diagonal).  The same tolerance is used for the
       four-index pre-screening (reduced scheme) and the per-L
       candidate Cholesky.
   * - ``scheme``
     - ``'reduced'``
     - ``'basic'`` enumerates all orbital primitive pairs as
       candidates; ``'reduced'`` first thins them with a shell-pair-
       driven pivoted Cholesky of the four-index ERI tensor.  The
       2023 paper recommends ``'reduced'``.
   * - ``n_random``
     - ``100``
     - Number of random orderings tried in the per-L candidate
       Cholesky.  In addition the linear order and the off-diagonal-
       norm presort are always tried; the smallest pivot set across
       all attempts is kept.  Setting ``n_random = 0`` reproduces the
       paper's deterministic baseline.
   * - ``seed``
     - ``0``
     - Seed for the random orderings, for reproducibility.
   * - ``contract``
     - ``True``
     - Apply the SVD-based general contraction of the 2023 paper.
   * - ``contract_threshold``
     - ``1e-5``
     - Eigenvalue cutoff :math:`\epsilon` for keeping contractions
       (matches the ``large`` size preset).
   * - ``prune_lmax``
     - ``True``
     - Drop shells with :math:`L > l_{\rm keep}` per the 2023 paper
       eq 9.
   * - ``linc``
     - ``1``
     - Increment :math:`l_{\rm inc}` in the pruning rule.


STO (Slater-type-orbital) driver
--------------------------------

The companion module :mod:`basis_set_exchange.auxgen.sto` runs the same
pivoted-Cholesky procedure for STO orbital bases, using Pitzer's
closed-form one-centre Slater two-electron radial integral instead of
the Gaussian one.  Primitives are
:math:`\chi_{n L M}(r) = r^{n - 1} e^{-\zeta r}\,Y_{L M}(\hat r)` with
integer ``n >= L + 1``; the I/O format mirrors what ADF ships in
``atomicdata/ZORA/``.

Python:

.. code-block:: python

    from basis_set_exchange.auxgen.sto import (
        generate_sto_auxiliary_basis, sto_diagonal_ri_error,
    )

    # Per-element STO orbital basis: {L: [(n, zeta), ...]}.
    orbital = {0: [(1, 0.76), (1, 1.28)]}            # Hydrogen DZ
    aux = generate_sto_auxiliary_basis(orbital, threshold=1.0e-7)

    err = sto_diagonal_ri_error(orbital, aux)
    print('total diagonal RI error =', err)

By default each candidate keeps its natural radial power
``n_aux = n_a + n_b - 1`` from the orbital product (so a Cholesky
selection on a typical orbital basis emits 1S/2S/3S/..., 2P/3P/...,
3D/4D/... at every L, like standard STO aux sets).  Pass
``compact=True`` to collapse every candidate onto the minimum-power
form ``n_aux = L + 1`` via the ``<r>``-matching map
:func:`~basis_set_exchange.auxgen.sto.sto_zeta_eff`.  Pass
``prune_lmax=True`` together with ``lmax_occ=<int>`` to apply the same
:math:`l_{\rm keep}` cap as the GTO driver.

The module also includes a small ADF basis-file reader/writer and a
``main()`` entry point:

.. code-block:: bash

    # Run as a script (`-m` invocation also works):
    python -m basis_set_exchange.auxgen.sto Fe Fe_new.adf --threshold 1e-7

    # Available flags
    #   --threshold TAU            Cholesky drop tolerance (default 1e-7)
    #   --scheme {basic,reduced}   default reduced
    #   --n-random N --seed S      randomised pivot orderings
    #   --prune-lmax [--linc N] [--lmax-occ N]
    #   --compact                  collapse to n = L+1 via <r>-matching
    #   --no-benchmark             skip the diagonal-RI-error reports

The driver reports the diagonal RI error of both the old (incoming)
and the new (regenerated) FIT block for direct comparison.  The output
file preserves the BASIS, CORE and DESCRIPTION sections from the
source; the FITCOEFFICIENTS block is *dropped* because it refers to
the old FIT exponents.


Notes
-----

* The generated auxiliary basis is always spherical; this matches the
  convention adopted by the 2021 paper and by most quantum chemistry
  programs.  Cartesian input shells are supported (with their radial
  contamination correctly tracked) but produce spherical output.
* Sympy is used only for the real-spherical Gaunt coefficients in
  :mod:`basis_set_exchange.auxgen.gaunt`, and is lazy-imported.  The
  radial integrals are evaluated with a pure closed form (no sympy at
  runtime).
* The PySCF-based test
  ``basis_set_exchange/tests/test_auxgen.py::test_eri_full_tensor_vs_pyscf_spd``
  cross-checks every one-center primitive ``(ab|cd)`` integral over
  an s/p/d basis against ``libcint`` to machine precision.
* The base package has no runtime dependencies.  Using
  :mod:`~basis_set_exchange.auxgen` requires ``numpy``, plus either
  ``wignernj`` (preferred, exact integer arithmetic) or ``sympy`` for
  the Gaunt evaluator -- both are lazy-imported on first call.
