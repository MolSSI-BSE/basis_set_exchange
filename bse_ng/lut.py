
import os


my_path = os.path.dirname(os.path.abspath(__file__))
el_data_path = os.path.join(my_path, 'element_map.txt')

element_Z_map = {}
element_sym_map = {}
element_name_map = {}

with open(el_data_path, 'r') as f:
    for Z, sym, name in [x.split() for x in f.readlines()]:
        Z = int(Z)
        sym = sym.lower()
        name = name.lower()

        el_data = (Z, sym, name)

        element_Z_map[Z] = el_data
        element_sym_map[sym] = el_data
        element_name_map[name] = el_data


amchar_map = 'spdfghiklmnoqrtuvwxyzabce'


def element_data_from_Z(Z):
    if Z not in element_Z_map:
        raise RuntimeError('No element data for Z = {}'.format(Z))
    return element_Z_map[Z]


def element_data_from_sym(sym):
    sym_lower = sym.lower()
    if sym_lower not in element_sym_map:
        raise RuntimeError('No element data for symbol \'{}\''.format(sym))
    return element_sym_map[sym_lower]


def element_data_from_name(name):
    name_lower = name.lower()
    if name_lower not in element_name_map:
        raise RuntimeError('No element data for name \'{}\''.format(name))
    return element_name_map[name_lower]


def normalize_element_symbol(sym):
    sym = sym.lower()
    sym2 = sym[0].upper()
    sym2 += sym[1:]
    return sym2


def normalize_element_name(name):
    name = name.lower()
    name2 = name[0].upper()
    name2 += name[1:]
    return name2


def amint_to_char(am):
    if am < 0:
        raise RuntimeError('Angular momentum must be a positive integer')
    if am >= len(amchar_map):
        raise RuntimeError('Angular momentum must be less than {}'.format(len(amchar_map)))

    return amchar_map[am]


def amchar_to_int(amchar):
    amchar_lower = amchar.lower()

    # This may be combined angular momentum (sp, spd)
    amint = []

    for c in amchar_lower:
        if c not in amchar_map:
            raise RuntimeError('Angular momentum character {} is not valid'.format(c))

        amint.append(amchar_map.index(c))

    return amint
