# Copyright (c) 2017-2022 The Molecular Sciences Software Institute, Virginia Tech
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
Functions related to validating JSON files (including against schema)
"""

import os
import jsonschema
import datetime

from . import fileio, misc

_my_dir = os.path.dirname(os.path.abspath(__file__))
_default_schema_dir = os.path.join(_my_dir, 'schema')


def _list_has_duplicates(lst):
    '''Check if a list has only unique elements
       Returns a list of duplicated elements'''

    dupe = []
    for x in lst:
        if lst.count(x) != 1:
            dupe.append(x)
    return dupe


def _list_has_nonpositives(lst):
    '''Check if a list of floats has nonpositive elements
       Returns a list of nonpositive elements'''

    nonpos = []
    for x in lst:
        if float(x) <= 0.0:
            nonpos.append(x)
    return nonpos


def _validate_extra_references(bs_data):
    '''Extra checks for references files'''
    pass


def _validate_extra_metadata(bs_data):
    '''Extra checks for metadata files'''

    # Check that family is lowercase
    fam = bs_data['family']
    if not fam.islower():
        raise RuntimeError("Family '{}' is not lowercase".format(fam))


def _validate_electron_shells(shells, element_z):
    '''Validate a list of electron shells'''

    for idx, s in enumerate(shells):
        nprim = len(s['exponents'])
        if nprim <= 0:
            raise RuntimeError("Element {} Shell {}: Invalid number of primitives: {}".format(element_z, idx, nprim))

        # If max(am) > 1, gto types must specify spherical or cartesian
        if max(s['angular_momentum']) > 1:
            if s['function_type'] not in ['gto_spherical', 'gto_cartesian']:
                raise RuntimeError(
                    "Element {} Shell {}: Shell with max am > p, but spherical/cartesian not specified".format(
                        element_z, idx))
        else:
            # If max(am) < 2, spherical/cartesian not allowed
            if 'spherical' in s['function_type'] or 'cartesian' in s['function_type']:
                raise RuntimeError("Element {} Shell {}: AM = {} marked as spherical or cartesian: {}".format(
                    element_z, idx, str(s['angular_momentum']), s['function_type']))

        # Duplicate exponents (when converted to float)?
        exponents_f = [float(x) for x in s['exponents']]
        dupe_ex = _list_has_duplicates(exponents_f)
        if dupe_ex:
            raise RuntimeError("Element {} Shell {}: Has duplicate exponents: {}".format(element_z, idx, dupe_ex))

        # Nonpositive exponents?
        nonpos_ex = _list_has_nonpositives(exponents_f)
        if nonpos_ex:
            raise RuntimeError("Element {} Shell {}: Has negative exponents: {}".format(element_z, idx, nonpos_ex))

        for g in s['coefficients']:
            if nprim != len(g):
                raise RuntimeError(
                    "Element {} Shell {}: Number of coefficients doesn't match number of primitives ({} vs {})".format(
                        element_z, idx, len(g), nprim))

            # Column of zero coefficients?
            coefficients_f = [float(x) for x in g]
            if all(x == 0.0 for x in coefficients_f):
                raise RuntimeError("Element {} Shell {}: Has column of coefficients with all = 0.0".format(
                    element_z, idx))

        # Duplicate columns of coefficients?
        # Only test this is not a fused shell (which can have duplicates)
        all_coefficients_f = [[float(x) for x in g] for g in s['coefficients']]
        if len(s['angular_momentum']) == 1:
            dupe_coef_col = _list_has_duplicates(all_coefficients_f)
            if dupe_coef_col:
                raise RuntimeError("Element {} Shell {}: Duplicate columns of coefficients: {}".format(
                    element_z, idx, dupe_coef_col))

        # Does a primitive have all zeroes in the coefficients?
        coeff_t = misc.transpose_matrix(all_coefficients_f)
        for pidx, row in enumerate(coeff_t):
            if all(x == 0.0 for x in row):
                raise RuntimeError("Element {} Shell {} Primitive {}: Primitive is unused (all coeffs = 0.0)".format(
                    element_z, idx, pidx))

        # If more than one AM is given, that should be the number of
        # general contractions
        nam = len(s['angular_momentum'])
        if nam > 1:
            ngen = len(s['coefficients'])
            if ngen != nam:
                raise RuntimeError(
                    "Element {} Shell {}: Number of general contractions doesn't match combined AM ({} vs {})".format(
                        element_z, idx, ngen, nam))


def _validate_ecp_potentials(potentials, ecp_electrons, element_z):
    # Check for duplicate AM and 'fused' AM
    all_am = [x['angular_momentum'] for x in potentials]
    for am in all_am:
        if len(am) > 1:
            raise RuntimeError("Element {} ECP: Fused AM in potentials (not supported)".format(element_z))

    all_am = [x[0] for x in all_am]
    dupe_am = _list_has_duplicates(all_am)
    if dupe_am:
        raise RuntimeError("Element {} ECP: Duplicated angular momentum: {}".format(element_z, dupe_am))

    # Need this for later
    max_am = max(pot['angular_momentum'] for pot in potentials)

    for idx, pot in enumerate(potentials):
        nexp = len(pot['r_exponents'])
        if len(pot['gaussian_exponents']) != nexp:
            raise RuntimeError("Element {} ECP Potential {}: len(r_exponents) != len(gaussian_exponents)".format(
                element_z, idx))

        for g in pot['coefficients']:
            if nexp != len(g):
                raise RuntimeError(
                    "Element {} ECP Potential {}: Number of coefficients doesn't match number of exponents ({} vs {})".
                    format(element_z, idx, len(g), nexp))

            # Column of zero coefficients?
            # Sometimes there is a potential with one exponent and a zero coefficient, but that should be the highest AM
            if nexp > 1 or pot['angular_momentum'] != max_am:
                coefficients_f = [float(x) for x in g]
                if all(x == 0.0 for x in coefficients_f):
                    raise RuntimeError("Element {} ECP Potential {}: Has column of coefficients with all = 0.0".format(
                        element_z, idx))

        # Duplicated columns of coefficients?
        all_coefficients_f = [[float(x) for x in g] for g in pot['coefficients']]
        dupe_coef_col = _list_has_duplicates(all_coefficients_f)
        if dupe_coef_col:
            raise RuntimeError("Element {} ECP Potential {}: Duplicate columns of coefficients: {}".format(
                element_z, idx, dupe_coef_col))

        # Check for rows with 0.0 in the coefficients, except for max_am with nexp == 1
        if nexp > 1 or pot['angular_momentum'] != max_am:
            coeff_t = misc.transpose_matrix(all_coefficients_f)
            for pidx, row in enumerate(coeff_t):
                if all(x == 0.0 for x in row):
                    raise RuntimeError(
                        "Element {} Shell {} Primitive {}: Primitive is unused (all coeffs = 0.0)".format(
                            element_z, idx, pidx))


def _validate_element(el_data, element_z):
    if 'electron_shells' in el_data:
        _validate_electron_shells(el_data['electron_shells'], element_z)

    if 'ecp_potentials' in el_data:
        if 'ecp_electrons' not in el_data:
            raise RuntimeError("ecp_electrons doesn't exist for element {}, but ecp_potentials does".format(element_z))
        _validate_ecp_potentials(el_data['ecp_potentials'], el_data['ecp_electrons'], element_z)


def _validate_extra_component(bs_data):
    '''Extra checks for component basis files'''

    assert len(bs_data['elements']) > 0

    for element_z, el_data in bs_data['elements'].items():
        _validate_element(el_data, element_z)


def _validate_extra_element(bs_data):
    '''Extra checks for basis metadata files'''

    assert len(bs_data['elements']) > 0


def _validate_extra_table(bs_data):
    '''Extra checks for table basis files'''

    assert len(bs_data['elements']) > 0

    # Will throw an exception on invalid dates
    datetime.datetime.strptime(bs_data['revision_date'], "%Y-%m-%d")


def _validate_extra_complete(bs_data):
    '''Extra checks for complete basis set data'''

    assert len(bs_data['elements']) > 0

    # Make sure 'name' exists in the list of 'names'
    if not bs_data['name'] in bs_data['names']:
        raise RuntimeError("Name {} not part of names: {}".format(bs_data['name'], bs_data['names']))

    for element_z, el_data in bs_data['elements'].items():
        _validate_element(el_data, element_z)


def _validate_extra_minimal(bs_data):
    '''Extra checks for minimal basis set data'''

    assert len(bs_data['elements']) > 0

    for element_z, el_data in bs_data['elements'].items():
        _validate_element(el_data, element_z)


_validate_map = {
    'references': _validate_extra_references,
    'metadata': _validate_extra_metadata,
    'component': _validate_extra_component,
    'element': _validate_extra_element,
    'table': _validate_extra_table,
    'complete': _validate_extra_complete,
    'minimal': _validate_extra_minimal
}


def _get_schema(file_type):
    '''Get a schema that can validate BSE JSON files or dictionaries

       The schema_type represents the type of BSE JSON file to be validated,
       and can be 'component', 'element', 'table', 'metadata', or 'references'.

       Returns the schema and the reference resolver
    '''

    schema_file = "{}-schema.json".format(file_type)
    file_path = os.path.join(_default_schema_dir, schema_file)

    schema = fileio.read_schema(file_path)

    # Set up the resolver for links
    base_uri = 'file:///{}/'.format(_default_schema_dir)
    resolver = jsonschema.RefResolver(base_uri=base_uri, referrer=schema)

    return schema, resolver


def validate_data(file_type, bs_data):
    """
    Validates json basis set data against a schema

    Parameters
    ----------
    file_type : str
        Type of the data to validate. May be 'component', 'element', 'table', 'complete', 'minimal', or 'references'
    bs_data:
        Data to be validated

    Raises
    ------
    RuntimeError
        If the file_type is not valid (and/or a schema doesn't exist)
    ValidationError
        If the given file does not pass validation
    FileNotFoundError
        If the file given by file_path doesn't exist
    """

    if file_type not in _validate_map:
        raise RuntimeError("{} is not a valid file_type".format(file_type))

    schema, resolver = _get_schema(file_type)
    jsonschema.validate(bs_data, schema, resolver=resolver)
    _validate_map[file_type](bs_data)


def validate_file(file_type, file_path):
    """
    Validates a file against a schema

    Parameters
    ----------
    file_type : str
        Type of file to read. May be 'component', 'element', 'table', 'complete', 'minimal', or 'references'
    file_path:
        Full path to the file to be validated

    Raises
    ------
    RuntimeError
        If the file_type is not valid (and/or a schema doesn't exist)
    ValidationError
        If the given file does not pass validation
    FileNotFoundError
        If the file given by file_path doesn't exist
    """

    file_data = fileio._read_plain_json(file_path, False)
    validate_data(file_type, file_data)


def validate_data_dir(data_dir):
    """
    Validates all files in a data_dir
    """

    all_meta, all_table, all_element, all_component = fileio.get_all_filelist(data_dir)

    for f in all_meta:
        full_path = os.path.join(data_dir, f)
        validate_file('metadata', full_path)
    for f in all_table:
        full_path = os.path.join(data_dir, f)
        validate_file('table', full_path)
    for f in all_element:
        full_path = os.path.join(data_dir, f)
        validate_file('element', full_path)
    for f in all_component:
        full_path = os.path.join(data_dir, f)
        validate_file('component', full_path)
