import basis_set_exchange as bse
import sys

for F in sys.argv[1:]:
    a= bse.fileio.read_json_basis(F)
    a = bse.manip.make_general(a)
    bse.fileio.write_json_basis(F, a)
