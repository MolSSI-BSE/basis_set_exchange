#!/usr/bin/env python3

import os
import sys
from pprint import pprint
import basis_set_exchange as bse
from basis_set_exchange.curate import add_from_components

add_from_components(['binning_641.0.json', 'binning-diffuse.0.json'], 
                     # data_dir             subdir            filebase        name          family     role        desc                            v     revision desc
                     bse.get_data_dir(), 'binning/bse_v0', 'binning_641+', 'binning 641+', 'binning', 'orbital', 'Binning/Curtiss 641 + diffuse', '0', 'Data compiled from original BSE')

add_from_components(['binning_641.0.json', 'binning-d-polarization.0.json', 'binning-diffuse.0.json'], 
                     bse.get_data_dir(), 'binning/bse_v0', 'binning_641+_d', 'binning 641+(d)', 'binning', 'orbital', 'Binning/Curtiss 641 + d polarization + diffuse', '0', 'Data compiled from original BSE')

add_from_components(['binning_641.0.json', 'binning-d-polarization.0.json', 'binning-f-polarization.0.json', 'binning-diffuse.0.json'], 
                     bse.get_data_dir(), 'binning/bse_v0', 'binning_641+_df', 'binning 641+(df)', 'binning', 'orbital', 'Binning/Curtiss 641 + df polarization + diffuse', '0', 'Data compiled from original BSE')
                      
add_from_components(['binning_962.0.json', 'binning-diffuse.0.json'], 
                     # data_dir             subdir            filebase        name          family     role        desc                            v     revision desc
                     bse.get_data_dir(), 'binning/bse_v0', 'binning_962+', 'binning 962+', 'binning', 'orbital', 'Binning/Curtiss 962 + diffuse', '0', 'Data compiled from original BSE')

add_from_components(['binning_962.0.json', 'binning-d-polarization.0.json', 'binning-diffuse.0.json'], 
                     bse.get_data_dir(), 'binning/bse_v0', 'binning_962+_d', 'binning 962+(d)', 'binning', 'orbital', 'Binning/Curtiss 962 + d polarization + diffuse', '0', 'Data compiled from original BSE')

add_from_components(['binning_962.0.json', 'binning-d-polarization.0.json', 'binning-f-polarization.0.json', 'binning-diffuse.0.json'], 
                     bse.get_data_dir(), 'binning/bse_v0', 'binning_962+_df', 'binning 962+(df)', 'binning', 'orbital', 'Binning/Curtiss 962 + df polarization + diffuse', '0', 'Data compiled from original BSE')
                      
