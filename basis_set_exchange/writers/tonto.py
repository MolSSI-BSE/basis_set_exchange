# Copyright (c) 2025 Lucas Militão - LaMuCrEs - São Carlos Institute for Physics - University of São Paulo
# Thanks to the The Molecular Sciences Software Institute, Virginia Tech for serving as a basis for this writer
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
Conversion of basis sets to Tonto format
'''

from .. import lut, manip, sort, printing


def write_tonto(basis):
    '''Converts a basis set to Tonto format
    '''

    # The role of the basis set determines what is put here
    role = basis.get('role', 'orbital')

    # Start the basis section
    s = '{\n\n'
    s += 'keys= { turbomole= }\n\n'
    s += 'data= {\n\n'

    # TM basis sets are completely uncontracted
    basis = manip.uncontract_general(basis, True)
    basis = manip.uncontract_spdf(basis, 0, False)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

    # Electron Basis
    if electron_elements:
        for z in electron_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z, True)
            s += f'{sym}:{basis["name"]}\n{{\n'

            for shell in data['electron_shells']:
                exponents = shell['exponents']
                coefficients = shell['coefficients']
                nprim = len(exponents)

                am = shell['angular_momentum']
                amchar = lut.amint_to_char(am, hij=False)
                s += '    {}  {}\n'.format(nprim, amchar)

                for i, exp in enumerate(exponents):
                    exp_val = float(exp)
                    line = "     "
                    # Format with standard scientific notation but without the 'e' or 'E'
                    exp_formatted = f"{exp_val:14.7f}".rstrip('0').rstrip('.')
                    line += f" {exp_formatted}".ljust(20)

                    for coef_list in coefficients:
                        coef_val = float(coef_list[i])
                        # For values near 1.0, just display as 1.0000000
                        if abs(coef_val - 1.0) < 1e-10:
                            coef_formatted = "1.0000000"
                        else:
                            coef_formatted = f"{coef_val:14.7f}".rstrip('0').rstrip('.')
                        line += f" {coef_formatted}".ljust(20)

                    s += line + "\n"
            s += '}\n\n'

    # Write out ECP if needed
    if ecp_elements:
        for z in ecp_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z, False)
            s += '{}:{}-ecp\n{{\n'.format(sym, basis['name'])

            max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])
            s += '    ncore = {}   lmax = {}\n'.format(data['ecp_electrons'], max_ecp_am)

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])
            ecp_list.insert(0, ecp_list.pop())

            for pot in ecp_list:
                rexponents = pot['r_exponents']
                gexponents = pot['gaussian_exponents']
                coefficients = pot['coefficients']

                am = pot['angular_momentum']
                amchar = lut.amint_to_char(am, hij=True)
                max_ecp_amchar = lut.amint_to_char([max_ecp_am], hij=True)

                if am[0] == max_ecp_am:
                    s += '    {}\n'.format(amchar)
                else:
                    s += '    {}-{}\n'.format(amchar, max_ecp_amchar)

                for i in range(len(rexponents)):
                    rexp_val = float(rexponents[i])
                    gexp_val = float(gexponents[i])
                    coef_val = float(coefficients[0][i])

                    line = "     "
                    coef_formatted = f"{coef_val:14.7f}".rstrip('0').rstrip('.')
                    rexp_formatted = f"{rexp_val:14.7f}".rstrip('0').rstrip('.')
                    gexp_formatted = f"{gexp_val:14.7f}".rstrip('0').rstrip('.')

                    s += f" {coef_formatted}".ljust(20)
                    s += f" {rexp_formatted}".ljust(15)
                    s += f" {gexp_formatted}\n"
            s += '}\n\n'

    s += '}\n\n}'
    return s
