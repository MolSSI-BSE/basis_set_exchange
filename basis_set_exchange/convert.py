'''
Functions for basis set conversion
'''

from .readers import read_formatted_basis_file, read_formatted_basis_str
from .writers import write_formatted_basis_file, write_formatted_basis_str


def convert_formatted_basis_str(basis_in, fmt_in, fmt_out):
    '''Convert a formatted basis set to another format

    Parameters
    ----------
    basis_in : str
        String representing the formatted input basis set input
    fmt_in : str
        The format of the basis set stored in basis_in
    fmt_out : str
        The desired output format

    Returns
    -------
    str
        The basis set as a str with the new format
    '''

    basis_dict = read_formatted_basis_str(basis_in, fmt_in, validate=True, as_component=False)
    return write_formatted_basis_str(basis_dict, fmt_out)


def convert_formatted_basis_file(file_path_in, file_path_out, fmt_in=None, fmt_out=None, encoding='utf-8-sig'):
    '''Convert a formatted basis set file to another format

    Parameters
    ----------
    file_path_in : str
        Path to the file to be read
    file_path_out : str
        Path to the file to be written.
    fmt_in : str
        The format of the basis to be read. If None, it is detected from the file name
    fmt_out : str
        The format of the basis to be written. If None, it is detected from the file name
    encoding : str
        The encoding of the input file

    Returns
    -------
    str
        The basis set as a str with the new format
    '''

    basis_dict = read_formatted_basis_file(file_path_in,
                                           basis_fmt=fmt_in,
                                           encoding=encoding,
                                           validate=True,
                                           as_component=False)

    write_formatted_basis_file(basis_dict, file_path_out, basis_fmt=fmt_out)
