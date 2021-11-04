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
Testing of a string containing bibtex entries

This tests by running latex/bibtex on a file containing the
string. Warnings are interpreted as failures (which catches
missing fields)
'''

import os
import shutil
import subprocess

# Other modules should query this variable
available = bool(shutil.which('bibtex')) and bool(shutil.which('latex'))

# Test latex file
test_txt = r"""
\documentclass{article}
\begin{document}
\nocite{*}
\bibliographystyle{plain}
\bibliography{bse_test}
\end{document}
"""


def validate_bibtex(tmp_path, bib_str):
    texfile = os.path.join(tmp_path, 'bse.tex')
    bibfile = os.path.join(tmp_path, 'bse_test.bib')

    with open(texfile, 'w', encoding='utf-8') as tf:
        tf.write(test_txt)

    with open(bibfile, 'w', encoding='utf-8') as bf:
        bf.write(bib_str)

    res = subprocess.check_output(['latex', 'bse'], cwd=tmp_path)

    # Run bibtex. Then check return code and scan the output for "Warning"
    res = subprocess.run(['bibtex', 'bse'],
                         universal_newlines=True,
                         cwd=tmp_path,
                         stderr=subprocess.STDOUT,
                         stdout=subprocess.PIPE)

    if "Warning" in res.stdout:
        raise RuntimeError("Warning found in output. Output is:\n" + res.stdout)
