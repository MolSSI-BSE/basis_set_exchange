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

"""
Tests validation of basis set data
"""

import bz2
import os
import json
import pytest

from basis_set_exchange import validator
from .common_testvars import validator_test_data_dir

test_files = os.listdir(validator_test_data_dir)
test_files = [x for x in test_files if x.endswith('.bz2')]


@pytest.mark.parametrize('file_rel_path', test_files)
def test_validator(file_rel_path):
    file_path = os.path.join(validator_test_data_dir, file_rel_path)
    is_bad = ".bad." in os.path.basename(file_path)
    file_type = os.path.basename(file_path).split('.')[1]

    with bz2.open(file_path, 'rt', encoding='utf-8') as tf:
        file_data = tf.read()

    if is_bad:
        # Read the first line of the file. This will contain the string
        # that should match the exception
        file_data_lines = file_data.splitlines()
        match = file_data_lines[0][8:].strip()
        json_data = json.loads('\n'.join(file_data_lines[1:]))

        with pytest.raises(Exception, match=match):
            validator.validate_data(file_type, json_data)

    else:
        json_data = json.loads(file_data)
        validator.validate_data(file_type, json_data)
