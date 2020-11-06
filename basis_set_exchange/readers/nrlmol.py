import re
from .. import lut
from . import helpers
import numpy

# Basis set starting line
start_re = re.compile(r'^([\d]+)\s+TOTAL NUMBER OF ATOM TYPES$')
# Element entry has two integers and text 
element_re = re.compile(r'^([\d]+)\s+([\d]+)\s+ELECTRONIC AND NUCLEAR CHARGE$')
# Number of primitives
nprim_re = re.compile(r'^([\d]+)\s+NUMBER OF BARE GAUSSIANS$')
# Number of s, p, and d functions
nspd_re = re.compile(r'^([\d]+)\s+([\d]+)\s+([\d]+)\s+NUMBER OF S,P,D FUNCTIONS$')
# Number of supplementary functions
nsup_re = re.compile(r'^([\d]+)\s+([\d]+)\s+([\d]+)\s+SUPPLEMENTARY S,P,D FUNCTIONS$')

def _parse_electron_lines(basis_lines, bs_data, extra=False):
    '''Parses lines representing all the electron shells for a single element

    Resulting information is stored in bs_data
    '''

    # Input line
    iline=0

    # Nuclear charge is
    Zel, element_Z = helpers.parse_line_regex(element_re, basis_lines[0], "Zel, Z")
    # We only support AE types at the moment
    assert(Zel == element_Z)

    # Get symbol
    element_sym = lut.element_name_from_Z(element_Z)
    element_data = helpers.create_element_data(bs_data, str(element_Z), 'electron_shells')

    # Number of primitives
    while not nprim_re.match(basis_lines[iline]):
        iline += 1
    nprim = helpers.parse_line_regex(nprim_re, basis_lines[iline], "nprim")

    # Number of spd functions
    while not nspd_re.match(basis_lines[iline]):
        iline += 1
    ns, np, nd = helpers.parse_line_regex(nspd_re, basis_lines[iline], "ns, np, nd")

    # Number of supplementary spd functions
    while not nsup_re.match(basis_lines[iline]):
        iline += 1
    nas, nap, nad = helpers.parse_line_regex(nsup_re, basis_lines[iline], "nas, nap, nad")

    # Collect exponents and coefficients from input
    def get_array(iline):
        array=[]
        missing=nprim
        while missing:
            iline=iline+1
            line=basis_lines[iline]
            entries=[x.replace('D','E') for x in line.split()]
            missing -= len(entries)
            array = array + entries
        return iline, array

    # Very first are the primitives
    iline, exps=get_array(iline)
    # Then come the s functions
    sfuncs=[]
    for ifunc in range(ns+nas):
        iline, coeffs=get_array(iline)
        sfuncs.append(coeffs)
    # the p functions
    pfuncs=[]
    for ifunc in range(np+nap):
        iline, coeffs=get_array(iline)
        pfuncs.append(coeffs)
    # and the d functions
    dfuncs=[]
    for ifunc in range(nd+nad):
        iline, coeffs=get_array(iline)
        dfuncs.append(coeffs)

    # Converts the contraction coefficients to standard form
    def convert(exps,coeffs,am):
        coeffs_arr = numpy.asarray([float(x) for x in coeffs])
        exps_arr = numpy.asarray([float(x) for x in exps])
        # Convert contraction coefficients to normal standard
        coeffs = numpy.multiply(coeffs_arr, numpy.power(exps_arr,-0.5*am-0.75))
        # except if there's only one exponent:
        nonzero = (coeffs_arr != 0.0)
        nonzeroc = coeffs[nonzero]
        if len(nonzeroc) == 1:
            coeffs[nonzero] = 1.0
        return coeffs

    # Adds the basis functions to the 
    def add_functions(exps,coeffs,norb,shell_am):
        # Collect the coefficients
        cmat=[]
        for iorb in range(norb):
            cmat.append(convert(exps,coeffs[iorb],shell_am))

        # Collect the contraction matrix in the normal nprim x norb format
        coeffs=[]
        for iprim in range(len(exps)):
            row=[]
            for iorb in range(norb):
                row.append('{: .8e}'.format(cmat[iorb][iprim]))
            coeffs.append(row)

        # Figure out which exponents are used for this angular momentum
        used_idx=[False for iprim in range(len(exps))]
        for iorb in range(norb):
            inuse = (numpy.asarray(cmat[iorb])!=0.0)
            used_idx = numpy.logical_or(used_idx,inuse)

        # Drop the unused primitives
        exps_used=[ exps[k] for k in range(len(exps)) if used_idx[k] ]
        coeffs_used=[ coeffs[k] for k in range(len(exps)) if used_idx[k] ]

        # BSE wants the transpose
        coeffs_trans=[]
        for iorb in range(norb):
            row=[]
            for iprim in range(len(exps_used)):
                row.append(coeffs_used[iprim][iorb])
            coeffs_trans.append(row)
        
        # NRLMOL uses a cartesian basis
        func_type = helpers.function_type_from_am([shell_am], 'gto', 'cartesian')
        shell = {
            'function_type': func_type,
            'region': '',
            'angular_momentum': [shell_am],
            'exponents': exps_used,
            'coefficients': coeffs_trans
        }

        element_data['electron_shells'].append(shell)

    # Add the basis functions
    add_functions(exps,sfuncs,ns+nas if extra else ns,0)
    add_functions(exps,pfuncs,np+nap if extra else np,1)
    add_functions(exps,dfuncs,nd+nad if extra else nd,2)

def read_nrlmol(basis_lines, extra=False):
    '''Reads NRLMOL formatted file data and converts it to a dictionary
       with the usual BSE fields

       Note that the NRLMOL format does not store all the fields we
       have, so some fields are left blank
    '''

    # Removes comments
    basis_lines = helpers.prune_lines(basis_lines, '!')

    bs_data = {}

    # Empty file?
    if not basis_lines:
        return bs_data

    # Get number of entries
    iline=0
    if not start_re.match(basis_lines[iline]):
        iline += 1
    ntypes = helpers.parse_line_regex(start_re, basis_lines[iline], "Ntypes")
    
    # split into element sections
    element_sections = helpers.partition_lines(basis_lines[iline+1:], element_re.match, min_size=3)
    assert(len(element_sections) == ntypes)
    for es in element_sections:
        _parse_electron_lines(es, bs_data, extra)

    return bs_data
