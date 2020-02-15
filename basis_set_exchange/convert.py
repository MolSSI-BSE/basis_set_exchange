'''
Functions for basis set conversion
'''

from .readers import read_formatted_basis_file, read_formatted_basis_str
from .writers import write_formatted_basis_file, write_formatted_basis_str


def convert_formatted_basis_str(basis_in, in_fmt, out_fmt):
    '''Convert a formatted basis set to another format

    Parameters
    ----------
    basis_in : str
        String representing the formatted input basis set input
    in_fmt : str
        The format of the basis set stored in basis_in
    out_fmt : str
        The desired output format

    Returns
    -------
    str
        The basis set as a str with the new format
    '''

    basis_dict = read_formatted_basis_str(basis_in, in_fmt, validate=True, as_component=False)
    return write_formatted_basis_str(basis_dict, out_fmt)


def convert_formatted_basis_file(file_path_in, file_path_out, in_fmt=None, out_fmt=None, encoding='utf-8-sig'):
    '''Convert a formatted basis set file to another format

    Parameters
    ----------
    file_path_in : str
        Path to the file to be read
    file_path_out : str
        Path to the file to be written.
    in_fmt : str
        The format of the basis to be read. If None, it is detected from the file name
    out_fmt : str
        The format of the basis to be written. If None, it is detected from the file name
    encoding : str
        The encoding of the input file

    Returns
    -------
    str
        The basis set as a str with the new format
    '''

    basis_dict = read_formatted_basis_file(file_path_in,
                                           basis_fmt=in_fmt,
                                           encoding=encoding,
                                           validate=True,
                                           as_component=False)

    write_formatted_basis_file(basis_dict, file_path_out, basis_fmt=out_fmt)
