'''
Helper functions for writing out basis set in various formats
'''


def determine_leftpad(column, desired_place):
    '''Find how many spaces to put before a column of numbers
       so that all the decimal points line up

    This function takes a column of decimal numbers, and returns a
    vector containing the number of spaces to place before each number
    so that (when possible) the decimal points line up.


    Parameters
    ----------
    column : list
        Numbers that will be printed as a column
    desired_place : int
        Number of the character column to put the decimal place
    '''

    # Find the number of digits before the decimal
    ndigits_left = [x.index('.') for x in column]

    # Maximum number of digits
    # ndigits_left_max = max(ndigits_left)

    # find the padding per entry, filtering negative numbers
    padding = [max((desired_place - 1) - x, 0) for x in ndigits_left]

    return padding
