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
Automatic auxiliary basis set generator.

Implements the procedure of Lehtola, J. Chem. Theory Comput. 17, 6886 (2021)
https://doi.org/10.1021/acs.jctc.1c00607 for selecting primitive auxiliary Gaussian
functions, and the contraction scheme of Lehtola, J. Chem. Theory Comput. 19,
6242 (2023) https://doi.org/10.1021/acs.jctc.3c00670 for forming a general-contracted
auxiliary basis.

The implementation is single-center / per-element and uses sympy for
analytic angular (Gaunt) and radial integrals.  Sympy is imported lazily;
only callers of :func:`generate_auxiliary_basis` require it.
"""

def generate_auxiliary_basis(*args, **kwargs):
    from .auxgen import generate_auxiliary_basis as _impl
    return _impl(*args, **kwargs)


def generate_auxiliary_basis_for_element(*args, **kwargs):
    from .auxgen import generate_auxiliary_basis_for_element as _impl
    return _impl(*args, **kwargs)


__all__ = [
    "generate_auxiliary_basis",
    "generate_auxiliary_basis_for_element",
]
