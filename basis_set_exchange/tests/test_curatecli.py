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
Testing of the BSE Curation CLI interface
'''

import os
import sys
import subprocess
import pytest
import shutil

from basis_set_exchange import fileio, curate
from .common_testvars import cli_dir, fake_data_dir, data_dir, curate_test_data_dir


def _test_curatecli_cmd(cmd):
    # NOTE: We do not enforce any encoding here. What is returned will be a byte string
    # For our purposes here, that is ok. We don't know what encoding is going to be
    # used (ie, windows)

    # Python to run
    cmd = '{} {} '.format(sys.executable, os.path.join(cli_dir, 'bsecurate_cli.py')) + cmd
    cmd = cmd.split(' ')
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT)


test_files1 = ['6-31G.0.table.json', 'ahlrichs/def2-ECP.1.element.json', 'dunning/cc-pV5+dZ-add.1.json']
test_files1 = [os.path.join(data_dir, x) for x in test_files1]

test_files2 = ['dunning/cc-pV5+dZ-add.1.json', 'dunning/cc-pVDZ.1.json']
test_files2 = [os.path.join(data_dir, x) for x in test_files2]

bsecurate_cmds = [
    '-V', '-h', '--help', 'elements-in-files ' + ' '.join(test_files1), 'component-file-refs ' + ' '.join(test_files2)
]

fakebsecurate_cmds = ['-V', 'compare-basis-sets bppfakebasis bppfakebasis']


@pytest.mark.parametrize('bsecurate_cmd', bsecurate_cmds)
def test_curatecli(bsecurate_cmd):
    _test_curatecli_cmd(bsecurate_cmd)


@pytest.mark.parametrize('bsecurate_cmd', fakebsecurate_cmds)
def test_curatecli_datadir(bsecurate_cmd):
    _test_curatecli_cmd('-d ' + fake_data_dir + ' ' + bsecurate_cmd)


def test_curatecli_makediff(tmp_path):
    tmp_path = str(tmp_path)  # Needed for python 3.5

    filename1 = '6-31G_s_s-full.json.bz2'
    filename2 = '6-31G-full.json.bz2'

    file1 = os.path.join(curate_test_data_dir, filename1)
    file2 = os.path.join(curate_test_data_dir, filename2)

    tmpfile1 = os.path.join(tmp_path, filename1)
    tmpfile2 = os.path.join(tmp_path, filename2)

    shutil.copyfile(file1, tmpfile1)
    shutil.copyfile(file2, tmpfile2)

    _test_curatecli_cmd('make-diff -l {} -r {}'.format(tmpfile1, tmpfile2))
    _test_curatecli_cmd('make-diff -l {} -r {}'.format(tmpfile2, tmpfile1))

    diff1 = fileio.read_json_basis(tmpfile1 + '.diff')
    diff2 = fileio.read_json_basis(tmpfile2 + '.diff')

    assert len(diff1['elements']) == 36
    assert len(diff2['elements']) == 0

    reffilename = '6-31G_s_s-polarization.json.bz2'
    reffile = os.path.join(curate_test_data_dir, reffilename)
    refdata = fileio.read_json_basis(reffile)

    assert curate.compare_basis(diff1, refdata, rel_tol=0.0)


def test_curatecli_compare_1():
    output = _test_curatecli_cmd('compare-basis-sets 6-31g 6-31g --version1 0 --version2 0')
    assert b"No difference found" in output

    output = _test_curatecli_cmd('compare-basis-sets 6-31g 6-31g --version1 0 --version2 0 --uncontract-general')
    assert b"No difference found" in output

    output = _test_curatecli_cmd('compare-basis-sets 6-31g 6-31g --version1 0 --version2 1')
    assert b"DIFFERENCES FOUND" in output


# yapf: disable
@pytest.mark.parametrize('filename1,filename2,expected',
                           [('6-31g-bse.gbs.bz2', '6-31g-bse.gbs.bz2', True),
                            ('6-31g-bse.gbs.bz2', '6-31g-bse.nw.bz2', True),
                            ('6-31g-bse.nw.bz2', '6-31g-bse-BAD1.gbs.bz2', False),
                            ('6-31g-bse.nw.bz2', '6-31g-bse-BAD2.gbs.bz2', False),
                            ('6-31g-bse.nw.bz2', '6-31g-bse-BAD3.gbs.bz2', False),
                            ('6-31g-bse.nw.bz2', '6-31g-bse-BAD4.gbs.bz2', False),
                            ('6-31g-bse.nw.bz2', '6-31g-bse-BAD5.gbs.bz2', False),
                            ('def2-ecp.gbs.bz2', 'def2-ecp.gbs.bz2', True),
                            ('def2-ecp.gbs.bz2', 'def2-ecp.nw.bz2', True),
                            ('def2-ecp.gbs.bz2', 'def2-ecp-BAD1.nw.bz2', False),
                            ('def2-ecp.gbs.bz2', 'def2-ecp-BAD2.nw.bz2', False),
                            ('def2-ecp.gbs.bz2', 'def2-ecp-BAD3.nw.bz2', False),
                            ('def2-ecp.gbs.bz2', 'def2-ecp-BAD4.nw.bz2', False),
                            ('def2-ecp.gbs.bz2', 'def2-ecp-BAD5.nw.bz2', False),
                            ('def2-ecp.gbs.bz2', 'def2-ecp-BAD6.gbs.bz2', False),
                            ('lanl2dz.nw.bz2', 'lanl2dz.nw.bz2', True),
                            ('lanl2dz.nw.bz2', 'lanl2dz-BAD1.nw.bz2', False),
                            ('lanl2dz.nw.bz2', 'lanl2dz-BAD2.nw.bz2', False)])
# yapf: enable
def test_curatecli_compare_files(filename1, filename2, expected):
    file1 = os.path.join(curate_test_data_dir, filename1)
    file2 = os.path.join(curate_test_data_dir, filename2)

    output = _test_curatecli_cmd('compare-basis-files {} {} --uncontract-general'.format(file1, file2))
    if expected:
        assert b"No difference found" in output
    else:
        assert b"DIFFERENCES FOUND" in output

    output = _test_curatecli_cmd('compare-basis-files {} {} --uncontract-general'.format(file2, file1))
    if expected:
        assert b"No difference found" in output
    else:
        assert b"DIFFERENCES FOUND" in output
