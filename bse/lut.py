'''
Lookup tables (lut) for converting to/from element names,
angular momentum characters, etc
'''


import os


# Open some text files to populate the tables
my_path = os.path.dirname(os.path.abspath(__file__))
el_data_path = os.path.join(my_path, 'element_map.txt')

# Maps Z to element data
element_Z_map = {}  # Maps Z to element data
element_sym_map = {}  # Maps element symbols to element data
element_name_map = {} # Maps element name to element data

with open(el_data_path, 'r') as f:
    for Z, sym, name in [x.split() for x in f.readlines()]:
        Z = int(Z)
        sym = sym.lower()
        name = name.lower()

        el_data = (Z, sym, name)

        element_Z_map[Z] = el_data
        element_sym_map[sym] = el_data
        element_name_map[name] = el_data


# Maps AM characters to integers (the integer is the
# index of the character in this string)
amchar_map = 'spdfghiklmnoqrtuvwxyzabce'


def element_data_from_Z(Z):
    '''Obtain elemental data given a Z number

    An exception is thrown if the Z number is not found
    '''

    if Z not in element_Z_map:
        raise RuntimeError('No element data for Z = {}'.format(Z))
    return element_Z_map[Z]


def element_data_from_sym(sym):
    '''Obtain elemental data given an elemental symbol

    The given symbol is not case sensitive

    An exception is thrown if the symbol is not found
    '''

    sym_lower = sym.lower()
    if sym_lower not in element_sym_map:
        raise RuntimeError('No element data for symbol \'{}\''.format(sym))
    return element_sym_map[sym_lower]


def element_data_from_name(name):
    '''Obtain elemental data given an elemental name

    The given name is not case sensitive

    An exception is thrown if the name is not found
    '''

    name_lower = name.lower()
    if name_lower not in element_name_map:
        raise RuntimeError('No element data for name \'{}\''.format(name))
    return element_name_map[name_lower]


def element_name_from_Z(Z):
    '''Obtain an element's name from its Z number

    An exception is thrown if the Z number is not found
    '''
    return element_data_from_Z(Z)[2]


def element_sym_from_Z(Z):
    '''Obtain an element's symbol from its Z number

    An exception is thrown if the Z number is not found
    '''
    return element_data_from_Z(Z)[1]



def normalize_element_symbol(sym):
    '''Normalize the capitalization of an element symbol

    For example, converts "he" to "He" and "uUo" to "Uuo"
    '''

    sym = sym.lower()
    sym2 = sym[0].upper()
    sym2 += sym[1:]
    return sym2


def normalize_element_name(name):
    '''Normalize the capitalization of an element name

    For example, converts "helium" to "Helium" and "aRgOn" to "Argon"
    '''

    name = name.lower()
    name2 = name[0].upper()
    name2 += name[1:]
    return name2


def amint_to_char(am):
    '''Convert an angular momentum integer to a character

    The input is a list (to handle sp, spd, ... orbitals). The return
    value is a string

    For example, converts [0] to 's' and [0,1,2] to 'spd'
    '''

    amchar = []

    for a in am:
        if a < 0:
            raise RuntimeError('Angular momentum must be a positive integer (not {})'.format(a))
        if a >= len(amchar_map):
            raise RuntimeError('Angular momentum {} out of range. Must be less than {}'.format(a, len(amchar_map)))
        amchar.append(amchar_map[am])

    return amchar 


def amchar_to_int(amchar):
    '''Convert an angular momentum integer to a character

    The return value is a list of integers (to handle sp, spd, ... orbitals)

    For example, converts 'p' to [1] and 'sp' to [0,1]
    '''

    amchar_lower = amchar.lower()

    amint = []

    for c in amchar_lower:
        if c not in amchar_map:
            raise RuntimeError('Angular momentum character {} is not valid'.format(c))

        amint.append(amchar_map.index(c))

    return amint
