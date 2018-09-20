'''
Read a basis set file in a given format
'''

def read_formatted_basis(filepath, file_type):
    type_readers = {'turbomole': read_turbomole,
                    'gaussian94': read_g94}

    file_type = file_type.lower()
    if file_type not in type_readers:
        raise RuntimeError("Unknown file type to read '{}'".format(file_type))

    data = type_readers[file_type](src_filepath)
    return _fix_uncontracted(data)


