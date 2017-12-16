
def create_reference_key(existing_references, author, year):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    test_key_base = author.lower() + ':' + str(year)

    for letter in alphabet:
        test_key = test_key_base + letter
        if not test_key in existing_references:
            return test_key
    else:
        raise RuntimeError("Unable to find suitable key")


def find_ref_by_doi(references, doi):
    test_doi = doi.strip().lower()
    for k,v in references.items():
        if 'DOI' in v and v['DOI'].strip().lower() == test_doi:
            return k
    return None
