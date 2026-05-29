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
Closed-form one-center radial Coulomb integrals for Gaussian primitives.

For functions f_i(r) = r^{n_i - 1} e^{-zeta_i r^2}, the angular-projected
radial Coulomb integral

    R^v(a, b, c, d) = \\int_0^\\infty \\int_0^\\infty
        f_a(r_1) f_b(r_1) f_c(r_2) f_d(r_2)
        (r_<^v / r_>^{v+1}) r_1^2 r_2^2 dr_1 dr_2

has the closed form due to R. M. Pitzer, "Atomic self-consistent-field
program by the basis set expansion method: Columbus version",
Comput. Phys. Commun. 170, 239 (2005)
[https://doi.org/10.1016/j.cpc.2005.04.003]:

    R_{mnv}(x, y) = Gamma((m+n-1)/2)
                    / (x y (x+y)^{(m+n-3)/2}) * 1/4
                    * [1 + E_k_n((n-v-2)/2, y/x)
                         + E_k_n((m-v-2)/2, x/y)]

with ``m = n_a + n_b``, ``n = n_c + n_d``, ``v`` the multipole, and

    E_n_k(n, k, x) = (sum_{j=0}^{k-1} C(n, j) x^j) / [C(n, k) x^k].

For the basic-scheme metric in this package, we map the candidate
parameters (l_rad_A, l_rad_B, L) to (m, n, v) = (L_A + 2, L_B + 2, L)
so that

    R_L(a, L_A; b, L_B) := \\int\\int r_1^{L_A + 2} e^{-a r_1^2}
                                      r_2^{L_B + 2} e^{-b r_2^2}
                                      (r_<^L / r_>^{L+1}) dr_1 dr_2
                          = R_{(L_A + 2)(L_B + 2)L}(a, b).

Selection rules: L <= L_A, L <= L_B, L_A + L even, L_B + L even.

The Coulomb expression is implemented analytically here and used by the
rest of the auxgen module.  Sympy is not used at runtime.
"""

from functools import lru_cache
from math import gamma, sqrt

_HAVE_NUMPY = True
try:
    import numpy as _np
except ImportError:  # numpy is the right path for vectorized eval
    _HAVE_NUMPY = False


# ---------------------------------------------------------------------------
# Helper: binomial coefficient with a half-integer ``n``.
# ---------------------------------------------------------------------------

def _binomial(n, k):
    """Binomial coefficient C(n, k) for non-negative integer ``k`` and
    any real ``n`` (in practice ``n`` is half-integer for the GTO case).
    """
    return gamma(n + 1.0) / (gamma(n - k + 1.0) * gamma(k + 1.0))


def _Enk(n, k, x):
    """Evaluate

        E_k_n(n, k, x) = (sum_{j=0}^{k-1} C(n, j) x^j) / [C(n, k) x^k].

    ``k`` is a non-negative integer; ``x`` may be a scalar or numpy
    array.  For ``k == 0`` returns 0.
    """
    if k == 0:
        if _HAVE_NUMPY and isinstance(x, _np.ndarray):
            return _np.zeros_like(x, dtype=float)
        return 0.0
    cnk = _binomial(n, k)
    if _HAVE_NUMPY and isinstance(x, _np.ndarray):
        num = _np.zeros_like(x, dtype=float)
        for j in range(k):
            num = num + _binomial(n, j) * x**j
        return num / (cnk * x**k)
    num = 0.0
    for j in range(k):
        num += _binomial(n, j) * x**j
    return num / (cnk * x**k)


def _Rmnv(m, n, v, x, y):
    """Closed-form GTO radial Coulomb integral, Pitzer convention
    (R. M. Pitzer, "Atomic self-consistent-field program by the basis
    set expansion method: Columbus version", Comput. Phys. Commun. 170,
    239 (2005), https://doi.org/10.1016/j.cpc.2005.04.003).  ``m``,
    ``n``, ``v`` are integers; ``x``, ``y`` are positive scalars or
    numpy arrays.
    """
    half_mid = (m + n - 3) / 2.0
    kn = (n - v - 2) // 2
    km = (m - v - 2) // 2
    pref = gamma((m + n - 1) / 2.0) / (x * y * (x + y)**half_mid)
    return pref * (1.0 + _Enk(half_mid, kn, y / x) + _Enk(half_mid, km, x / y)) / 4.0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@lru_cache(maxsize=200000)
def _radial_scalar_cached(L, LA, LB, alpha, beta):
    """Cached scalar variant of :func:`radial_integral`.

    The cache key (``L``, ``LA``, ``LB``, ``alpha``, ``beta``) saturates
    quickly: in the 4-index pre-screening only a few thousand distinct
    tuples occur, but each gets queried millions of times by the
    m-resolved iteration.
    """
    return _Rmnv(LA + 2, LB + 2, L, alpha, beta)


def radial_integral(L, LA, LB, alpha, beta):
    """Closed-form R_L(alpha, L_A; beta, L_B).

    Returns 0 when the selection rules are violated.  Accepts scalar or
    numpy-array ``alpha``/``beta`` (with broadcastable shapes); scalar
    invocations are memoized via :func:`_radial_scalar_cached`.
    """
    L = int(L); LA = int(LA); LB = int(LB)
    if L > LA or L > LB or (LA + L) % 2 or (LB + L) % 2:
        if _HAVE_NUMPY and (isinstance(alpha, _np.ndarray) or isinstance(beta, _np.ndarray)):
            return _np.zeros(_np.broadcast_shapes(_np.shape(alpha), _np.shape(beta)),
                             dtype=float)
        return 0.0
    if _HAVE_NUMPY and (isinstance(alpha, _np.ndarray) or isinstance(beta, _np.ndarray)):
        return _Rmnv(LA + 2, LB + 2, L, alpha, beta)
    return _radial_scalar_cached(L, LA, LB, float(alpha), float(beta))


def precompute_radial(L_max):
    """Compatibility shim with previous sympy-based interface.  The
    closed-form evaluator does not need to be warmed up, so this is a
    no-op."""
    return None


@lru_cache(maxsize=4096)
def gto_norm(n, alpha):
    """Overlap norm constant N such that chi(r) = N r^n e^{-alpha r^2}
    Y_lm has <chi|chi> = 1, i.e.

        N = sqrt(2 (2 alpha)^(n + 3/2) / Gamma(n + 3/2)).

    Here ``n`` is the radial power (not the angular momentum); for
    standard spherical Gaussians ``n = l``, but a cartesian-shell
    contamination may have ``n > l``.  Memoized -- the number of unique
    ``(n, alpha)`` pairs is bounded by the orbital primitive count.
    """
    return sqrt(2.0 * (2.0 * alpha)**(n + 1.5) / gamma(n + 1.5))


def gto_norm_array(n, alphas):
    """Vectorized version of :func:`gto_norm`."""
    if not _HAVE_NUMPY:
        return [gto_norm(n, a) for a in alphas]
    a = _np.asarray(alphas, dtype=float)
    return _np.sqrt(2.0 * (2.0 * a)**(n + 1.5) / gamma(n + 1.5))


def alpha_eff(L, n_rad, alpha_rad):
    """Effective exponent for converting an ``(n_rad, alpha_rad)``
    candidate at angular momentum L to a standard r^L e^{-alpha_eff r^2}
    primitive, matching the radial expectation value <r> (Lehtola,
    J. Chem. Theory Comput. 17, 6886 (2021)
    [https://doi.org/10.1021/acs.jctc.1c00607], Appendix II eq 16):

        alpha_eff = [ Gamma(L+2) Gamma(n_rad + 3/2)
                      / ( Gamma(L + 3/2) Gamma(n_rad + 2) ) ]**2
                    * alpha_rad.

    For ``n_rad = L`` the scale factor is unity and
    ``alpha_eff = alpha_rad``.  For ``n_rad > L`` the scale factor is
    < 1 and the candidate is more diffuse, in line with the more
    diffuse r^{n_rad} radial product.
    """
    s = (gamma(L + 2) * gamma(n_rad + 1.5)) / (gamma(L + 1.5) * gamma(n_rad + 2))
    return float(s * s * alpha_rad)
