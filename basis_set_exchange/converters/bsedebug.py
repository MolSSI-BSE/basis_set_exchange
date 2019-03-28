'''
Conversion of basis sets to the BSE debug/dump format
'''

from ..printing import element_data_str


def write_bsedebug(basis):
    '''Converts a basis set to BSE Debug format
    '''

    s = ''

    for el, eldata in basis['elements'].items():
        s += element_data_str(el, eldata)
    return s
