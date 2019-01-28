'''
Testing of the BSE CLI interface
'''

import os
import subprocess
import pytest

# Find the dir with the fake data
_my_dir = os.path.dirname(os.path.abspath(__file__))
_fake_data_dir = os.path.join(_my_dir, 'fakedata')


def _test_cli_cmd(cmd):
    return subprocess.check_output(cmd, shell=True, cwd='/tmp', universal_newlines=True, stderr=subprocess.STDOUT)


bse_cmds = ['-V',
            '-h',
            '--help',
            'list-formats',
            'list-ref-formats',
            'list-roles',
            'list-basis-sets',
            'list-basis-sets -s sto',
            'list-basis-sets -f duNNing',
            'list-basis-sets -r orbiTAL -f ahlrichs',
            'list-families',
            'lookup-by-role def2-tzVp riFit',
            'get-basis sto-3g nwchem',
            'get-basis cc-pvtz psi4 --elements=1-10',
            'get-basis def2-tzvp turbomole --elements=H-9,11-Ar,cO',
            'get-basis cc-pvqz gaussian94 --version=1 --noheader',
            'get-basis 6-31g nwchem --unc-gen --unc-spdf --unc-seg',
            'get-basis 6-31g nwchem --opt-gen',
            'get-basis 6-31g nwchem --make-gen',
            'get-refs 6-31g txt',
            'get-refs sto-3g bib --elements=6-Ne',
            'get-info aug-cc-pv5z',
            'get-info def2-tzvp',
            'get-notes sto-3g',
            'get-family crenbl',
            'get-versions cc-pvqz',
            'get-family-notes sto'          
]


fakebse_cmds = ['list-basis-sets',
                'list-basis-sets -s fake',
                'list-basis-sets -f bppfake',
                'list-families',
                'lookup-by-role bppFAKEbasis jkFit',
                'get-basis bppfakebasis nwchem',
                'get-refs bppfakebasis txt',
                'get-info bppfakebasis',
                'get-family bppfakebasis',
                'get-versions bppfakebasis',
                'get-family-notes bppfake'          
]

@pytest.mark.parametrize('bse_cmd', bse_cmds)
def test_cli(bse_cmd):
    _test_cli_cmd('bse ' + bse_cmd)


@pytest.mark.parametrize('bse_cmd', fakebse_cmds)
def test_cli_datadir(bse_cmd):
    output = _test_cli_cmd('bse -d ' + _fake_data_dir + ' ' + bse_cmd)
    assert 'bppfake' in output
