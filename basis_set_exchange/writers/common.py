'''
Helper functions for writing out basis set in various formats
'''


def find_range(coeffs):
    '''
    Find the range in a list of coefficients where the coefficient is nonzero
    '''

    coeffs = [float(x) != 0 for x in coeffs]
    first = coeffs.index(True)
    coeffs.reverse()
    last = len(coeffs) - coeffs.index(True) - 1
    return first, last
