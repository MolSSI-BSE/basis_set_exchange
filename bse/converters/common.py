import os
from .. import lut

def determine_leftpad(column, desired_place):
    # Find the number of digits before the decimal
    ndigits_left = [ x.index('.') for x in column ]

    # Maximum number of digits
    # ndigits_left_max = max(ndigits_left)

    # find the padding per entry, filtering negative numbers
    padding = [ max((desired_place - 1) - x, 0) for x in ndigits_left ]

    return padding


