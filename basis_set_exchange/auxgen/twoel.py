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
One-center two-electron integrals used by the auxgen pipeline.

Primitive Gaussians are described by ``(l, n, m, alpha)`` with the
unnormalized form

    chi_{l m n alpha}(r) = r^n Y_{l m}(\\Omega) e^{-alpha r^2},

so ``l`` is the angular momentum (controlling the Y_{l m} factor), and
``n`` is the radial power.  For spherical / regular GTOs ``n = l``;
cartesian shells of nominal angular momentum L contribute lower-l
components with ``n = L > l`` (the well-known cartesian
"contamination").

Three integral families are provided:

  * :func:`primitive_eri` -- the four-index (ab|cd) over normalized
    primitives.  Reference implementation used by the test suite
    (validated against PySCF's libcint to machine precision).

  * :func:`primitive_aux_metric` -- two-index (P|Q) between normalized
    standard primitives at a single L (the candidate metric used by
    the per-L Cholesky), and :func:`normalized_metric` which rescales
    it to unit diagonal.

  * :func:`coupled_L_metric` -- per-L Coulomb metric on radial
    shell-pair candidates in the coupled ``(L, M)`` basis; used by the
    production reduced-scheme pre-screen.

  * :func:`product_metric` -- shell-pair-vectorised four-index metric
    over m-resolved product pairs.  Kept as the dense reference against
    which :func:`coupled_L_metric` is validated in the test suite; not
    used in the production pipeline (dense ``O(N_m_pair^2)`` memory).

  * :func:`orbital_aux_projection` -- the three-index projection
    ``J[(rs, M), P] = (rs | P)_{L, M}`` over m-resolved orbital product
    densities and aux primitives at the same ``L``.  Used by the test
    suite to compute the diagonal RI error of a generated aux basis.
"""

import numpy as np
from math import pi

from .gaunt import real_gaunt, coupling_lvals, gaunt_table
from .radial import radial_integral, gto_norm, gto_norm_array


def _iter_nonzero_gaunt(G, la, lb, L):
    """Yield ``(g, ima, imb, iM)`` for every non-zero entry of the
    real-Gaunt slab ``G = gaunt_table(la, lb, L)`` (shape
    ``(2 la + 1, 2 lb + 1, 2 L + 1)``).  Hot-path enumerator shared by
    the GTO and STO projections so they walk the same m-resolved row
    order."""
    for ima in range(2 * la + 1):
        for imb in range(2 * lb + 1):
            for iM in range(2 * L + 1):
                g = G[ima, imb, iM]
                if g != 0.0:
                    yield g, ima, imb, iM


# ---------------------------------------------------------------------------
# Reference 4-index ERI (used by tests; not in the hot path).
# ---------------------------------------------------------------------------

def primitive_eri(la, na, ma, alpha_a,
                  lb, nb, mb, alpha_b,
                  lc, nc, mc, alpha_c,
                  ld, nd, md, alpha_d):
    """(ab|cd) over overlap-normalized primitives of the form
    chi(r) = N r^n Y_{l m} e^{-alpha r^2}.

    Reference implementation: explicit sum over the multipole index L
    and projection M, no shell-level vectorisation.  Used by the test
    suite (cross-checked against PySCF/libcint to machine precision).
    """
    L_left = coupling_lvals(la, lb)
    L_right = coupling_lvals(lc, ld)
    Lset = tuple(L for L in L_left if L in L_right)
    if not Lset:
        return 0.0

    n_ab = na + nb
    n_cd = nc + nd
    alpha_ab = alpha_a + alpha_b
    alpha_cd = alpha_c + alpha_d

    total = 0.0
    for L in Lset:
        ang = 0.0
        for M in range(-L, L + 1):
            gl = real_gaunt(la, ma, lb, mb, L, M)
            if gl == 0.0:
                continue
            gr = real_gaunt(lc, mc, ld, md, L, M)
            if gr == 0.0:
                continue
            ang += gl * gr
        if ang == 0.0:
            continue
        rad = radial_integral(L, n_ab, n_cd, alpha_ab, alpha_cd)
        total += (4.0 * pi / (2 * L + 1)) * ang * rad

    Na = gto_norm(na, alpha_a)
    Nb = gto_norm(nb, alpha_b)
    Nc = gto_norm(nc, alpha_c)
    Nd = gto_norm(nd, alpha_d)
    return Na * Nb * Nc * Nd * total


# ---------------------------------------------------------------------------
# Single-L Coulomb metric between normalized standard primitives.
# ---------------------------------------------------------------------------

def primitive_aux_metric(L, alphas):
    """``(P|Q)`` between normalized standard primitives
    ``r^L Y_{L M} e^{-alpha r^2}`` sharing the same ``L`` (and ``M``).

    Symmetric, positive definite, M-independent.  Returns the metric in
    its natural (un-normalized) form; see :func:`normalized_metric` for
    the unit-diagonal variant used by the candidate Cholesky.
    """
    a = np.asarray(alphas, dtype=float)
    n = a.size
    if n == 0:
        return np.zeros((0, 0), dtype=float)
    A, B = np.meshgrid(a, a, indexing='ij')
    rad = radial_integral(L, L, L, A, B)
    Np = gto_norm_array(L, a)
    return (4.0 * pi / (2 * L + 1)) * Np[:, None] * Np[None, :] * rad


def normalized_metric(L, alphas):
    """Coulomb metric on standard primitives at angular momentum ``L``,
    rescaled to unit diagonal -- i.e. each primitive is implicitly
    re-normalized so that ``(A|A) = 1``, matching the convention of
    Lehtola, J. Chem. Theory Comput. 17, 6886 (2021)
    [https://doi.org/10.1021/acs.jctc.1c00607], eq 7.
    """
    M = primitive_aux_metric(L, alphas)
    if M.size == 0:
        return M
    d = np.sqrt(np.diag(M))
    return M / np.outer(d, d)


# ---------------------------------------------------------------------------
# Three-index orbital-product / aux projection (test-suite use).
# ---------------------------------------------------------------------------

def _aux_radial_vector(L, n_ab, alpha_ab, aux_alphas):
    """One-center Coulomb radial integrals ``R_L(n_ab, L; alpha_ab,
    alpha_P)`` for every ``alpha_P`` in ``aux_alphas`` (the orbital-pair
    radial power ``n_ab`` and combined exponent ``alpha_ab`` fixed).
    Shared helper used by :func:`_W_block` and :func:`orbital_aux_projection`.
    """
    return np.fromiter(
        (radial_integral(L, n_ab, L, alpha_ab, float(p)) for p in aux_alphas),
        dtype=float, count=len(aux_alphas),
    )


def orbital_aux_projection(L, primitives, alphas):
    """Three-index projection of orbital product densities onto a set
    of aux primitives at angular momentum ``L``.

    Builds

        J[k, P] = (r_a s_b | P)_{L, M}
                = G(l_a m_a, l_b m_b, L, M) * (4 pi / (2 L + 1))
                  * N_a N_b N_P
                  * R_L(n_a + n_b, alpha_a + alpha_b; L, alpha_P)

    where the row index ``k`` enumerates all
    ``(l_a, m_a, n_a, alpha_a, l_b, m_b, n_b, alpha_b, M)`` combinations
    with ``L`` in the angular coupling range of ``(l_a, l_b)``, and
    columns enumerate the aux exponents in ``alphas``.  The companion
    ``V[P, Q] = (P|Q)`` metric on the same aux primitives is also
    returned (it is :func:`primitive_aux_metric`).

    Used by the test suite to compute the diagonal RI error of a
    generated aux basis -- i.e. ``sum_{rs} [(rs|rs)_exact -
    (rs|rs)_RI]``.

    Parameters
    ----------
    L : int
        Angular momentum of the aux block.
    primitives : list of ``(l, n, alpha)``
        Orbital primitives (cartesian contamination handled by ``n``).
    alphas : array_like of float
        Aux primitive exponents (all at angular momentum ``L``).

    Returns
    -------
    V : numpy.ndarray, shape (n_aux, n_aux)
        Two-index aux metric ``(P|Q)``.
    J : numpy.ndarray, shape (n_rows, n_aux)
        Three-index projection ``(rs|P)`` over m-resolved orbital
        products that couple to ``L``.  Rows with all-zero Gaunt
        coefficients are dropped at construction time.
    """
    n_aux = len(alphas)
    V = primitive_aux_metric(L, alphas)
    if n_aux == 0:
        return V, np.zeros((0, 0), dtype=float)
    a_aux = np.asarray(alphas, dtype=float)
    N_aux = gto_norm_array(L, a_aux)

    rows = []
    fourpi_2Lp1 = 4.0 * pi / (2 * L + 1)

    for la, n_a, aa in primitives:
        Na = gto_norm(n_a, aa)
        for lb, n_b, ab in primitives:
            if L not in coupling_lvals(la, lb):
                continue
            Nb = gto_norm(n_b, ab)
            base = Na * Nb * fourpi_2Lp1

            # Radial vector over aux: depends on (n_a+n_b, alpha_a+alpha_b, alpha_P).
            kern_P = base * N_aux * _aux_radial_vector(L, n_a + n_b, aa + ab, a_aux)

            # Gaunt slab for this shell-pair at this L: (2la+1, 2lb+1, 2L+1).
            G = gaunt_table(la, lb, L)
            for g, _ima, _imb, _iM in _iter_nonzero_gaunt(G, la, lb, L):
                rows.append(g * kern_P)

    if rows:
        J = np.vstack(rows)
    else:
        J = np.zeros((0, n_aux), dtype=float)
    return V, J


# ---------------------------------------------------------------------------
# Coupled-basis Coulomb metric on radial shell-pair candidates (reduced-scheme).
# ---------------------------------------------------------------------------


def coupled_L_metric(L, shell_pairs, norm_fn=None, radial_fn=None):
    """One-per-shell-pair Coulomb metric at coupled channel ``L``.

    The four-index Coulomb metric ``(mu nu | rho sigma)`` on orbital
    product densities decomposes, via the multipole expansion of ``1/r_12``,
    into blocks that are diagonal in the coupled channel ``(L, M)`` and
    M-independent (Wigner-Eckart).  Rather than materialise the dense
    m-resolved matrix (``O(N_m_pair^2)`` memory) and then run a
    shell-pair-driven block Cholesky over it, the reduced-scheme screen
    can work directly in the coupled basis: one radial "coupled candidate"
    per orbital shell-pair ``(l_a, n_a, alpha_a, l_b, n_b, alpha_b)`` at
    each ``L`` in the shell-pair's coupling range, with metric

        M_L[i, j] = (4 pi / (2 L + 1))
                    * N(n_a_i, alpha_a_i) N(n_b_i, alpha_b_i)
                    * N(n_a_j, alpha_a_j) N(n_b_j, alpha_b_j)
                    * R_L(n_ab_i, n_ab_j, alpha_ab_i, alpha_ab_j).

    Angular multiplicity (Gaunt-squared, summed over M) is folded away --
    the residual is pure radial linear-independence at ``L``, which is
    what the pivoted-Cholesky screen actually needs.  Compared to the
    dense m-resolved formulation, this drops peak memory from
    ``O(N_m_pair^2) = O(sum_shell (2 l_a + 1)(2 l_b + 1))^2`` down to
    ``O(N_shell_pair^2)`` per L block, typically two orders of magnitude
    smaller for high-l orbital bases.

    The caller is responsible for filtering ``shell_pairs`` to those with
    ``L in coupling_lvals(l_a, l_b)``.

    ``norm_fn(n, exponent) -> N`` and
    ``radial_fn(L, n_ab, n_cd, exp_ab, exp_cd) -> R_L`` parameterise the
    radial primitive family (defaults reproduce GTOs; the STO driver
    passes its own closures).
    """
    if norm_fn is None:
        norm_fn = gto_norm
    if radial_fn is None:
        radial_fn = radial_integral
    n = len(shell_pairs)
    M = np.zeros((n, n), dtype=float)
    if n == 0:
        return M
    pref = 4.0 * pi / (2 * L + 1)
    norms = np.fromiter(
        (norm_fn(na, aa) * norm_fn(nb, ab_)
         for (_la, na, aa, _lb, nb, ab_) in shell_pairs),
        dtype=float, count=n,
    )
    n_abs = np.fromiter(
        (na + nb for (_la, na, _aa, _lb, nb, _ab) in shell_pairs),
        dtype=int, count=n,
    )
    a_abs = np.fromiter(
        (aa + ab_ for (_la, _na, aa, _lb, _nb, ab_) in shell_pairs),
        dtype=float, count=n,
    )
    # ``radial_fn(L, n_ab, n_cd, ...)`` takes the two radial-power
    # arguments as scalars (they steer selection rules and the closed-form
    # kn / km evaluation), but broadcasts naturally over its exponent
    # arguments.  Group shell-pairs by radial power and vectorise the
    # ``(alpha_ab, alpha_cd)`` grid inside each ``(n_ab, n_cd)`` block --
    # unique radial powers are ``O(l_max^2)`` at most, so a small number
    # of grouped calls replaces the ``O(n^2)`` scalar loop.
    unique_n = sorted(set(int(x) for x in n_abs))
    pos_by_n = {u: np.flatnonzero(n_abs == u) for u in unique_n}
    for u in unique_n:
        idx_u = pos_by_n[u]
        if idx_u.size == 0:
            continue
        a_u = a_abs[idx_u]
        norm_u = norms[idx_u]
        for v in unique_n:
            idx_v = pos_by_n[v]
            if idx_v.size == 0:
                continue
            a_v = a_abs[idx_v]
            norm_v = norms[idx_v]
            R = radial_fn(L, u, v, a_u[:, None], a_v[None, :])
            block = pref * (norm_u[:, None] * norm_v[None, :]) * R
            M[np.ix_(idx_u, idx_v)] = block
    return M


# ---------------------------------------------------------------------------
# Shell-pair-vectorised four-index Coulomb metric (dense; reference).
# ---------------------------------------------------------------------------


def product_metric(pairs, norm_fn=None, radial_fn=None):
    """Build the four-index Coulomb metric ``M[mu, nu] = (mu nu | rho sigma)``
    over m-resolved orbital primitive product pairs.

    The pairs are grouped by their orbital shell-pair
    ``(l_a, n_a, alpha_a, l_b, n_b, alpha_b)``.  For each shell-pair x
    shell-pair we form the full ``(2 l_a + 1)(2 l_b + 1)`` x
    ``(2 l_c + 1)(2 l_d + 1)`` block in one numpy ``einsum`` call,

        block[ma, mb, mc, md]
            = sum_L  (4 pi / (2 L + 1)) * R_L * sum_M G_left[ma, mb, L M]
                                                     G_right[mc, md, L M],

    times the orbital normalisations, and place it into the global
    metric.  Compared to the naive m-resolved loop, this moves the
    work from O(N_m_pair^2) Python iterations down to O(N_shell_pair^2)
    vectorised contractions.

    ``norm_fn(n, exponent) -> N`` and
    ``radial_fn(L, n_ab, n_cd, exp_ab, exp_cd) -> R_L`` parameterise the
    radial primitive family: the defaults
    (:func:`~basis_set_exchange.auxgen.radial.gto_norm` and
    :func:`~basis_set_exchange.auxgen.radial.radial_integral`) reproduce
    the GTO metric; the STO driver passes its own closures so the entire
    shell-pair-vectorised body is shared.
    """
    if norm_fn is None:
        norm_fn = gto_norm
    if radial_fn is None:
        radial_fn = radial_integral
    n = len(pairs)
    M = np.zeros((n, n), dtype=float)
    if n == 0:
        return M

    # Group m-resolved pair indices by orbital shell-pair.
    sp_of = {}
    for idx, ((la, na, ma, aa), (lb, nb, mb, ab_)) in enumerate(pairs):
        sp_of.setdefault((la, na, aa, lb, nb, ab_), []).append((idx, ma, mb))

    # idx_grid[ma + la, mb + lb] -> global index in ``pairs``; -1 for missing.
    sp_keys = list(sp_of.keys())
    sp_idx_grid = {}
    for key in sp_keys:
        la, _na, _aa, lb, _nb, _ab = key
        grid = -np.ones((2*la + 1, 2*lb + 1), dtype=np.int64)
        for (idx, ma, mb) in sp_of[key]:
            grid[ma + la, mb + lb] = idx
        sp_idx_grid[key] = grid

    for ip, kp in enumerate(sp_keys):
        la, na, aa, lb, nb, ab_ = kp
        norm_p = norm_fn(na, aa) * norm_fn(nb, ab_)
        n_ab = na + nb
        a_ab = aa + ab_
        L_left = coupling_lvals(la, lb)
        idx_p = sp_idx_grid[kp]

        for iq in range(ip, len(sp_keys)):
            kq = sp_keys[iq]
            lc, nc, ac, ld, nd, ad = kq
            norm_q = norm_fn(nc, ac) * norm_fn(nd, ad)
            n_cd = nc + nd
            a_cd = ac + ad

            Lset = tuple(L for L in L_left if L in coupling_lvals(lc, ld))
            if not Lset:
                continue

            block = None
            for L in Lset:
                rad = radial_fn(L, n_ab, n_cd, a_ab, a_cd)
                if rad == 0.0:
                    continue
                kernel = (4.0 * pi / (2 * L + 1)) * rad
                contrib = kernel * np.einsum('abM,cdM->abcd',
                                             gaunt_table(la, lb, L),
                                             gaunt_table(lc, ld, L))
                block = contrib if block is None else block + contrib

            if block is None:
                continue
            block *= norm_p * norm_q

            # Scatter into the global metric.  All shells are fully
            # populated (every m-component present) by construction, so
            # the index grids contain no sentinels.
            idx_q = sp_idx_grid[kq]
            Na, Nb, Nc, Nd = block.shape
            row_idx = idx_p.reshape(-1)
            col_idx = idx_q.reshape(-1)
            block_flat = block.reshape(Na * Nb, Nc * Nd)
            M[np.ix_(row_idx, col_idx)] += block_flat
            if ip != iq:
                M[np.ix_(col_idx, row_idx)] += block_flat.T

    return M
