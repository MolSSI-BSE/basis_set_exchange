import sys
import basis_set_exchange as bse

for f in sys.argv[1:]:
    a = bse.fileio.read_json_basis(f)
    bse.fileio.write_json_basis(f, a)
