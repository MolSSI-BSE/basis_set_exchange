# Copyright (c) 2017-2022 The Molecular Sciences Software Institute, Virginia Tech
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

'''
Testing of the BSE CLI interface
'''

import os
import sys
import subprocess
import pytest

from .common_testvars import cli_dir, fake_data_dir


def _test_cli_cmd(cmd):
    # NOTE: We do not enforce any encoding here. What is returned will be a byte string
    # For our purposes here, that is ok. We don't know what encoding is going to be
    # used (ie, windows)
    cmd = '{} {} '.format(sys.executable, os.path.join(cli_dir, 'bse_cli.py')) + cmd
    cmd = cmd.split(' ')
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT)


bse_cmds = [
    '-V', '-h', '--help', 'list-formats', 'list-reader-formats', 'list-ref-formats', 'list-roles', 'get-data-dir',
    'list-basis-sets', 'list-basis-sets -s sto', 'list-basis-sets -f duNNing',
    'list-basis-sets -r orbiTAL -f ahlrichs', 'list-basis-sets -e cn-OG', 'list-families',
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
    _test_cli_cmd(bse_cmd)


@pytest.mark.parametrize('bse_cmd', fakebse_cmds)
def test_cli_datadir(bse_cmd):
    output = _test_cli_cmd('-d ' + fake_data_dir + ' ' + bse_cmd)
    assert b'bppfake' in output


def test_cli_createbundle_datadir(tmp_path):
    tmp_path = str(tmp_path)  # Needed for python 3.5
    bfile_path = os.path.join(tmp_path, 'test_bundle_datadir.tar.bz2')
    output = _test_cli_cmd('-d ' + fake_data_dir + ' create-bundle gaussian94 bib ' + bfile_path)
    assert os.path.isfile(bfile_path)
    assert output.startswith(b'Created ')
