#!/usr/bin/env python3

import os
import tempfile
from .. import api, fileio
from ..misc import compact_elements

try:
    import graphviz
    graphviz_avail = True
except ImportError:
    graphviz_avail = False


def _make_graph(bsname, version=None, data_dir=None):
    '''
    Create a DOT graph file of the files included in a basis set
    '''

    if not graphviz_avail:
        raise RuntimeError("graphviz package is not installed")

    data_dir = api.fix_data_dir(data_dir)

    md = api._get_basis_metadata(bsname, data_dir)

    if version is None:
        version = md['latest_version']
    else:
        version = str(version)

    if not version in md['versions']:
        raise RuntimeError("Version {} of {} doesn't exist".format(version, bsname))

    gr = graphviz.Digraph(comment='Basis Set Graph: ' + bsname)

    # Read the table file
    table_path = os.path.join(data_dir, md['versions'][version]['file_relpath'])
    table_data = fileio.read_json_basis(table_path)

    table_edges = {}
    for el, entry in table_data['elements'].items():
        if entry not in table_edges:
            table_edges[entry] = []
        table_edges[entry].append(el)

    for k, v in table_edges.items():
        gr.edge(bsname, k, label=compact_elements(v))

    # Element file
    for elfile in table_edges.keys():
        element_path = os.path.join(data_dir, elfile)
        element_data = fileio.read_json_basis(element_path)

        element_edges = {}

        for el, components in element_data['elements'].items():
            components = components['components']
            components_str = '\n'.join(components)

            # skip if this element for the table basis doesn't come from this file
            if el not in table_data['elements']:
                continue
            if table_data['elements'][el] != elfile:
                continue

            if components_str not in element_edges:
                element_edges[components_str] = []
            element_edges[components_str].append(el)

        for k, v in element_edges.items():
            if len(v):
                gr.edge(elfile, k, label=compact_elements(v))

    return gr


def view_graph(bsname, version=None, data_dir=None):
    gr = _make_graph(bsname, version, data_dir)

    outdir = tempfile.mkdtemp()
    gr.render(directory=outdir, format='png', view=True)


def make_graph_file(bsname, outfile, render=False, version=None, data_dir=None):
    gr = _make_graph(bsname, version, data_dir)

    if render:
        gr.render(outfile, format='png', view=False)
    else:
        gr.save(outfile)
