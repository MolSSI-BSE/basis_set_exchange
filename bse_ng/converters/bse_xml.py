import os
import xml.etree.ElementTree as ET

from bse_ng import lut, read_json_basis_file, write_json_basis_file

ns = { 'default': 'http://purl.oclc.org/NET/EMSL/BSE',
       'cml': 'http://www.xml-cml.org/schema/cml2/core', 
       'dc': 'http://purl.org/dc/elements/1.1/',
       'dct': 'http://purl.org/dc/terms/',
       'xlink': 'http://www.w3.org/1999/xlink'
}


def create_json_path(xmlpath, filetype=None):
    bsdir = os.path.dirname(xmlpath)
    filebase = os.path.basename(xmlpath)
    filename = os.path.splitext(filebase)[0]

    if filetype:
        outfile = "{}.{}.json".format(filename, filetype)
    else:
        outfile = "{}.json".format(filename)
    outfile = os.path.join(bsdir, outfile)
    return outfile


def get_single_node(node, tag):
    a = node.findall(tag, ns)
    if not a:
        raise RuntimeError('tag {} not found'.format(tag))
    if len(a) != 1:
        raise RuntimeError('Multiple tags {} found'.format(tag))
    return a[0]


def get_single_text(node, tag, default=None):
    a = node.findall(tag, ns)
    if not a:
        if default:
            return default
        else:
            raise RuntimeError('tag {} not found'.format(tag))

    if len(a) != 1:
        raise RuntimeError('Multiple tags {} found'.format(tag))

    if len(a[0].attrib) > 0:
        raise RuntimeError('Tag {} has attributes'.format(tag))

    return a[0].text


def get_links(node, tag):
    all_nodes = node.findall(tag, ns)
    if not all_nodes:
        raise RuntimeError('tag {} not found'.format(tag))
    ret = []
    for a in all_nodes:
        ret.append(a.attrib['{{{}}}href'.format(ns['xlink'])])

    return ret


def get_single_link(node, tag):
    return get_links(node, tag)[0] 


def text_to_cont(txt):
    coefficients = []
    exponents = []

    txt = txt.strip()
    for l in txt.splitlines():
        l = l.split()
        exponents.append(l[0])
        coefficients.append(l[1:])


    for i in coefficients:
        if len(i) != len(coefficients[0]):
            print(coefficients)
            raise RuntimeError('Different number of general contractions')


    coefficients = list(map(list, zip(*coefficients)))
    return (exponents,coefficients)
    

def get_ref_file(reffile):
    root = ET.parse(reffile).getroot()
    return get_single_text(root, 'default:notes')


def determine_role_region(r):
    orb_roles = ['diffuse', 'polarization', 'rydberg', 'tight', 'valence']
    if r in orb_roles:
        return ('orbital',r)
    else:
        return (r, r)


def read_basis_xml(xmlfile):
    # Path to the directory
    bsdir = os.path.dirname(xmlfile)

    # Parse the XML
    bsdict = {}
    root = ET.parse(xmlfile).getroot()

    # Read the metadata
    bsdict['basisSetName'] = get_single_text(root, 'dc:title')
    bsdict['basisSetDescription'] = get_single_text(root, 'dct:abstract', bsdict['basisSetName'])
    bstype = get_single_text(root, 'default:basisSetType')
    role, region = determine_role_region(bstype)
    bsdict['basisSetRole'] = role
    bsdict['basisSetRegion'] = region

    harmonicType = get_single_text(root, 'default:harmonicType')
    functionType = 'gto'

    # Path to the reference file
    ref_file = get_single_link(root, 'default:referencesLink')
    ref_file = os.path.join(bsdir, ref_file)
    ref_data = get_ref_file(ref_file)

    # These will be stored separately
    bs_desc = get_single_text(root, 'dc:description')
    bs_ref = get_ref_file(ref_file)

    # Read in contraction data
    bsdict['basisSetElements'] = {}
    all_contractions = root.findall('default:contractions', ns)

    for cs in all_contractions:
        # Read in element and convert to Z number
        el = cs.attrib['elementType']
        el = lut.element_data_from_sym(el)[0]

        elementData = { 'elementReference': 'TODO' }
        shells = []

        for c in cs.findall('default:contraction', ns):
            # read in angular momentum, convert to integers
            am = c.attrib['shell']
            am = lut.amchar_to_int(am)

            mat = get_single_node(c, 'cml:matrix')
            nprim = int(mat.attrib['rows'])
            ngen = int(mat.attrib['columns']) - 1  # Columns includes exponents
            exponents,coefficients = text_to_cont(mat.text) 

            shell = { 'shellFunctionType': functionType,
                      'shellHarmonicType': harmonicType,
                      'shellAngularMomentum': am,
                      'shellExponents' : exponents,
                      'shellCoefficients' : coefficients
                     }
            shells.append(shell)

        elementData['elementElectronShells'] = shells
        bsdict['basisSetElements'][el] = elementData

    return bsdict



def read_basis_xml_agg(xmlfile):
    # Path to the directory
    bsdir = os.path.dirname(xmlfile)

    # Parse the XML
    root = ET.parse(xmlfile).getroot()

    # Read the metadata
    name = get_single_text(root, 'dc:title')
    desc = get_single_text(root, 'dct:abstract', name)

    bstype = get_single_text(root, 'default:basisSetType')
    role, region = determine_role_region(bstype)

    # These will be stored separately
    bs_desc = get_single_text(root, 'dc:description')

    # Read in the components
    # These are the paths to the xml files
    all_paths = []
    all_paths.append(get_single_link(root, 'default:primaryBasisSetLink'))
    all_paths.extend(get_links(root, 'default:basisSetLink'))

    # Convert to full paths
    all_xml_paths = [ os.path.join(bsdir, p) for p in all_paths ]

    # Convert these paths to json files instead
    # and read in the basis set data
    all_json_paths = [ create_json_path(p) for p in all_xml_paths ]
    all_json_data = [ read_json_basis_file(p) for p in all_json_paths ]

    # Find the intersection for all the elements of the basis sets
    all_elements = []
    for x in all_json_data:
        all_elements.append(list(x['basisSetElements'].keys()))

    element_intersection = set(all_elements[0]).intersection(*all_elements[1:])
    element_union = set(all_elements[0]).union(*all_elements[1:])
    all_json_files = [ os.path.basename(p) for p in all_json_paths ]

    # "Atom" basis dictionary
    elements = { k: { 'elementComponents': all_json_files } for k in element_intersection }

    atom_dict = { 'basisSetName': name,
                  'basisSetDescription' : desc,
                  'basisSetElements': elements
                 }



    # Periodic table basis dictionary
    # For each element, include only the components where that atom is defined
    elements = { }
    for e in element_union:
        v = []
        for i,p in enumerate(all_json_files):
            bs = all_json_data[i]
            if e in bs['basisSetElements'].keys():
                v.append(p)
        elements[e] = { 'elementComponents': v }
    
    table_dict = { 'basisSetName': name,
                   'basisSetDescription' : desc,
                   'basisSetElements': elements
                 }
        
    return (atom_dict, table_dict)



def convert_xml(xmlfile):
    bsdict = read_basis_xml(xmlfile)
    outfile = create_json_path(xmlfile)
    print("New basis file: ", outfile)
    write_json_basis_file(outfile, bsdict)


def convert_xml_agg(xmlfile):
    atom_dict, table_dict = read_basis_xml_agg(xmlfile)

    atom_basis_path = create_json_path(xmlfile, 'atom')
    table_basis_path = create_json_path(xmlfile, 'table')

    print("Atom basis: ", atom_basis_path)
    print("Table basis: ", table_basis_path)
    
    write_json_basis_file(atom_basis_path, atom_dict)
    write_json_basis_file(table_basis_path, table_dict)


def create_xml_agg(xmlfile):
    # Create from a simple (non-composed) basis
    atom_basis_path = create_json_path(xmlfile, 'atom')
    table_basis_path = create_json_path(xmlfile, 'table')
    json_file = os.path.basename(create_json_path(xmlfile))

    bs = read_basis_xml(xmlfile)

    elementlist = list(bs['basisSetElements'].keys())

    elements = { k: { 'elementComponents': [json_file] } for k in elementlist }

    atom_dict = { 'basisSetName': bs['basisSetName'],
                  'basisSetDescription': bs['basisSetDescription'],
                  'basisSetElements': elements
                 }

    table_dict = { 'basisSetName': bs['basisSetName'],
                   'basisSetDescription': bs['basisSetDescription'],
                   'basisSetElements': elements
                  }

    write_json_basis_file(atom_basis_path, atom_dict)
    write_json_basis_file(table_basis_path, table_dict)
