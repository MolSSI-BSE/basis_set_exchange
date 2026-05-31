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
Enumerate orbital function products and the resulting auxiliary
candidate pool, following Lehtola, J. Chem. Theory Comput. 17, 6886
(2021) [https://doi.org/10.1021/acs.jctc.1c00607].

A primitive orbital basis function is described by a triple
``(l_angular, n_radial, alpha)`` corresponding to the unnormalized form

    chi(r) = r^{n_radial} Y_{l_angular, m}(\\Omega) e^{-alpha r^2}.

For spherical GTOs (function_type ``gto`` or ``gto_spherical``),
``n_radial = l_angular``.  For cartesian GTOs (``gto_cartesian``), an
angular-momentum-L shell additionally contributes lower-l components at
``l_angular = L - 2, L - 4, ...`` (down to 0 or 1) that share the same
radial power ``n_radial = L`` -- the well-known cartesian
"contamination".

A candidate auxiliary function is

    A_tilde = R_{mu nu}(r) Y_{L M}(\\Omega) =
              r^{n_mu + n_nu} e^{-(alpha_mu + alpha_nu) r^2} Y_{L M},

where the angular-momentum sum L runs over the real-Gaunt-allowed range
``|l_mu - l_nu| <= L <= l_mu + l_nu`` with ``l_mu + l_nu + L`` even.  In
the candidate pool we therefore index by ``(L, n_rad = n_mu + n_nu,
alpha_rad = alpha_mu + alpha_nu)``.
"""

import math

import numpy as np

from .. import manip
from .radial import alpha_eff, gto_norm_array
from .twoel import primitive_eri


def _split_sp(element_basis):
    """Split combined ``sp``/``spd``/``spdf`` shells of one element into
    separate single-angular-momentum shells (a no-op for already-single
    shells).  Returns the modified element-basis dict.
    """
    return manip.uncontract_spdf({'elements': {'1': element_basis}},
                                 max_am=0, use_copy=True)['elements']['1']


def _iter_shells(element_basis):
    """Yield ``(L, l_angs, exps, coefficients)`` per sp-split shell of
    ``element_basis``:

    - ``L`` is the shell's radial power (= its original am).
    - ``l_angs`` lists the angular momenta the shell contributes (just
      ``[L]`` for spherical shells; ``[L, L-2, ...]`` for cartesian
      ``contamination``).
    - ``exps`` is the shell's primitive exponents as floats.
    - ``coefficients`` is the shell's untouched list of contraction
      columns.
    """
    for shell in _split_sp(element_basis).get('electron_shells', []):
        if not _shell_function_types_ok(shell):
            raise ValueError("auxgen: unsupported function_type %r" % shell.get('function_type'))
        cart = _is_cartesian(shell)
        L = int(shell['angular_momentum'][0])
        exps = [float(e) for e in shell['exponents']]
        l_angs = [int(l) for l in _angular_components(L, cart)]
        yield L, l_angs, exps, shell['coefficients']


_ALLOWED_FT = ('gto', 'gto_spherical', 'gto_cartesian')


def _shell_function_types_ok(shell):
    """Accept all GTO variants.  ``gto`` is interpreted as spherical
    (matching the rest of the BSE codebase).  ``gto_cartesian`` triggers
    the angular-momentum contamination expansion in
    :func:`decontract_primitives`.
    """
    return shell.get('function_type', 'gto') in _ALLOWED_FT


def _is_cartesian(shell):
    return shell.get('function_type', 'gto') == 'gto_cartesian'


def _angular_components(L, cartesian):
    """Angular momenta carried by a shell of nominal angular momentum L.

    For spherical shells this is just ``[L]``; for cartesian shells it is
    ``[L, L - 2, L - 4, ..., 0 or 1]``.  All components share the same
    radial power ``L``.
    """
    if not cartesian:
        return (L,)
    return tuple(range(L, -1, -2))


def decontract_primitives(element_basis):
    """Collect unique primitive ``(l_angular, n_radial, alpha)`` triples.

    Spherical and cartesian shells are both accepted; the cartesian
    contamination is expanded into explicit lower-l primitives sharing
    the original radial power.  Any ``ecp_potentials`` on the element
    are ignored -- ECPs do not enter a fitting auxiliary basis.

    Returns a list of triples sorted by ``(l, n, -alpha)``.
    """
    seen = {}
    for L, l_angs, exps, _coeffs in _iter_shells(element_basis):
        for l_ang in l_angs:
            for a in exps:
                seen[(l_ang, L, a)] = True
    return sorted(seen.keys(), key=lambda x: (x[0], x[1], -x[2]))


def _match_single_primitive_moment(L, exps, coeffs):
    """Exponent ``beta`` of the single primitive ``r^L e^{-beta r^2}``
    that has the same radial expectation value ``<r>`` as the contracted
    function ``chi = sum_k coeffs[k] * (overlap-normalized
    r^L e^{-exps[k] r^2})``.

    Closed form: ``<r>_chi = (1/2) Gamma(L+2) sum_{ij} c_i c_j N_i N_j /
    (alpha_i + alpha_j)^{L+2}`` (with ``N_k`` the primitive overlap
    norm) and ``<r>_g_beta = Gamma(L+2) / [Gamma(L+3/2) sqrt(2 beta)]``,
    giving ``beta = (1/2) [Gamma(L+2) / (Gamma(L+3/2) <r>_chi)]^2``.
    """
    a = np.asarray(exps, dtype=float)
    c = np.asarray(coeffs, dtype=float)
    N = gto_norm_array(L, a)
    Sab = a[:, None] + a[None, :]
    M = (c[:, None] * c[None, :]) * (N[:, None] * N[None, :]) / Sab**(L + 2)
    r_chi = 0.5 * math.gamma(L + 2) * float(M.sum())
    ratio = math.gamma(L + 2) / (math.gamma(L + 1.5) * r_chi)
    return 0.5 * ratio * ratio


def _match_single_primitive_selfrepulsion(L, exps, coeffs):
    """Exponent ``beta`` of the single primitive ``r^L e^{-beta r^2}``
    that has the same orbital Coulomb self-energy ``(chi chi | chi chi)``
    as the contracted function ``chi = sum_k coeffs[k] * (overlap-
    normalized r^L Y_{L 0} e^{-exps[k] r^2})``.

    The orbital self-energy is the four-index ERI ``(chi chi | chi chi)``
    of the electron density ``|chi|^2``, not the two-index ``(chi|chi)``
    that treats ``chi`` itself as a charge.

    Closed form: ``(chi chi | chi chi) = sum_{ijkl} c_i c_j c_k c_l (phi_i
    phi_j | phi_k phi_l)`` (computed via :func:`twoel.primitive_eri` at
    ``m = 0``), and ``(g_beta g_beta | g_beta g_beta) = K_L * sqrt(beta)``
    since the ERI carries units of ``1/length ~ sqrt(alpha)``.  ``K_L``
    is the ERI at ``beta = 1``.  Equating gives ``beta = [(chi chi | chi
    chi) / K_L]^2``.
    """
    a = list(np.asarray(exps, dtype=float))
    c = [float(x) for x in coeffs]
    n = len(a)
    chichi = 0.0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for m in range(n):
                    chichi += c[i] * c[j] * c[k] * c[m] * primitive_eri(
                        L, L, 0, a[i], L, L, 0, a[j],
                        L, L, 0, a[k], L, L, 0, a[m],
                    )
    K_L = primitive_eri(L, L, 0, 1.0, L, L, 0, 1.0,
                        L, L, 0, 1.0, L, L, 0, 1.0)
    ratio = chichi / K_L
    return ratio * ratio


_COLLAPSE_MATCHERS = {
    'moment': _match_single_primitive_moment,
    'selfrepulsion': _match_single_primitive_selfrepulsion,
}


def decontract_primitives_single(element_basis, mapping='moment'):
    """Like :func:`decontract_primitives`, but each *contracted* orbital
    function is replaced by a single primitive whose exponent matches it
    analytically:

    * ``mapping='moment'`` (default) matches the radial expectation
      value ``<r>`` of the contracted function (closed form, see
      :func:`_match_single_primitive_moment`).
    * ``mapping='selfrepulsion'`` matches the Coulomb self-energy
      ``(chi|chi)`` of the contracted function (closed form, see
      :func:`_match_single_primitive_selfrepulsion`).

    Free (single-primitive) functions are kept unchanged (both modes
    reduce to ``beta = alpha`` for a single-primitive "contraction").
    Combined ``sp``/``spd`` shells are split first; cartesian shells
    still expand into their lower-l contamination at the matched
    exponent.  Returns the same ``(l_angular, n_radial, alpha)`` triple
    list as :func:`decontract_primitives`.
    """
    try:
        matcher = _COLLAPSE_MATCHERS[mapping]
    except KeyError:
        raise ValueError("mapping must be one of %s" % sorted(_COLLAPSE_MATCHERS))
    seen = {}
    for L, l_angs, exps, coeffs in _iter_shells(element_basis):
        for col in coeffs:
            c = [float(x) for x in col]
            nz = [i for i, x in enumerate(c) if x != 0.0]
            if not nz:
                continue
            beta = exps[nz[0]] if len(nz) == 1 else matcher(L, exps, c)
            for l_ang in l_angs:
                seen[(l_ang, L, float(beta))] = True
    return sorted(seen.keys(), key=lambda x: (x[0], x[1], -x[2]))


def _shellpair_L_range(li, lj):
    """Allowed total angular momenta when coupling shells of angular
    momentum ``li`` and ``lj``: ``|li - lj|``, ``|li - lj| + 2``,
    ..., ``li + lj``.  The stride-of-two reflects the real-spherical
    Gaunt parity rule ``li + lj + L`` even -- parity-forbidden L give
    zero coupling to any orbital-product channel and therefore are
    pointless aux candidates.
    """
    return range(abs(li - lj), li + lj + 1, 2)


def _pairs_to_pool(pair_iter, mapping):
    """Common tail of :func:`candidate_pool_from_primitives` and
    :func:`candidate_pool_from_pairs`: for each ``(la, n_a, alpha_a,
    lb, n_b, alpha_b)`` orbital primitive-pair tuple yielded by
    ``pair_iter``, accumulate ``alpha_eff(L, n_rad, alpha_rad, mapping)``
    over every parity-allowed coupling angular momentum ``L``, then
    deduplicate at floating-point tolerance and return
    ``{L: [alpha_eff, ...]}`` sorted decreasing.
    """
    pool = {}
    for la, n_a, a_a, lb, n_b, a_b in pair_iter:
        n_rad = n_a + n_b
        a_rad = float(a_a + a_b)
        for L in _shellpair_L_range(la, lb):
            pool.setdefault(L, []).append(alpha_eff(L, n_rad, a_rad, mapping))
    out = {}
    for L, alphas in pool.items():
        seen = {}
        for a in alphas:
            seen[round(a, 10)] = a
        out[L] = sorted(seen.values(), reverse=True)
    return out


def candidate_pool_from_primitives(primitives, mapping='moment'):
    """Build the per-L candidate pool from orbital primitives, per the
    ERKALE implementation of Lehtola 2021.

    For every unordered pair ``{(l_mu, n_mu, alpha_mu),
    (l_nu, n_nu, alpha_nu)}`` of primitives (including the diagonal),
    and every L in ``range(|l_mu - l_nu|, l_mu + l_nu + 1)``, the
    candidate is converted directly to its effective standard-primitive
    form ``r^L e^{-alpha_eff r^2}`` via the Appendix II
    ``<r>``-matching formula

        alpha_eff = scale(L, n_rad) * (alpha_mu + alpha_nu),
        scale(L, n_rad) = [Gamma(L+2) Gamma(n_rad + 3/2)
                           / (Gamma(L + 3/2) Gamma(n_rad + 2))]^2,

    where the radial power of the product is ``n_rad = n_mu + n_nu``
    (= ``l_mu + l_nu`` for purely spherical inputs, but larger when a
    cartesian shell contributes its lower-l contamination).

    Duplicates are removed *within numerical tolerance* (rounded to 10
    decimal places of relative magnitude).

    Returns ``{L: [alpha_eff, ...]}`` sorted decreasing.
    """
    def pairs():
        n = len(primitives)
        for i in range(n):
            li, ni, ai = primitives[i]
            for j in range(i, n):
                lj, nj, aj = primitives[j]
                yield li, ni, ai, lj, nj, aj
    return _pairs_to_pool(pairs(), mapping)


def candidate_pool_from_pairs(selected_pairs, mapping='moment'):
    """Build the per-L candidate pool from m-resolved primitive pairs
    selected by the reduced-scheme 4-index pre-screening.  The same
    Appendix II transformation is applied as in
    :func:`candidate_pool_from_primitives`.

    Each entry in ``selected_pairs`` is
    ``((l_a, n_a, m_a, alpha_a), (l_b, n_b, m_b, alpha_b))``.
    """
    def pairs():
        for (la, na, _ma, aa), (lb, nb, _mb, ab) in selected_pairs:
            yield la, na, aa, lb, nb, ab
    return _pairs_to_pool(pairs(), mapping)


def primitive_product_pairs(primitives):
    """Build all unordered (i <= j) primitive product pairs with m
    components expanded.  Each entry is

        ((l_a, n_a, m_a, alpha_a), (l_b, n_b, m_b, alpha_b)),

    consumed by :func:`twoel.product_metric` for the reduced-scheme
    4-index Cholesky.
    """
    expanded = []
    for l, n, a in primitives:
        for m in range(-l, l + 1):
            expanded.append((l, n, m, a))

    pairs = []
    npts = len(expanded)
    for i in range(npts):
        for j in range(i, npts):
            pairs.append((expanded[i], expanded[j]))
    return pairs
