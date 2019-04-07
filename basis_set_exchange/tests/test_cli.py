'''
Testing of the BSE CLI interface
'''

import os
import subprocess
import pytest

from .common_testvars import fake_data_dir


def _test_cli_cmd(cmd):
    # NOTE: We do not enforce any encoding here. What is returned will be a byte string
    # For our purposes here, that is ok. We don't know what encoding is going to be
    # used (ie, windows)
    cmd = cmd.split(' ')
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT)


bse_cmds = [
    '-V', '-h', '--help', 'list-formats', 'list-ref-formats', 'list-roles', 'get-data-dir', 'list-basis-sets',
    'list-basis-sets -s sto', 'list-basis-sets -f duNNing', 'list-basis-sets -r orbiTAL -f ahlrichs', 'list-families',
    'lookup-by-role def2-tzVp riFit', 'get-basis sto-3g nwchem', 'get-basis cc-pvtz psi4 --elements=1-10',
    'get-basis def2-tzvp turbomole --elements=H-9,11-Ar,cO', 'get-basis cc-pvqz gaussian94 --version=1 --noheader',
    'get-basis 6-31g nwchem --unc-gen --unc-spdf --unc-seg', 'get-basis 6-31g nwchem --opt-gen',
    'get-basis 6-31g nwchem --make-gen', 'get-refs 6-31g txt', 'get-refs sto-3g bib --elements=6-Ne',
    'get-refs ano-rcc txt --elements sc', 'get-info aug-cc-pv5z', 'get-info def2-tzvp', 'get-notes sto-3g',
    'get-family crenbl', 'get-versions cc-pvqz', 'get-family-notes sto'
]

fakebse_cmds = [
    'list-basis-sets', 'list-basis-sets -s fake', 'list-basis-sets -f bppfake', 'list-families',
    'lookup-by-role bppFAKEbasis jkFit', 'get-basis bppfakebasis nwchem', 'get-refs bppfakebasis txt',
    'get-info bppfakebasis', 'get-family bppfakebasis', 'get-versions bppfakebasis', 'get-family-notes bppfake'
]


@pytest.mark.parametrize('bse_cmd', bse_cmds)
def test_cli(bse_cmd):
    _test_cli_cmd('bse ' + bse_cmd)


@pytest.mark.parametrize('bse_cmd', fakebse_cmds)
def test_cli_datadir(bse_cmd):
    output = _test_cli_cmd('bse -d ' + fake_data_dir + ' ' + bse_cmd)
    assert b'bppfake' in output


def test_cli_createbundle_datadir(tmp_path):
    tmp_path = str(tmp_path)  # Needed for python 3.5
    bfile_path = os.path.join(tmp_path, 'test_bundle_datadir.tar.bz2')
    output = _test_cli_cmd('bse -d ' + fake_data_dir + ' create-bundle gaussian94 bib ' + bfile_path)
    assert os.path.isfile(bfile_path)
    assert output.startswith(b'Created ')
