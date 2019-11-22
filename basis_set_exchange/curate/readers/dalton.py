import re
from ... import lut
from ..skel import create_skel
from .common import partition_line_list, parse_primitive_matrix, prune_lines

all_element_names = [x.upper() for x in lut.all_element_names()]
all_element_names.extend('WOLFFRAM')  # For tungsten

# Lines beginning a shell can be:
#   H {nprim} {ngen}
# or
#   {nprim} {ngen} 0
# This regex handles both cases
_shell_begin_re = re.compile(r'^(?:H +)?(\d+) +(\d+)(?: +0)?$')


def _line_begins_element(line):
    if not line:
        return False
    if line.startswith('a '):
        return True
    if line[0] == '!' and len(line) > 2:
        s = line[2:].split()
        if s[0] in all_element_names:
            return True

    return False


def _parse_dalton_block(block):
    # Figure out which type of block this is
    header = block[0]
    if header.lower().startswith('a'):
        element_Z = int(header.split()[1])
    elif header.startswith('! '):
        element_Z = lut.element_Z_from_name(header.split()[1])
    else:
        raise RuntimeError("Unable to parse block in dalton: header line is \"{}\"".format(header))

    block = block[1:]

    # Now partition again into blocks of shells
    block = [x for x in block if not x.startswith('!')]
    shell_blocks = partition_line_list(block, lambda x: _shell_begin_re.match(x), start=0)

    shell_am = 0

    shells = []
    for block in shell_blocks:
        m = _shell_begin_re.match(block[0])
        if not m:
            raise RuntimeError("Line does not match beginning of shell: " + block[0])
        nprim, ngen = m.groups()
        exponents, coefficients = parse_primitive_matrix(block[1:])

        if shell_am <= 1:
            func_type = 'gto'
        else:
            func_type = 'gto_spherical'

        shell = {'function_type': func_type,
                 'region': '',
                 'angular_momentum': [shell_am],
                 'exponents': exponents,
                 'coefficients': coefficients}
        shells.append(shell)
        shell_am += 1

    return (str(element_Z), {'electron_shells': shells})


def read_dalton(basis_lines, fname):
    '''Reads Dalton-formatted file data and converts it to a dictionary with the
       usual BSE fields
    '''

    # There seems to be several dalton formats. One splits out by element, with
    # each element block starting with "a {element_Z}". Then each shell
    # starts with "{nprim} {ngen} 0"
    # The second is also split by elements, but the element name
    # is in a comment...

    basis_lines = prune_lines(basis_lines, '$')

    # Skip forward until either:
    # 1. Line begins with 'a'
    # 2. Lines begins with '!', with an element name following
    i = 0
    while not _line_begins_element(basis_lines[i]):
        i += 1

    # Now go through and find all element blocks
    all_blocks = partition_line_list(basis_lines, _line_begins_element, start=i)

    # Skip blocks with only 1 line. This represents duplicated element header lines
    all_blocks = [x for x in all_blocks if len(x) > 1]

    # Now parse each block into shells
    element_data = [_parse_dalton_block(x) for x in all_blocks]

    bs_data = create_skel('component')
    bs_data['elements'] = dict(element_data)

    return bs_data
