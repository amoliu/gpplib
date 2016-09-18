'''
@author: Arvind Pereira
@contact: arvind.pereira@gmail.com
@summary: Create plots of some of the data collected in Jul, Aug 2011.
'''
from LoadAscFile import LoadAscFile
import matplotlib.pyplot as plt

data_dir = '/home/supreeth/rusalka_test'
fileName = '0288000'
plt.figure()
plt.hold(True)
for i in range(0,5):
    hdrs,num_hdr_items,num_fields,data_fields,data_units, data_num_bytes, data_values = LoadAscFile('%s/%s%d.ASCa'%(data_dir,fileName,i))
    #plt.plot((data_values[:,data_fields.index('m_present_time')]-data_values[0,data_fields.index('m_present_time')])/3600,data_values[:,data_fields.index('m_depth')])
    plt.plot( data_values[:,data_fields.index('m_lon')], data_values[:,data_fields.index('m_lat')],'*',ms=16)
    #import pdb; pdb.set_trace()
plt.show()

