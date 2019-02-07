'''
Functions for creating archives of all basis sets
'''

import os
import zipfile
import tarfile
import bz2
import io
from . import api, converters, refconverters


def _basis_data_iter(fmt, reffmt, data_dir):
    '''Iterate over all basis set names, and return a tuple of
       (name, data) where data is the basis set in the given format
    '''
    names = iter(api.get_all_basis_names(data_dir=data_dir))
    for n in names:
        data = api.get_basis(n, fmt=fmt, data_dir=data_dir)
        refdata = api.get_references(n, fmt=reffmt, data_dir=data_dir)
        notes = api.get_basis_notes(n, data_dir)
        yield (n, data, refdata, notes)


def _bundle_zip(outfile, fmt, reffmt, data_dir):
    ext = converters.get_format_extension(fmt)
    refext = refconverters.get_format_extension(reffmt)

    with zipfile.ZipFile(outfile, 'w') as zf:
        for name, data, refdata, notes in _basis_data_iter(fmt, reffmt, data_dir):
            basis_filename = name + ext
            ref_filename = name + '.ref' + refext
            notes_filename = name + '.notes'
            zf.writestr(basis_filename, data)
            zf.writestr(ref_filename, refdata)

            if len(notes) > 0:
                zf.writestr(notes_filename, notes)

        for fam in api.get_families(data_dir):
            fam_notes = api.get_family_notes(fam, data_dir)

            if len(fam_notes) > 0:
                fam_notes_filename = 'family_' + fam + '.notes'
                zf.writestr(fam_notes_filename, fam_notes)


def _add_tbz_file(tfile, filename, data_str):
    '''
    Adds string data to a tarfile
    '''

    # Create a bytesio object for adding to a tarfile
    # https://stackoverflow.com/a/52724508
    encoded_data = data_str.encode('utf-8')
    data_len = len(encoded_data)
    ti = tarfile.TarInfo(name=filename)
    ti.size = len(encoded_data)
    tfile.addfile(tarinfo=ti, fileobj=io.BytesIO(encoded_data))


def _bundle_tbz(outfile, fmt, reffmt, data_dir):
    ext = converters.get_format_extension(fmt)
    refext = refconverters.get_format_extension(reffmt)

    with tarfile.open(outfile, 'w:bz2') as tf:
        for name, data, refdata, notes in _basis_data_iter(fmt, reffmt, data_dir):
            basis_filename = name + ext
            ref_filename = name + '.ref' + refext

            _add_tbz_file(tf, basis_filename, data)
            _add_tbz_file(tf, ref_filename, refdata)

            if len(notes) > 0:
                notes_filename = name + '.notes'
                _add_tbz_file(tf, notes_filename, notes)

        for fam in api.get_families(data_dir):
            fam_notes = api.get_family_notes(fam, data_dir)

            if len(fam_notes) > 0:
                fam_notes_filename = 'family_' + fam + '.notes'
                _add_tbz_file(tf, fam_notes_filename, fam_notes)


_archive_handlers = {
    'zip': _bundle_zip,
    'tbz': _bundle_tbz,
}

_valid_archive_types = _archive_handlers.keys()


def create_bundle(outfile, fmt, reffmt, archive_type=None, data_dir=None):
    '''
    Create a single archive file containing all basis
    sets in a given format

    Parameters
    ----------
    outfile : str
        Path to the file to create. Existing files will be overwritten
    fmt : str
        Format of the basis set to archive (nwchem, turbomole, ...)
    reffmt : str
        Format of the basis set references to archive (nwchem, turbomole, ...)
    archive_type : str
        Type of archive to create. Can be 'zip' or 'tbz'. Default is
        None, which will autodetect based on the outfile name
    data_dir : str
        Data directory with all the basis set information. By default,
        it is in the 'data' subdirectory of this project.
    '''

    if archive_type is None:
        outfile_lower = outfile.lower()
        if outfile_lower.endswith('.zip'):
            archive_type = 'zip'
        elif outfile_lower.endswith('.tar.bz2'):
            archive_type = 'tbz'
        elif outfile_lower.endswith('.tbz'):
            archive_type = 'tbz'
        else:
            raise RuntimeError("Cannot autodetect archive type from file name: {}".format(os.path.basename(outfile)))

    else:
        archive_type = archive_type.lower()
        if not archive_type in _valid_archive_types:
            raise RuntimeError("Archive type '{}' is not valid. Must be one of: {}".format(
                archive_type, ','.join(_valid_archive_types)))

    basis_names = api.get_all_basis_names()
    _archive_handlers[archive_type](outfile, fmt, reffmt, data_dir)
