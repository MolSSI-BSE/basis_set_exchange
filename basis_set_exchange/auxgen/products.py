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

from .gaunt import coupling_lvals
from .radial import alpha_eff


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
    for shell in element_basis.get('electron_shells', []):
        if not _shell_function_types_ok(shell):
            raise ValueError("auxgen: unsupported function_type %r" % shell.get('function_type'))
        cart = _is_cartesian(shell)
        exps = [float(e) for e in shell['exponents']]
        for L in shell['angular_momentum']:
            for l_ang in _angular_components(int(L), cart):
                for a in exps:
                    seen[(int(l_ang), int(L), float(a))] = True
    items = list(seen.keys())
    items.sort(key=lambda x: (x[0], x[1], -x[2]))
    return items


def _match_single_primitive(L, exps, coeffs):
    """Exponent ``beta`` of the single primitive ``r^L e^{-beta r^2}``
    that maximizes the (normalized) overlap with the contracted function
    ``sum_k coeffs[k] * (normalized r^L e^{-exps[k] r^2})``.

    The normalized overlap of two primitives at radial power ``L`` is
    ``[2 sqrt(a b) / (a + b)]^{L + 3/2}``, so the objective is

        f(beta) = | sum_k coeffs[k] [2 sqrt(exps[k] beta)
                                     / (exps[k] + beta)]^{L + 3/2} |,

    maximized by a log-space grid scan followed by golden-section
    refinement (no SciPy dependency).
    """
    p = L + 1.5
    a = [float(x) for x in exps]
    c = [float(x) for x in coeffs]

    def overlap(beta):
        s = 0.0
        for ak, ck in zip(a, c):
            t = 2.0 * math.sqrt(ak * beta) / (ak + beta)
            s += ck * t ** p
        return abs(s)

    lo = math.log(min(a)) - 2.0
    hi = math.log(max(a)) + 2.0
    npts = 200
    best_x, best = lo, -1.0
    for i in range(npts + 1):
        x = lo + (hi - lo) * i / npts
        v = overlap(math.exp(x))
        if v > best:
            best, best_x = v, x

    # Golden-section refine within one grid step of the scan maximum.
    h = (hi - lo) / npts
    aL, bR = best_x - h, best_x + h
    gr = (math.sqrt(5.0) - 1.0) / 2.0
    cL = bR - gr * (bR - aL)
    dR = aL + gr * (bR - aL)
    fcL, fdR = overlap(math.exp(cL)), overlap(math.exp(dR))
    for _ in range(60):
        if fcL < fdR:
            aL, cL, fcL = cL, dR, fdR
            dR = aL + gr * (bR - aL)
            fdR = overlap(math.exp(dR))
        else:
            bR, dR, fdR = dR, cL, fcL
            cL = bR - gr * (bR - aL)
            fcL = overlap(math.exp(cL))
    return math.exp(0.5 * (aL + bR))


def decontract_primitives_single(element_basis):
    """Like :func:`decontract_primitives`, but each *contracted* orbital
    function is replaced by a single primitive whose exponent is matched
    by the overlap criterion (:func:`_match_single_primitive`).  Free
    (single-primitive) functions are kept unchanged.

    Combined ``sp``/``spd`` shells are split first; cartesian shells
    still expand into their lower-l contamination at the matched
    exponent.  Returns the same ``(l_angular, n_radial, alpha)`` triple
    list as :func:`decontract_primitives`.
    """
    from .. import manip
    split = manip.uncontract_spdf({'elements': {'1': element_basis}},
                                  max_am=0, use_copy=True)['elements']['1']
    seen = {}
    for shell in split.get('electron_shells', []):
        if not _shell_function_types_ok(shell):
            raise ValueError("auxgen: unsupported function_type %r" % shell.get('function_type'))
        cart = _is_cartesian(shell)
        exps = [float(e) for e in shell['exponents']]
        L = int(shell['angular_momentum'][0])
        for col in shell['coefficients']:
            c = [float(x) for x in col]
            nz = [i for i, x in enumerate(c) if x != 0.0]
            if not nz:
                continue
            beta = exps[nz[0]] if len(nz) == 1 else _match_single_primitive(L, exps, c)
            for l_ang in _angular_components(L, cart):
                seen[(int(l_ang), L, float(beta))] = True
    items = list(seen.keys())
    items.sort(key=lambda x: (x[0], x[1], -x[2]))
    return items


def _shellpair_L_range(li, lj):
    """Allowed total angular momenta when coupling shells of angular
    momentum ``li`` and ``lj``: ``|li - lj|``, ``|li - lj| + 2``,
    ..., ``li + lj``.  The stride-of-two reflects the real-spherical
    Gaunt parity rule ``li + lj + L`` even -- parity-forbidden L give
    zero coupling to any orbital-product channel and therefore are
    pointless aux candidates.
    """
    return range(abs(li - lj), li + lj + 1, 2)


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
    pool = {}
    n = len(primitives)
    for i in range(n):
        l_i, n_i, a_i = primitives[i]
        for j in range(i, n):
            l_j, n_j, a_j = primitives[j]
            n_rad = n_i + n_j
            a_rad = float(a_i + a_j)
            for L in _shellpair_L_range(l_i, l_j):
                pool.setdefault(L, []).append(alpha_eff(L, n_rad, a_rad, mapping))
    out = {}
    for L, alphas in pool.items():
        # Deduplicate at floating-point tolerance.
        seen = {}
        for a in alphas:
            key = round(a, 10)
            seen[key] = a
        out[L] = sorted(seen.values(), reverse=True)
    return out


def candidate_pool_from_pairs(selected_pairs, mapping='moment'):
    """Build the per-L candidate pool from m-resolved primitive pairs
    selected by the reduced-scheme 4-index pre-screening.  The same
    Appendix II transformation is applied as in
    :func:`candidate_pool_from_primitives`.

    Each entry in ``selected_pairs`` is
    ``((l_a, n_a, m_a, alpha_a), (l_b, n_b, m_b, alpha_b))``.
    """
    pool = {}
    for (la, na, _ma, aa), (lb, nb, _mb, ab) in selected_pairs:
        n_rad = na + nb
        a_rad = float(aa + ab)
        for L in _shellpair_L_range(la, lb):
            pool.setdefault(L, []).append(alpha_eff(L, n_rad, a_rad, mapping))
    out = {}
    for L, alphas in pool.items():
        seen = {}
        for a in alphas:
            seen[round(a, 10)] = a
        out[L] = sorted(seen.values(), reverse=True)
    return out


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
