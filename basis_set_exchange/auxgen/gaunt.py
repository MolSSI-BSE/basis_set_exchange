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
Real-spherical-harmonic Gaunt coefficients.

The coefficient

    G_R(l1 m1, l2 m2, l3 m3) = \\int S_{l1 m1}(\\Omega) S_{l2 m2}(\\Omega)
                                     S_{l3 m3}(\\Omega) d\\Omega

is evaluated using the ``wignernj`` library (exact integer arithmetic
with prime-factorization of factorials, two orders of magnitude faster
than sympy on the typical ``l <= 6`` range relevant here) when it is
available, and via :func:`sympy.physics.wigner.real_gaunt` otherwise.
Both implementations use the standard Condon-Shortley real-spherical-
harmonic convention and produce identical numerical values.

Selection rules: ``l1 + l2 + l3`` even, ``|l1 - l2| <= l3 <= l1 + l2``
(and analogous permutations).  Results are cached.
"""

from functools import lru_cache

import numpy as np

try:
    import wignernj as _wignernj  # https://pypi.org/project/wignernj/
    _HAVE_WIGNERNJ = True
except ImportError:
    _HAVE_WIGNERNJ = False


def _real_gaunt_wignernj(l1, m1, l2, m2, l3, m3):
    return _wignernj.gaunt_real(l1, m1, l2, m2, l3, m3)


def _real_gaunt_sympy(l1, m1, l2, m2, l3, m3):
    from sympy.physics.wigner import real_gaunt as _sym_real_gaunt
    return float(_sym_real_gaunt(l1, l2, l3, m1, m2, m3))


@lru_cache(maxsize=None)
def real_gaunt(l1, m1, l2, m2, l3, m3):
    """Real-spherical Gaunt coefficient as a float.

    Returns 0.0 when selection rules are violated.  Cached.
    """
    if abs(m1) > l1 or abs(m2) > l2 or abs(m3) > l3:
        return 0.0
    if (l1 + l2 + l3) % 2 != 0:
        return 0.0
    if l3 < abs(l1 - l2) or l3 > l1 + l2:
        return 0.0
    if _HAVE_WIGNERNJ:
        return _real_gaunt_wignernj(l1, m1, l2, m2, l3, m3)
    return _real_gaunt_sympy(l1, m1, l2, m2, l3, m3)


@lru_cache(maxsize=None)
def gaunt_table(la, lb, L):
    """Dense table ``G[ma_idx, mb_idx, M_idx]`` of real-Gaunt
    coefficients ``<S_{la,ma} S_{lb,mb} S_{LM}>`` with

        ma_idx = ma + la,    in [0, 2 la],
        mb_idx = mb + lb,    in [0, 2 lb],
        M_idx  = M + L,      in [0, 2 L].

    Most entries are zero by parity and m-sum selection; the table is
    stored dense so it can be contracted with numpy ``einsum`` directly.
    Cached.
    """
    g = np.zeros((2*la + 1, 2*lb + 1, 2*L + 1), dtype=float)
    for ma in range(-la, la + 1):
        for mb in range(-lb, lb + 1):
            for M in range(-L, L + 1):
                v = real_gaunt(la, ma, lb, mb, L, M)
                if v != 0.0:
                    g[ma + la, mb + lb, M + L] = v
    return g


@lru_cache(maxsize=None)
def coupling_lvals(l1, l2):
    """Allowed total angular momenta L when coupling l1 and l2 with the
    real-Gaunt parity rule l1+l2+L even.
    """
    return tuple(range(abs(l1 - l2), l1 + l2 + 1, 2))
