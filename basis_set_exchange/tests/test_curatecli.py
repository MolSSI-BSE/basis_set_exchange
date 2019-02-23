'''
Testing of the BSE Curation CLI interface
'''

import os
import subprocess
import pytest

from .common_testvars import fake_data_dir, data_dir

def _test_curatecli_cmd(cmd):
    return subprocess.check_output(cmd, shell=True, cwd='/tmp', universal_newlines=True, stderr=subprocess.STDOUT)

test_files1 = [ '6-31G.0.table.json', 'ahlrichs/def2-ECP.1.element.json', 'dunning/cc-pV5+dZ-add_prascher2011a.1.json']
test_files1 = [os.path.join(data_dir, x) for x in test_files1]

bsecurate_cmds = [
    '-V', '-h', '--help',
    'elements-in-files ' + ' '.join(test_files1),
]

fakebsecurate_cmds = []

@pytest.mark.parametrize('bsecurate_cmd', bsecurate_cmds)
def test_curatecli(bsecurate_cmd):
    _test_curatecli_cmd('bsecurate ' + bsecurate_cmd)

@pytest.mark.parametrize('bsecurate_cmd', fakebsecurate_cmds)
def test_curatecli_datadir(bsecurate_cmd):
    output = _test_curatecli_cmd('bsecurate -d ' + fake_data_dir + ' ' + bsecurate_cmd)
    assert 'bppfake' in output
