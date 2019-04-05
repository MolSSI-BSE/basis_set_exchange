'''
Functions for creating archives of all basis sets
'''

import os
import copy
import zipfile
import tarfile
import io
import datetime
from . import api, converters, refconverters, misc

_readme_str = '''Basis set exchange: Basis set bundle
==========================================

Basis Set Exchange: {bsever}
Created {timestamp}
Format: {fmt}
Reference format: {reffmt}

This directory contains all the basis sets in the library
in {fmt} format. 

Filenames of the basis sets are in the format
{{name}}.{{version}}.{{extension}} where the version represents
the version of the basis set.

Filenames of the references are similar, except they
contain .ref before the final extension.

Basis set notes have a .notes extension, and family
notes have a .family_notes extension.

-------------------------------------------------
https://wwww.basissetexchange.org
https://github.com/MolSSI-BSE/basis_set_exchange
bse@molssi.org
-------------------------------------------------
'''


def _create_readme(fmt, reffmt):
    '''
    Creates the readme file for the bundle

    Returns a str representing the readme file
    '''

    now = datetime.datetime.utcnow()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S UTC')

    # yapf: disable
    outstr = _readme_str.format(timestamp=timestamp,
                                bsever=api.version(),
                                fmt=fmt, reffmt=reffmt)
    # yapf: enable

    return outstr


def _basis_data_iter(fmt, reffmt, data_dir):
    '''Iterate over all basis set names, and return a tuple of
       (name, data) where data is the basis set in the given format
    '''
    md = api.get_metadata(data_dir)
    for bs, bs_md in md.items():
        versions = bs_md['versions'].keys()

        data = {}
        for v in versions:
            bsdata = api.get_basis(bs, fmt=fmt, version=v, data_dir=data_dir)
            refdata = api.get_references(bs, fmt=reffmt, version=v, data_dir=data_dir)
            data[v] = (bsdata, refdata)

        notes = api.get_basis_notes(bs, data_dir)
        yield (bs, data, notes)


def _add_to_tbz(tfile, filename, data_str):
    '''
    Adds string data to a tarfile
    '''

    # Create a bytesio object for adding to a tarfile
    # https://stackoverflow.com/a/52724508
    encoded_data = data_str.encode('utf-8')
    ti = tarfile.TarInfo(name=filename)
    ti.size = len(encoded_data)
    tfile.addfile(tarinfo=ti, fileobj=io.BytesIO(encoded_data))


def _add_to_zip(zfile, filename, data_str):
    '''
    Adds string data to a zipfile
    '''
    zfile.writestr(filename, data_str)


def _bundle_tbz(outfile, fmt, reffmt, data_dir):
    with tarfile.open(outfile, 'w:bz2') as tf:
        _bundle_generic(tf, _add_to_tbz, fmt, reffmt, data_dir)


def _bundle_zip(outfile, fmt, reffmt, data_dir):
    with zipfile.ZipFile(outfile, 'w') as zf:
        _bundle_generic(zf, _add_to_zip, fmt, reffmt, data_dir)


def _bundle_generic(bfile, addhelper, fmt, reffmt, data_dir):
    '''
    Loop over all basis sets and add data to an archive

    Parameters
    ----------
    bfile : object
        An object that gets passed through to the addhelper function
    addhelper : function
        A function that takes bfile and adds data to the bfile
    fmt : str
        Format of the basis set to create
    reffmt : str
        Format to use for the references
    data_dir : str
        Data directory with all the basis set information.

    Returns
    -------
    None
    '''

    ext = converters.get_format_extension(fmt)
    refext = refconverters.get_format_extension(reffmt)
    subdir = 'basis_set_bundle-' + fmt + '-' + reffmt

    readme_path = os.path.join(subdir, 'README.txt')
    addhelper(bfile, readme_path, _create_readme(fmt, reffmt))

    for name, data, notes in _basis_data_iter(fmt, reffmt, data_dir):
        for ver, verdata in data.items():
            filename = misc.basis_name_to_filename(name)
            basis_filepath = os.path.join(subdir, '{}.{}{}'.format(filename, ver, ext))
            ref_filename = os.path.join(subdir, '{}.{}.ref{}'.format(filename, ver, refext))

            bsdata, refdata = verdata
            addhelper(bfile, basis_filepath, bsdata)
            addhelper(bfile, ref_filename, refdata)

        if len(notes) > 0:
            notes_filename = os.path.join(subdir, filename + '.notes')
            addhelper(bfile, notes_filename, notes)

    for fam in api.get_families(data_dir):
        fam_notes = api.get_family_notes(fam, data_dir)

        if len(fam_notes) > 0:
            fam_notes_filename = os.path.join(subdir, fam + '.family_notes')
            addhelper(bfile, fam_notes_filename, fam_notes)


_bundle_types = {
    'zip': {
        'display': 'ZIP file',
        'handler': _bundle_zip,
        'extension': '.zip'
    },
    'tbz': {
        'display': 'Tar + bzip2',
        'handler': _bundle_tbz,
        'extension': '.tar.bz2'
    }
}


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

    Returns
    -------
    None
    '''

    if archive_type is None:
        outfile_lower = outfile.lower()

        for k, v in _bundle_types.items():
            if outfile_lower.endswith(v['extension']):
                archive_type = k
                break
        else:
            raise RuntimeError("Cannot autodetect archive type from file name: {}".format(os.path.basename(outfile)))

    else:
        archive_type = archive_type.lower()
        if not archive_type in _bundle_types:
            raise RuntimeError("Archive type '{}' is not valid.")

    _bundle_types[archive_type]['handler'](outfile, fmt, reffmt, data_dir)


def get_archive_types():
    '''
    Return information related to the types of archives available
    '''
    ret = copy.deepcopy(_bundle_types)
    for k, v in ret.items():
        v.pop('handler')
    return ret
