import json
import bse


files=[ "DEF2-ECP.0.element.json",    "DEF2-QZVPP.0.element.json",   "DEF2-SVPD.0.element.json",  "DEF2-TZVPD.0.element.json",
"DEF2-QZVP.0.element.json",   "DEF2-QZVPPD.0.element.json",  "DEF2-SVPP.0.element.json",  "DEF2-TZVPP.0.element.json",
"DEF2-QZVPD.0.element.json",  "DEF2-SVP.0.element.json",     "DEF2-TZVP.0.element.json",  "DEF2-TZVPPD.0.element.json" ]

newmap = { 55: 'ahlrichs/DEF2-ECP_leininger1996a.0.json',
           56: 'ahlrichs/DEF2-ECP_kaupp1991a.0.json',
           57: 'ahlrichs/DEF2-ECP_dolg1989a.0.json',
           72: 'ahlrichs/DEF2-ECP_andrae1990a.0.json',
           73: 'ahlrichs/DEF2-ECP_andrae1990a.0.json',
           74: 'ahlrichs/DEF2-ECP_andrae1990a.0.json',
           75: 'ahlrichs/DEF2-ECP_andrae1990a.0.json',
           76: 'ahlrichs/DEF2-ECP_andrae1990a.0.json',
           77: 'ahlrichs/DEF2-ECP_andrae1990a.0.json',
           78: 'ahlrichs/DEF2-ECP_andrae1990a.0.json',
           79: 'ahlrichs/DEF2-ECP_andrae1990a.0.json',
           80: 'ahlrichs/DEF2-ECP_andrae1990a.0.json',
           81: 'ahlrichs/DEF2-ECP_metz2000b.0.json',
           82: 'ahlrichs/DEF2-ECP_metz2000a.0.json',
           83: 'ahlrichs/DEF2-ECP_metz2000a.0.json',
           84: 'ahlrichs/DEF2-ECP_peterson2003b.0.json',
           85: 'ahlrichs/DEF2-ECP_peterson2003b.0.json',
           86: 'ahlrichs/DEF2-ECP_peterson2003b.0.json' }


for f in files:
    data = bse.io.read_json_basis(f)

    for n,v in newmap.items():
        d = data['basisSetElements'][n]['elementComponents']
        newd = [ v if 'ECP' in x else x for x in d ]
        data['basisSetElements'][n]['elementComponents'] = newd

    bse.io.write_json_basis(f, data)

