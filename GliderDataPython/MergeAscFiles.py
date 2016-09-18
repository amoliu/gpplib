'''
Created on Aug 30, 2011

@author: Arvind Antonio de Menezes Pereira
@summary: This program which requires Python and ASCII files produced from DBD and EBD files will merge them
            to produce a single merged ASCII file.
@attention: Dependencies of this program are: SciPy and NumPy
            See: http://www.scipy.org/
'''

import numpy as np
#import scipy.io
import shelve
from LoadAscFile import LoadAscFile

RusalkaGliderDataDirectory = '/Users/arvind/Documents/data/20110810_GliderData/rusalka/processed-data/'
HeHaPeGliderDataDirectory  = '/Users/arvind/Documents/data/20110810_GliderData/he-ha-pe/processed-data/'

FileName = HeHaPeGliderDataDirectory+'00980000.ASC'
ASCfromDBD = FileName+'a'
ASCfromEBD = FileName+'b'

# Open these files
hdrsA,num_hdr_itemsA,num_fieldsA,data_fieldsA,data_unitsA, data_num_bytesA, data_valuesA = LoadAscFile(ASCfromDBD)
hdrsB,num_hdr_itemsB,num_fieldsB,data_fieldsB,data_unitsB, data_num_bytesB, data_valuesB = LoadAscFile(ASCfromEBD)

# Merge these two files
hdrs = hdrsA
num_fields = num_fieldsA + num_fieldsB
hdrs['sensors_per_cycle']=int(hdrsA['sensors_per_cycle']) + int(hdrsB['sensors_per_cycle'])

