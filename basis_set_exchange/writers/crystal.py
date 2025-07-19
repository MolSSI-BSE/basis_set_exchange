# Copyright (c) 2017-2022 The Molecular Sciences Software Institute, Virginia Tech
#                    2025 Susi Lehtola
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

'''
Conversion of basis sets to Crystal format

Written by Susi Lehtola, 2020-2025
'''

from .. import manip, sort, printing


def write_crystal(basis):
    '''Converts a basis set to Crystal format
    '''

    basis = manip.uncontract_general(basis, True)
    basis = manip.uncontract_spdf(basis, 1, False)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

    # Returned string
    s = ''

    # Basis sets written together
    for z, data in basis['elements'].items():
        # Atomic number marking
        nat = int(z)
        if nat >= 99:
            #raise RuntimeError('Crystal format cannot handle elements beyond Z=98')
            continue
        if z in ecp_elements:
            # ECP carrying atoms have a displaced charge
            nat += 200

        # First line: nuclear charge and the number of shells
        s += '{} {}\n'.format(nat, len(data['electron_shells']))

        # Do we have an ECP?
        if z in ecp_elements:
            # Effective nuclear charge
            Zeff = int(z) - data['ecp_electrons']

            # What's the maximum angular momentum?
            max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])
            if max_ecp_am > 4:
                raise RuntimeError(
                    'ECP contains l={} term but Crystal format only supports up to g projectors!'.format(max_ecp_am))

            # Form the ecp entry block
            ecp_entries = ''
            num_terms = []
            def add_term(am):
                # Grab the ECP terms with this am
                am_ecp = [k for k in data['ecp_potentials'] if k['angular_momentum'] == [am]]
                n_terms = 0
                ecp_entry = ''
                for term in am_ecp:
                    exps = term['gaussian_exponents']
                    coefs = term['coefficients'][0]
                    rexp = term['r_exponents']
                    for i in range(len(exps)):
                        # r exponent in CRYSTAL format is the full one: it does NOT have the r^{-2} prefactor as in other formats
                        ecp_entry += '{} {} {}\n'.format(exps[i], coefs[i], rexp[i]-2)
                        n_terms += 1
                return ecp_entry, n_terms
                num_terms.append(n_terms)

            # The highest-am projector comes first
            ecp_entry, n_terms = add_term(max_ecp_am)
            ecp_entries += ecp_entry
            num_terms.append(n_terms)
            for am in range(max_ecp_am):
                ecp_entry, n_terms = add_term(am)
                ecp_entries += ecp_entry
                num_terms.append(n_terms)
            for am in range(max_ecp_am, 5):
                num_terms.append(0)
                
            # Print out the ECP header
            s += 'INPUT\n'
            s += '{:.0f}'.format(Zeff)
            for term in num_terms:
                s += f' {term}'
            s += '\n'
            # and the ECP data
            s += ecp_entries

        # Do we have basis functions?
        if z in electron_elements:
            for shell in data['electron_shells']:
                am = shell['angular_momentum']
                exponents = shell['exponents']
                coefficients = shell['coefficients']

                # type of basis: general basis
                ityb = 0
                # shell type, SP contractions not considered yet
                if len(am) == 2:
                    if am[0] != 0 or am[1] != 1:
                        raise RuntimeError('The only combined shells the Crystal interface supports are SP shells!')
                    lat = 1
                elif len(am) == 1:
                    lat = 0 if am[0] == 0 else am[0] + 1
                else:
                    raise RuntimeError('Crystal interface does not handle other combined shells than SP shells')

                # Number of primitives
                ng = len(exponents)
                # Number of columns
                ncol = len(coefficients) + 1
                # Formal charge: this is impossible for us to know!
                che = 0
                # Scale factor
                scal = 1
                # Print shell descriptor
                s += '{} {} {} {} {:.1f}\n'.format(ityb, lat, ng, che, scal)

                # Print out contractions
                point_places = [8 * i + 15 * (i - 1) for i in range(1, ncol + 1)]
                s += printing.write_matrix([exponents, *coefficients], point_places, convert_exp=True)

    # End of basis set input
    s += '99 0\n'
    return s
