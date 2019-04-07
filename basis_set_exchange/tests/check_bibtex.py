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
    res = subprocess.run(
        ['bibtex', 'bse'], universal_newlines=True, cwd=tmp_path, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)

    if "Warning" in res.stdout:
        raise RuntimeError("Warning found in output. Output is:\n" + res.stdout)
