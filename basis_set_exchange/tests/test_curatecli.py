'''
Testing of the BSE Curation CLI interface
'''

import os
import subprocess
import pytest
import shutil

from basis_set_exchange import fileio, curate
from .common_testvars import fake_data_dir, data_dir, test_data_dir

def _test_curatecli_cmd(cmd):
    return subprocess.check_output(cmd, shell=True, cwd='/tmp', universal_newlines=True, stderr=subprocess.STDOUT)

test_files1 = [ '6-31G.0.table.json', 'ahlrichs/def2-ECP.1.element.json', 'dunning/cc-pV5+dZ-add_prascher2011a.1.json']
test_files1 = [os.path.join(data_dir, x) for x in test_files1]


bsecurate_cmds = [
    '-V', '-h', '--help',
    'elements-in-files ' + ' '.join(test_files1)
]

fakebsecurate_cmds = []

@pytest.mark.parametrize('bsecurate_cmd', bsecurate_cmds)
def test_curatecli(bsecurate_cmd):
    _test_curatecli_cmd('bsecurate ' + bsecurate_cmd)

@pytest.mark.parametrize('bsecurate_cmd', fakebsecurate_cmds)
def test_curatecli_datadir(bsecurate_cmd):
    output = _test_curatecli_cmd('bsecurate -d ' + fake_data_dir + ' ' + bsecurate_cmd)
    assert 'bppfake' in output


def test_curatecli_makediff(tmp_path):
    tmp_path = str(tmp_path)  # Needed for python 3.5

    filename1 = '6-31G**-full.json.bz2' 
    filename2 = '6-31G-full.json.bz2' 

    file1 = os.path.join(test_data_dir, filename1)
    file2 = os.path.join(test_data_dir, filename2)

    tmpfile1 = os.path.join(tmp_path, filename1)
    tmpfile2 = os.path.join(tmp_path, filename2)

    shutil.copyfile(file1, tmpfile1)
    shutil.copyfile(file2, tmpfile2)

    _test_curatecli_cmd('bsecurate make-diff -l {} -r {}'.format(tmpfile1, tmpfile2))
    _test_curatecli_cmd('bsecurate make-diff -l {} -r {}'.format(tmpfile2, tmpfile1))

    diff1 = fileio.read_json_basis(tmpfile1 + '.diff')
    diff2 = fileio.read_json_basis(tmpfile2 + '.diff')

    assert len(diff1['basis_set_elements']) == 36
    assert len(diff2['basis_set_elements']) == 0

    reffilename = '6-31G**-valence.json.bz2' 
    reffile = os.path.join(test_data_dir, reffilename)
    refdata = fileio.read_json_basis(reffile)

    assert curate.compare_basis(diff1, refdata, rel_tol=0.0)
