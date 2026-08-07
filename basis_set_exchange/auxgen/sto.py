# Copyright (c) 2026 Susi Lehtola
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
Slater-type-orbital (STO) variant of the Cholesky aux-basis driver.

A primitive STO is parameterised by a principal quantum number ``n``
(integer, ``n >= L + 1``), an angular momentum ``L``, and an exponent
``zeta``:

    chi_{n L M}(r) = r^(n - 1) e^(-zeta r) Y_{L M}(theta, phi).

The driver implements the pivoted-Cholesky procedure of Lehtola,
J. Chem. Theory Comput. 17, 6886 (2021)
[https://doi.org/10.1021/acs.jctc.1c00607] with the closed-form
one-centre two-electron Slater radial integral of R. M. Pitzer,
Comput. Phys. Commun. 170, 239 (2005)
[https://doi.org/10.1016/j.cpc.2005.04.003] (matching the openorbital
``AtomicSolver`` convention used by ``STOBasis``):

    R^v_{m n}(x, y) = Gamma(m + n) / [x y (x + y)^(m + n - 1)]
                      * (1 + E_{m+n-1, n - v - 1}(y/x)
                            + E_{m+n-1, m - v - 1}(x/y))

reusing the ``E`` polynomial from :mod:`.radial` (it is valid for both
integer and half-integer arguments).

Candidate auxiliary primitives have the natural radial form
``r^(n_aux - 1) e^(-zeta_aux r) Y_{L M}`` with
``n_aux = n_a + n_b - 1`` and ``zeta_aux = zeta_a + zeta_b``, preserving
the radial character of the underlying orbital product
``chi_a * chi_b`` -- standard STO aux sets routinely include 2S, 3S,
3D, 4D, ... at every L, and a collapse onto the minimum-power form
``n_aux = L + 1`` would discard exactly that high-n character.  The
opt-in :func:`generate_sto_auxiliary_basis` ``compact=True`` mode does
perform the collapse (via the ``<r>``-matching map
:func:`sto_zeta_eff`) for users who want a single-radial-power aux
basis.

The driver handles primitive STOs only (no contractions); the
candidate pool and per-L selection are angular-momentum-resolved
exactly as in the GTO path.
"""

import sys
from math import gamma, sqrt, pi

# Support both ``python -m basis_set_exchange.auxgen.sto`` and the bare
# ``python .../auxgen/sto.py``: when invoked as a top-level script the
# relative imports below would fail, so we put the package root on
# ``sys.path`` and fix up ``__package__`` first.
if __name__ == '__main__' and __package__ in (None, ''):
    import os
    _here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.abspath(os.path.join(_here, '..', '..')))
    __package__ = 'basis_set_exchange.auxgen'

import numpy as np

from .. import lut
from .gaunt import coupling_lvals, gaunt_table
from .radial import _Enk
from .products import _shellpair_L_range, orbital_shell_pairs
from .twoel import _iter_nonzero_gaunt, coupled_shell_pair_screen


# ---------------------------------------------------------------------------
# Closed-form one-centre integrals
# ---------------------------------------------------------------------------

def sto_norm(n, zeta):
    """Overlap norm constant ``N`` such that
    ``chi(r) = N r^(n - 1) e^(-zeta r) Y_LM`` has ``<chi|chi> = 1``,
    i.e. ``N = sqrt((2 zeta)^(2 n + 1) / Gamma(2 n + 1))``.
    """
    return sqrt((2.0 * float(zeta)) ** (2 * n + 1) / gamma(2 * n + 1))


def sto_norm_array(n, zetas):
    z = np.asarray(zetas, dtype=float)
    return np.sqrt((2.0 * z) ** (2 * n + 1) / gamma(2 * n + 1))


def sto_radial_coulomb(m, n, v, x, y):
    """Pitzer/openorbital one-centre two-electron STO radial integral.

    ``m``, ``n``, ``v`` are integers; ``x``, ``y`` are positive scalars
    or broadcast-compatible numpy arrays.

    For an aux-metric integral ``(a|b)_L`` over two single STO functions
    of principal quantum numbers ``N_a, N_b`` and exponents
    ``zeta_a, zeta_b`` at multipole ``L`` use
    ``(m, n, v, x, y) = (N_a + 1, N_b + 1, L, zeta_a, zeta_b)``.  For an
    orbital-pair integral ``(chi_i chi_j | chi_k chi_l)`` at multipole
    ``L`` use ``(N_i + N_j, N_k + N_l, L, zeta_i + zeta_j,
    zeta_k + zeta_l)``.

    The full Coulomb matrix element is obtained by multiplying with the
    ``4 pi / (2 L + 1)`` angular factor and the real-Gaunt coefficient(s).
    """
    if np.isscalar(x) and np.isscalar(y) and (x <= 0.0 or y <= 0.0):
        return 0.0
    half = m + n - 1                # always a positive integer for STOs
    return (gamma(m + n) / (x * y * (x + y) ** half) *
            (1.0 + _Enk(half, n - v - 1, y / x)
                 + _Enk(half, m - v - 1, x / y)))


# ---------------------------------------------------------------------------
# One-electron one-centre matrix elements (Pitzer/openorbital STO forms)
# ---------------------------------------------------------------------------
#
# These differ from the GTO formulas (which live in radial.py / twoel.py);
# they are provided here so the STO driver and tests have a fully
# self-contained closed-form kit and never accidentally mix GTO kernels
# with STO basis data.  The basis functions below are taken in the
# *un-normalised* form chi = r^(n - 1) e^(-zeta r) Y_LM; multiply by
# sto_norm(n, zeta) for either index to obtain matrix elements in the
# normalised basis.

def _Vn(n, x):
    """Pitzer helper ``V_n(x) = Gamma(n + 1) / x^(n + 1)`` (the radial
    integral ``int_0^inf r^n e^(-x r) dr``).
    """
    return gamma(n + 1) / x ** (n + 1)


def _Wn(n, x):
    """Pitzer helper ``W_n(x) = (n - 1) / x`` (logarithmic-derivative
    helper in the kinetic-energy expression).
    """
    return (n - 1) / x


def sto_overlap_matrix(items):
    """``S_ij = <chi_i | chi_j>`` over un-normalised STO primitives
    ``chi = r^(n - 1) e^(-zeta r) Y_LM``.  Angular-momentum independent
    (the Y_LM ON-condition only requires the bra/ket share L,M, which is
    the caller's responsibility); ``items`` is ``[(n, zeta), ...]``.
    """
    n_items = len(items)
    S = np.zeros((n_items, n_items), dtype=float)
    for i, (ni, zi) in enumerate(items):
        for j in range(i, n_items):
            nj, zj = items[j]
            # Openorbital STOBasis::overlap, Pitzer p. 244.
            v = _Vn(ni + nj, zi + zj)
            S[i, j] = S[j, i] = v
    return S


def sto_nuclear_attraction_matrix(items):
    """``+<chi_i | 1/r | chi_j>`` over un-normalised STO primitives at
    a single angular momentum (sign convention: positive; multiply by
    ``-Z`` for the physical nuclear-attraction matrix at nuclear charge
    ``Z``).
    """
    n_items = len(items)
    V = np.zeros((n_items, n_items), dtype=float)
    for i, (ni, zi) in enumerate(items):
        for j in range(i, n_items):
            nj, zj = items[j]
            # Openorbital STOBasis::nuclear_attraction, Pitzer p. 244.
            v = _Vn(ni + nj - 1, zi + zj)
            V[i, j] = V[j, i] = v
    return V


def sto_kinetic_matrix(L, items):
    """``T_ij = <chi_i | -1/2 nabla^2 | chi_j>`` over un-normalised STO
    primitives at angular momentum ``L``.  Closed form from
    openorbital ``STOBasis::kinetic`` / Pitzer p. 244::

        T_ij = 0.5 zeta_i zeta_j [
                 W(n_i - L, zeta_i) W(n_j - L, zeta_j) V(n_i + n_j - 2, z)
               - (W(n_i - L, zeta_i) + W(n_j - L, zeta_j)) V(n_i + n_j - 1, z)
               + V(n_i + n_j, z)
               ],

    with ``z = zeta_i + zeta_j``.
    """
    n_items = len(items)
    T = np.zeros((n_items, n_items), dtype=float)
    for i, (ni, zi) in enumerate(items):
        Wi = _Wn(ni - L, zi)
        for j in range(i, n_items):
            nj, zj = items[j]
            Wj = _Wn(nj - L, zj)
            z = zi + zj
            t = 0.5 * zi * zj * (
                Wi * Wj * _Vn(ni + nj - 2, z)
                - (Wi + Wj) * _Vn(ni + nj - 1, z)
                + _Vn(ni + nj, z)
            )
            T[i, j] = T[j, i] = t
    return T


# ---------------------------------------------------------------------------
# Aux metric on STO standard primitives at a single L
# ---------------------------------------------------------------------------

def sto_aux_metric_overlap_norm(L, items):
    """``(P|Q)`` between *overlap*-normalised STO primitives sharing the
    same ``L`` (and ``M``).  Each primitive ``chi_P = sto_norm(n_P, z_P)
    * r^(n_P - 1) e^(-z_P r) Y_LM`` satisfies ``<chi_P|chi_P> = 1``;
    in this convention the metric diagonal is *not* unity.

    Provided for completeness / diagnostics.  The Cholesky selection and
    the orbital-aux projection both use the Coulomb-normalised variant
    (:func:`sto_aux_metric`).
    """
    n_items = len(items)
    if n_items == 0:
        return np.zeros((0, 0), dtype=float)
    M = np.zeros((n_items, n_items), dtype=float)
    fourpi_2Lp1 = 4.0 * pi / (2 * L + 1)
    for i, (na, za) in enumerate(items):
        Na = sto_norm(na, za)
        for j in range(i, n_items):
            nb, zb = items[j]
            Nb = sto_norm(nb, zb)
            rad = sto_radial_coulomb(na + 1, nb + 1, L, float(za), float(zb))
            v = Na * Nb * fourpi_2Lp1 * rad
            M[i, j] = v
            M[j, i] = v
    return M


def _coulomb_rescale_factors(V_overlap):
    """``s_P = 1 / sqrt((P|P)_overlap)`` for converting an overlap-
    normalised aux primitive to a Coulomb-normalised one
    (``(P|P)_Coulomb = 1``).  Returns ``zeros`` for an empty matrix.
    """
    if V_overlap.size == 0:
        return np.zeros(0, dtype=float)
    return 1.0 / np.sqrt(np.diag(V_overlap))


def sto_aux_metric(L, items):
    """``(P|Q)`` between *Coulomb*-normalised STO primitives at angular
    momentum ``L``: each primitive carries an extra rescaling so that
    ``(P|P) = 1``.  This is the convention used for auxiliary functions
    throughout the auxgen pipeline (Lehtola JCTC 17, 6886 (2021), eq 7)
    and yields a unit-diagonal metric.
    """
    M = sto_aux_metric_overlap_norm(L, items)
    if M.size == 0:
        return M
    s = _coulomb_rescale_factors(M)
    return M * np.outer(s, s)


# ---------------------------------------------------------------------------
# Optional collapse onto the minimum-radial-power form (compact mode)
# ---------------------------------------------------------------------------

def sto_zeta_eff(L, n_rad, zeta_rad):
    """Effective exponent for the minimum-radial-power STO standard
    primitive ``r^L e^(-zeta_eff r) Y_LM`` whose normalised radial
    expectation value ``<r>`` matches that of the natural candidate
    ``r^(n_rad - 1) e^(-zeta_rad r)``.

    Derivation: for a normalised STO ``r^(N - 1) e^(-zeta r) Y_LM``,
    ``<r> = (2 N + 1) / (2 zeta)``.  Equating ``<r>`` for the natural
    candidate (``N = n_rad``) and the standard primitive
    (``N = L + 1``) gives
    ``zeta_eff = (2 L + 3) * zeta_rad / (2 n_rad + 1)``.  When
    ``n_rad = L + 1`` this reduces to ``zeta_eff = zeta_rad``.

    Only used by the opt-in ``compact=True`` mode of
    :func:`generate_sto_auxiliary_basis`; the default mode preserves
    the natural radial power.
    """
    if n_rad < L + 1:
        raise ValueError("sto_zeta_eff: n_rad=%d incompatible with L=%d"
                         % (n_rad, L))
    return (2 * L + 3) * float(zeta_rad) / (2 * n_rad + 1)


# ---------------------------------------------------------------------------
# Candidate pool construction
# ---------------------------------------------------------------------------
#
# Unlike GTOs, where the spherical standard primitive ``r^L e^(-alpha r^2)``
# has the same radial power as a (spherical) orbital product, an STO
# orbital product ``chi_a * chi_b`` has natural radial power
# ``n_a + n_b - 2`` which is *almost always* larger than the minimum
# ``L``.  By default we keep the natural ``n`` (so the candidate pool
# carries the same radial richness as standard STO aux sets, which
# routinely include 2S, 3S, 3D, 4D, ... at every L); the opt-in
# ``compact=True`` mode collapses every candidate onto ``n_aux = L + 1``
# via :func:`sto_zeta_eff` for users who want a single-radial-power
# aux basis.

def sto_decontract(sto_basis):
    """Validate and flatten an STO-basis dict to a list of unique
    ``(l, n, zeta)`` triples sorted by ``(l, n, -zeta)``.

    ``sto_basis`` is ``{L: [(n, zeta), ...]}``; an iterable of
    ``(L, n, zeta)`` triples is also accepted.
    """
    if isinstance(sto_basis, dict):
        triples = ((L, n, z) for L, items in sto_basis.items()
                              for (n, z) in items)
    else:
        triples = sto_basis
    seen = set()
    for (L, n, z) in triples:
        L, n = int(L), int(n)
        if n < L + 1:
            raise ValueError(
                "STO primitive (n=%d, l=%d) violates n >= l + 1" % (n, L))
        seen.add((L, n, float(z)))
    return sorted(seen, key=lambda t: (t[0], t[1], -t[2]))


def sto_candidate_pool_from_primitives(primitives):
    """Build the per-L STO candidate pool from a list of primitive
    triples ``(l, n, zeta)`` (output of :func:`sto_decontract`).

    For every unordered pair of primitives and every parity-allowed
    coupling angular momentum ``L``, the orbital product
    ``chi_a * chi_b`` has natural form ``r^(n_a + n_b - 2) e^(-(z_a + z_b) r)``
    and contributes a candidate ``(n_aux = n_a + n_b - 1, zeta_aux = z_a + z_b)``
    at every parity-allowed ``L``.  This preserves the natural
    radial power -- unlike the GTO case, an ``<r>``-matching collapse
    onto ``n_aux = L + 1`` would discard exactly the high-n character
    that standard STO aux sets need.

    Returns ``{L: [(n_aux, zeta_aux), ...]}`` sorted by ``(n_aux,
    -zeta_aux)``, with duplicates collapsed to ten decimal places of
    ``zeta``.
    """
    pool = {}
    n = len(primitives)
    for i in range(n):
        la, na, za = primitives[i]
        for j in range(i, n):
            lb, nb, zb = primitives[j]
            n_aux = na + nb - 1
            z_aux = float(za + zb)
            for L in _shellpair_L_range(la, lb):
                pool.setdefault(L, []).append((n_aux, z_aux))
    return _dedupe_pool(pool)


def _dedupe_pool(pool):
    """Dedupe each ``{L: [(n, zeta), ...]}`` pool list at ten decimal
    places of ``zeta`` *per ``n``*, and emit lists sorted by
    ``(n, -zeta)``.
    """
    out = {}
    for L, items in pool.items():
        seen = {}
        for (n, z) in items:
            seen[(int(n), round(float(z), 10))] = (int(n), float(z))
        out[L] = sorted(seen.values(), key=lambda nz: (nz[0], -nz[1]))
    return out


def _compact_pool(pool):
    """Project a ``{L: [(n, zeta), ...]}`` pool onto the minimum-radial-
    power form ``n = L + 1`` using the ``<r>``-matching map
    :func:`sto_zeta_eff`.  Dedupes after projection.
    """
    out = {}
    for L, items in pool.items():
        zetas = [sto_zeta_eff(L, n, z) for (n, z) in items]
        seen = {}
        for z in zetas:
            seen[round(float(z), 10)] = float(z)
        n_aux = L + 1
        out[L] = [(n_aux, z) for z in sorted(seen.values(), reverse=True)]
    return out


# ---------------------------------------------------------------------------
# Reduced-scheme coupled-basis Cholesky pre-screening
# ---------------------------------------------------------------------------


def _sto_radial_fn(L, n_ab, n_cd, z_ab, z_cd):
    """Adapter matching the ``(L, n_ab, n_cd, exp_ab, exp_cd)`` convention
    expected by :func:`twoel.coupled_L_metric` -- the STO closed form
    :func:`sto_radial_coulomb` orders its arguments as ``(m, n, v, x, y)``.
    """
    return sto_radial_coulomb(n_ab, n_cd, L, z_ab, z_cd)


def sto_orbital_aux_projection(L, primitives, items):
    """STO analogue of :func:`twoel.orbital_aux_projection`: build the
    aux-aux metric and the three-index projection of m-resolved orbital
    product densities onto a set of STO aux primitives at a single
    angular momentum ``L``.

    Convention: orbital primitives ``chi_r, chi_s`` are *overlap*-
    normalised (``<o|o> = 1``); auxiliary primitives ``P, Q`` are
    *Coulomb*-normalised (``(P|P) = 1``).  Returns ``(V, J)`` with
    ``V[P, Q] = (P|Q)`` (unit-diagonal) and
    ``J[k, P] = (chi_r chi_s | P)_{L, M}`` for the ``k``th m-resolved
    orbital-product row whose Gaunt coupling to ``(L, M)`` is non-zero.

    ``items`` is a list of ``(n, zeta)`` aux primitives (``n`` may take
    any value ``>= L + 1``; the candidate-pool builder preserves the
    natural radial power of each orbital product).  ``primitives`` is
    the orbital primitive list as ``(l, n, zeta)`` triples.
    """
    n_aux = len(items)
    if n_aux == 0:
        return np.zeros((0, 0)), np.zeros((0, 0), dtype=float)
    a_aux_n = np.asarray([na for (na, _z) in items], dtype=int)
    a_aux_z = np.asarray([float(z) for (_n, z) in items], dtype=float)
    # Overlap-normalisation constants on the aux side; we will rescale to
    # the Coulomb-normalised convention at the end so the returned
    # V satisfies (P|P) = 1 and J is consistent with it.
    N_aux_overlap = np.array([sto_norm(na, za) for (na, za) in items],
                             dtype=float)

    rows = []
    fourpi_2Lp1 = 4.0 * pi / (2 * L + 1)

    for (la, n_a, za) in primitives:
        Na = sto_norm(n_a, za)
        for (lb, n_b, zb) in primitives:
            if L not in coupling_lvals(la, lb):
                continue
            Nb = sto_norm(n_b, zb)
            base = Na * Nb * fourpi_2Lp1

            rad_vec = np.fromiter(
                (sto_radial_coulomb(n_a + n_b, int(nP) + 1, L,
                                    float(za + zb), float(zP))
                 for (nP, zP) in zip(a_aux_n, a_aux_z)),
                dtype=float, count=n_aux,
            )
            # J_overlap = (orbital overlap-norm) * (aux overlap-norm) * radial.
            kern_P = base * N_aux_overlap * rad_vec

            G = gaunt_table(la, lb, L)
            for g, _ima, _imb, _iM in _iter_nonzero_gaunt(G, la, lb, L):
                rows.append(g * kern_P)

    V_overlap = sto_aux_metric_overlap_norm(L, items)
    s = _coulomb_rescale_factors(V_overlap)         # 1 / sqrt((P|P)_overlap)
    V_coul = V_overlap * np.outer(s, s)             # unit-diagonal Coulomb metric
    if rows:
        # Each row already carries the orbital and aux overlap-norms; rescaling
        # the aux column by ``s`` puts the aux index into the Coulomb-normalised
        # convention so V_coul and J_coul are consistent.
        J_coul = np.vstack(rows) * s[None, :]
    else:
        J_coul = np.zeros((0, n_aux), dtype=float)
    return V_coul, J_coul


def _sto_orbital_diag_exact(L, primitives):
    """Per-row exact ``(chi_r chi_s | chi_r chi_s)_{L, M}`` matching the
    row order produced by :func:`sto_orbital_aux_projection`.  Each row
    corresponds to one ``(la, m_a, lb, m_b, M)`` channel.
    """
    out = []
    fourpi_2Lp1 = 4.0 * pi / (2 * L + 1)
    for (la, n_a, za) in primitives:
        Na = sto_norm(n_a, za)
        for (lb, n_b, zb) in primitives:
            if L not in coupling_lvals(la, lb):
                continue
            Nb = sto_norm(n_b, zb)
            R_diag = sto_radial_coulomb(n_a + n_b, n_a + n_b, L,
                                        float(za + zb), float(za + zb))
            G = gaunt_table(la, lb, L)
            base = fourpi_2Lp1 * (Na * Nb) ** 2 * R_diag
            for g, _ima, _imb, _iM in _iter_nonzero_gaunt(G, la, lb, L):
                out.append(base * g * g)
    return np.asarray(out, dtype=float)


def sto_diagonal_ri_error(sto_orbital_basis, sto_aux_basis):
    """Total diagonal RI error over all m-resolved orbital primitive
    product channels::

        err = sum_{rs, L, M}  [ (rs | rs)_{L, M, exact}
                                - (rs | rs)_{L, M, RI} ]

    The L, M decomposition matches the row enumeration used by
    :func:`sto_orbital_aux_projection`.  ``(rs | rs)_{L, M, RI}`` uses
    only the aux primitives in ``sto_aux_basis`` for the given ``L``.
    Both ``sto_orbital_basis`` and ``sto_aux_basis`` are
    ``{L: [(n, zeta), ...]}`` dicts.

    The pivoted-Cholesky selection of the auxiliary primitives guarantees
    ``err >= 0`` (up to floating-point noise) and, when the aux pool
    exactly spans the orbital product subspace at ``L``, ``err = 0``
    contribution from that ``L`` block.
    """
    orbital_primitives = sto_decontract(sto_orbital_basis)
    if not orbital_primitives:
        return 0.0

    L_orbital = set()
    for (la, _na, _za) in orbital_primitives:
        for (lb, _nb, _zb) in orbital_primitives:
            L_orbital.update(_shellpair_L_range(la, lb))
    L_set = L_orbital | {int(L) for L in sto_aux_basis}

    err = 0.0
    for L in sorted(L_set):
        items = sto_aux_basis.get(L, [])
        exact = _sto_orbital_diag_exact(L, orbital_primitives)
        if exact.size == 0:
            continue
        if not items:
            # No aux at this L: contribution is the full exact diagonal.
            err += float(exact.sum())
            continue
        V, J = sto_orbital_aux_projection(L, orbital_primitives, items)
        if J.size == 0:
            err += float(exact.sum())
            continue
        c = np.linalg.solve(V, J.T)
        ri_diag = np.einsum('rj,jr->r', J, c)
        err += float((exact - ri_diag).sum())
    return err


def _sto_reduced_pair_screen(primitives, threshold):
    """STO analogue of :func:`auxgen._reduced_pair_screen`.  Delegates to
    :func:`~basis_set_exchange.auxgen.twoel.coupled_shell_pair_screen`
    with the STO norm/radial closures.
    """
    shell_pairs = orbital_shell_pairs(primitives)
    if not shell_pairs:
        return []
    keep = coupled_shell_pair_screen(shell_pairs, threshold,
                                     norm_fn=sto_norm,
                                     radial_fn=_sto_radial_fn)
    return [shell_pairs[i] for i in keep]


def _sto_candidate_pool_from_shell_pairs(selected_shell_pairs):
    pool = {}
    for (la, na, za, lb, nb, zb) in selected_shell_pairs:
        n_aux = na + nb - 1
        z_aux = float(za + zb)
        for L in _shellpair_L_range(la, lb):
            pool.setdefault(L, []).append((n_aux, z_aux))
    return _dedupe_pool(pool)


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------

def generate_sto_auxiliary_basis(sto_basis, threshold=1.0e-7,
                                 scheme='reduced', n_random=100, seed=0,
                                 prune_lmax=False, lmax_occ=None, linc=1,
                                 compact=False):
    """Generate an STO auxiliary basis from an STO orbital basis using
    the pivoted-Cholesky procedure of Lehtola, J. Chem. Theory Comput. 17,
    6886 (2021) [https://doi.org/10.1021/acs.jctc.1c00607], with the
    optional ``l_max`` cap of Lehtola JCTC 19, 6242 (2023) eq 9.

    Parameters
    ----------
    sto_basis : dict
        ``{L: [(n, zeta), ...]}`` mapping angular momentum to STO
        primitives (``n`` is the principal quantum number, ``zeta`` the
        exponent).  Each primitive is the un-contracted radial form
        ``r^(n - 1) e^(-zeta r) Y_{L M}``.  An iterable of
        ``(L, n, zeta)`` triples is also accepted.
    threshold : float
        Pivoted-Cholesky drop tolerance ``tau`` (absolute, applied to
        the residual diagonal).  Used for both the 4-index pre-screening
        (reduced scheme) and the per-L candidate Cholesky.
    scheme : {'basic', 'reduced'}
        ``'basic'`` enumerates every orbital primitive pair; ``'reduced'``
        first thins them with a shell-pair-driven pivoted Cholesky of
        the 4-index ``(mu nu | rho sigma)`` STO tensor.
    n_random : int
        Number of random candidate orderings tried in the per-L Cholesky
        (the linear and off-diagonal-norm orderings are always tried in
        addition; the most compact pivot set is kept).
    seed : int
        Seed for the random orderings.
    prune_lmax : bool
        Drop auxiliary shells with ``L > l_keep``, where
        ``l_keep = max(2 l_occ, l_occ + l_OBS + l_inc)`` (Lehtola 2023
        eq 9).  Requires ``lmax_occ`` when enabled.
    lmax_occ : int, optional
        Maximum angular momentum of occupied shells (``l_occ``).  When
        the element ``Z`` is known, the row-based default from
        :func:`auxgen._default_lmax_occ` is appropriate.
    linc : int
        Increment ``l_inc`` in the pruning rule (default 1).
    compact : bool
        When ``True``, collapse every candidate onto the minimum-radial-
        power form ``n_aux = L + 1`` via the ``<r>``-matching map
        :func:`sto_zeta_eff` before the Cholesky selection.  The
        resulting aux basis is "single-n per L" -- it sacrifices the
        natural radial richness of orbital products for simplicity.
        Default ``False`` (preserve the natural ``n``).

    Returns
    -------
    dict
        ``{L: [(n, zeta), ...]}`` of selected STO aux primitives.  In
        the default mode ``n`` varies; with ``compact=True`` every
        primitive has ``n = L + 1``.
    """
    # Local import to avoid circular dependency at module load.
    from .auxgen import _most_compact_pivot

    primitives = sto_decontract(sto_basis)
    if not primitives:
        return {}

    if scheme == 'reduced':
        sel = _sto_reduced_pair_screen(primitives, threshold)
        pool = _sto_candidate_pool_from_shell_pairs(sel)
    elif scheme == 'basic':
        pool = sto_candidate_pool_from_primitives(primitives)
    else:
        raise ValueError("scheme must be 'basic' or 'reduced'")

    if prune_lmax:
        if lmax_occ is None:
            raise ValueError("prune_lmax=True requires lmax_occ "
                             "(see auxgen._default_lmax_occ for the default)")
        lmax_obs = max((l for (l, _n, _z) in primitives), default=0)
        l_keep = max(2 * lmax_occ, lmax_occ + lmax_obs + linc)
        pool = {L: items for L, items in pool.items() if L <= l_keep}

    if compact:
        pool = _compact_pool(pool)

    out = {}
    for L, items in pool.items():
        if not items:
            continue
        # Build the normalised metric over the (n, zeta) candidates --
        # arbitrary n is honoured here, so the pivoted Cholesky operates
        # on the full candidate space rather than a single radial-power
        # slice.
        S = sto_aux_metric(L, items)
        sel_idx = _most_compact_pivot(S, tol=threshold, n_random=n_random,
                                      seed=seed + 1000 * L)
        if sel_idx:
            kept = [items[i] for i in sel_idx]
            out[L] = sorted(kept, key=lambda nz: (nz[0], -nz[1]))
    return out


# ---------------------------------------------------------------------------
# ADF basis file I/O
# ---------------------------------------------------------------------------
#
# ADF per-element basis files (e.g. those shipped with the program in
# atomicdata/ZORA/...) have the layout::
#
#     <element title>          # e.g. "Hydrogen (II)" or "Iron (V)"
#     <blank>
#     BASIS
#     1S   0.76
#     1S   1.28
#     ...
#     END
#     CORE    n_s n_p n_d n_f
#     END
#     DESCRIPTION
#     ...
#     END
#     FIT
#      1S   3.16
#      ...
#     END
#     FITCOEFFICIENTS
#     ...
#     /
#     END
#
# Each shell line is ``<n><L_letter> <zeta>`` -- principal quantum
# number, angular-momentum letter (S/P/D/F/G/...), exponent.

def _parse_adf_shell_line(line):
    """Parse one ADF shell line like ``" 1S   0.76"`` into ``(L, n, zeta)``;
    returns ``None`` if the line is blank or otherwise unparsable.
    """
    s = line.strip()
    if not s:
        return None
    # First whitespace-separated token is "<n><L>", second is the exponent.
    parts = s.split()
    if len(parts) < 2:
        return None
    head, zeta_str = parts[0], parts[1]
    # head must start with one or more digits followed by a letter.
    i = 0
    while i < len(head) and head[i].isdigit():
        i += 1
    if i == 0 or i >= len(head):
        return None
    try:
        n = int(head[:i])
        L = lut.amchar_to_int(head[i:i + 1])[0]
        zeta = float(zeta_str)
    except (ValueError, IndexError):
        return None
    return L, n, zeta


_ADF_SECTION_NAMES = {'BASIS', 'CORE', 'DESCRIPTION', 'FIT', 'FITCOEFFICIENTS'}


def _read_adf_sections(text):
    """Split an ADF basis-file text into ``(title, sections)`` where
    ``sections`` maps section name (uppercased) to a list of body
    lines.  A section starts at a line whose first whitespace-separated
    token is one of ``_ADF_SECTION_NAMES`` (the remainder of that line,
    if any, is captured as the first body line -- ADF's ``CORE`` block
    puts its data inline with the keyword).  A section ends at a line
    whose first token is ``END``.
    """
    lines = text.splitlines()
    title_lines = []
    sections = {}
    cur_name = None
    cur_body = []
    for raw in lines:
        stripped = raw.strip()
        first = stripped.split(None, 1)[0].upper() if stripped else ''
        if cur_name is None:
            if first in _ADF_SECTION_NAMES:
                cur_name = first
                cur_body = []
                rest = stripped[len(first):].strip()
                if rest:
                    cur_body.append(rest)
            else:
                title_lines.append(raw)
        else:
            if first == 'END':
                sections[cur_name] = cur_body
                cur_name = None
                cur_body = []
            else:
                cur_body.append(raw)
    title = '\n'.join(title_lines).strip()
    return title, sections


def read_adf_basis(path):
    """Read an ADF per-element basis file and return a dict
    ``{'title': str, 'orbital': {L: [(n, zeta), ...]},
       'fit': {L: [(n, zeta), ...]}, 'sections': dict}``.

    ``'sections'`` is the raw section map (preserves CORE, DESCRIPTION,
    FITCOEFFICIENTS, ...) so that :func:`write_adf_basis` can round-trip
    everything except the replaced FIT block.
    """
    with open(path, 'r') as f:
        text = f.read()
    title, sections = _read_adf_sections(text)
    orbital = {}
    for line in sections.get('BASIS', []):
        parsed = _parse_adf_shell_line(line)
        if parsed is None:
            continue
        L, n, zeta = parsed
        orbital.setdefault(L, []).append((n, zeta))
    fit = {}
    for line in sections.get('FIT', []):
        parsed = _parse_adf_shell_line(line)
        if parsed is None:
            continue
        L, n, zeta = parsed
        fit.setdefault(L, []).append((n, zeta))
    return {'title': title, 'orbital': orbital, 'fit': fit,
            'sections': sections}


def _format_fit_block(fit):
    """Render a ``{L: [(n, zeta), ...]}`` dict in ADF FIT-block form.
    ``zeta`` is written with eight significant digits so a regenerated
    FIT does not silently round-trip away precision relative to what
    the Cholesky selector produced.
    """
    out = []
    for L in sorted(fit.keys()):
        L_char = lut.amint_to_char([int(L)]).upper()
        for (n, zeta) in fit[L]:
            out.append(f" {int(n)}{L_char} {float(zeta):16.8f}")
    return out


def write_adf_basis(path, parsed, new_fit):
    """Write an ADF basis file with the FIT section replaced by
    ``new_fit`` (``{L: [(n, zeta), ...]}``) while preserving the title,
    BASIS, CORE, and DESCRIPTION sections from the ``parsed`` dict
    returned by :func:`read_adf_basis`.

    The FITCOEFFICIENTS block from the source file is *dropped* -- it
    refers to the old FIT exponents and would be silently wrong against
    the regenerated FIT.  Downstream ADF runs will recompute it.
    """
    parts = []
    title = parsed.get('title', '').rstrip()
    if title:
        parts.append(title)
    parts.append('')

    def emit(name, body_lines):
        parts.append(name)
        for line in body_lines:
            parts.append(line.rstrip())
        parts.append('END')
        parts.append('')

    sections = parsed.get('sections', {})
    emit('BASIS', sections.get('BASIS', []))
    emit('CORE', sections.get('CORE', ['    0  0  0  0']))
    emit('DESCRIPTION', sections.get('DESCRIPTION', []))
    emit('FIT', _format_fit_block(new_fit))

    with open(path, 'w') as f:
        f.write('\n'.join(parts) + '\n')


def _element_z_from_title(title):
    """Best-effort element Z extraction from an ADF title line like
    ``"Hydrogen (II)"`` or ``"Iron (V)"``.  Returns ``None`` on failure;
    callers use this to default ``lmax_occ`` via
    :func:`auxgen._default_lmax_occ`.
    """
    if not title:
        return None
    name = title.split('(')[0].strip()
    if not name:
        return None
    try:
        return lut.element_Z_from_name(name)
    except KeyError:
        return None


# ---------------------------------------------------------------------------
# main() driver: read ADF basis, regenerate FIT, benchmark RI error
# ---------------------------------------------------------------------------

def _format_basis_summary(basis):
    """``{L: [...]} -> "5S 3P 2D"``-style compact summary."""
    parts = []
    for L in sorted(basis.keys()):
        ch = lut.amint_to_char([int(L)]).upper()
        parts.append("%d%s" % (len(basis[L]), ch))
    return ' '.join(parts) or '<empty>'


def main(argv=None):
    """Command-line driver: read an ADF per-element basis file, regenerate
    its FIT (auxiliary) basis with the pivoted-Cholesky procedure, save
    the new file, and report the diagonal RI error of the old and new
    fit bases for comparison.

    Usage::

        python -m basis_set_exchange.auxgen.sto input.adf [output.adf]
            [--threshold TAU] [--scheme {basic,reduced}]
            [--prune-lmax] [--linc INT] [--lmax-occ INT]
            [--no-benchmark-old]
    """
    import argparse

    p = argparse.ArgumentParser(
        prog='python -m basis_set_exchange.auxgen.sto',
        description=(
            "Regenerate the FIT (auxiliary) basis in an ADF per-element "
            "STO basis file using the pivoted-Cholesky procedure of "
            "Lehtola JCTC 17, 6886 (2021).  Reports the diagonal RI "
            "error of the old and new fits for comparison."),
    )
    p.add_argument('input', help='ADF input basis file (contains BASIS + FIT)')
    p.add_argument('output', nargs='?', default=None,
                   help='Output ADF file (default: <input>.new)')
    p.add_argument('--threshold', type=float, default=1.0e-7,
                   help='Pivoted-Cholesky drop tolerance (default 1e-7)')
    p.add_argument('--scheme', choices=['basic', 'reduced'],
                   default='reduced',
                   help='Selection scheme (default reduced)')
    p.add_argument('--n-random', type=int, default=0,
                   help='Random orderings in per-L Cholesky (default 0)')
    p.add_argument('--seed', type=int, default=0,
                   help='Seed for random orderings (default 0)')
    p.add_argument('--prune-lmax', action='store_true',
                   help='Drop aux shells above l_keep '
                        '(Lehtola JCTC 19, 6242 (2023) eq 9)')
    p.add_argument('--linc', type=int, default=1,
                   help='l_inc in the prune-lmax rule (default 1)')
    p.add_argument('--lmax-occ', type=int, default=None,
                   help='l_occ override; default uses the per-element '
                        'row-based table when Z can be inferred from '
                        'the file title.')
    p.add_argument('--compact', action='store_true',
                   help='Collapse every candidate onto the minimum-radial-'
                        'power form (n = L + 1) via the <r>-matching map '
                        'before selection.  Yields a single-n-per-L aux '
                        'basis at the cost of natural radial richness.')
    p.add_argument('--no-benchmark', action='store_true',
                   help='Skip the diagonal-RI-error benchmark for both '
                        'the old and the new FIT blocks')
    args = p.parse_args(argv)

    from .auxgen import _default_lmax_occ

    parsed = read_adf_basis(args.input)
    orbital = parsed['orbital']
    old_fit = parsed['fit']
    if not orbital:
        print("error: no BASIS shells found in %s" % args.input,
              file=sys.stderr)
        return 1

    lmax_occ = args.lmax_occ
    if args.prune_lmax and lmax_occ is None:
        z = _element_z_from_title(parsed['title'])
        if z is None:
            print("error: --prune-lmax needs --lmax-occ "
                  "(could not infer element Z from title %r)"
                  % parsed['title'], file=sys.stderr)
            return 1
        lmax_occ = _default_lmax_occ(z)

    new_fit = generate_sto_auxiliary_basis(
        orbital,
        threshold=args.threshold,
        scheme=args.scheme,
        n_random=args.n_random,
        seed=args.seed,
        prune_lmax=args.prune_lmax,
        lmax_occ=lmax_occ,
        linc=args.linc,
        compact=args.compact,
    )

    out_path = args.output or (args.input + '.new')
    write_adf_basis(out_path, parsed, new_fit)

    print("title:    %s" % parsed['title'])
    print("orbital:  %s" % _format_basis_summary(orbital))
    print("old FIT:  %s" % _format_basis_summary(old_fit))
    print("new FIT:  %s  (wrote %s)" % (_format_basis_summary(new_fit), out_path))
    if not args.no_benchmark:
        if old_fit:
            old_err = sto_diagonal_ri_error(orbital, old_fit)
            print("diagonal RI error (old): %.6e" % old_err)
        new_err = sto_diagonal_ri_error(orbital, new_fit)
        print("diagonal RI error (new): %.6e" % new_err)
    return 0


if __name__ == '__main__':
    sys.exit(main())
