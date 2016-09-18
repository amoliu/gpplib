import gpplib
from gpplib.GliderAscFileReader import *
from gpplib.Utils import *
from gpplib.GliderFileTools import *
import random
from sets import Set
import gpplib
from gpplib.Utils import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.StateActionMDP import *
from gpplib.LatLonConversions import *
from gpplib.PseudoWayptGenerator import *
import time,datetime
import ftplib
import numpy as np
import scipy.io as sio
import sys, os, re

conf = GppConfig()
ascFileDir = conf.myDataDir + '2013_April/ASC/'
dir_list = os.listdir(ascFileDir)

FieldsOfInterest = ['m_is_ballast_pump_moving', 'm_ballast_pumped', 'm_air_pump', 
                    'm_battery', 'm_gps_on','m_console_on', 'm_iridium_on', 'm_science_on',
                    'm_present_time','m_tot_num_inflections','m_heading']
MissionOfInterest = 'PVCATCC.MI'
gafr = GliderAscFileReader.GliderAscFileReader()

fileList = []
headers = []
for file in dir_list:
    m = re.match('([a-zA-Z0-9\_\-]+.[aAsScC]+)',file)
    if m:
        #import pdb; pdb.set_trace()
        try:
            gliderName,missionName,fileOpenTime,fullFileName = gafr.GetGliderMissionTime(ascFileDir+m.group(1))
            if MissionOfInterest.lower() == missionName.lower():
                fileList.append((fileOpenTime,fullFileName))
                
                hdrs,data_fields,data_units,data_num_bytes,num_fields = gafr.LoadHeadersUnitsFields(ascFileDir+m.group(1))
                headers.append(hdrs)
        except UnboundLocalError:
            pass
        except IOError:
            pass

# Sort headers based upon the 8x3 filename

headers = sorted(headers, key=lambda k:k['the8x3_filename'],reverse=False)

first_time = 1
for idx, hdr in enumerate(headers):
        #gliderName,missionName,fileOpenTime,fullFileName = gafr.GetGliderMissionTime(ascFileDir+'%s.%s'%(hdr['filename'],hdr['filename_extension']))
        #headers,data_fields,data_units,data_num_bytes,num_fields = gafr.LoadHeadersUnitsFields(ascFileDir+m.group(1))
        #import pdb; pdb.set_trace()
        try:
            hdrs,num_hdr_items,num_fields,data_fields,data_units, data_num_bytes, data_values = \
                gafr.LoadSelectFieldsFromAscFile(ascFileDir+'%s_%s.asc'%(hdr['filename'],hdr['filename_extension']),FieldsOfInterest)
                
            if first_time:
                    c_data_values = data_values; first_time = 0
            else:
                    c_data_values = np.vstack([c_data_values,data_values])
        except IOError:
            pass
        except UnboundLocalError:
            pass
        except NameError:
            pass
                
data_dict = {}
units_dict = {}
mission_data = {}

mission_data['headers'] = headers

for idx, field in enumerate(data_fields):
    data_dict[field] = c_data_values[:,idx]
    units_dict[field] = data_units[idx]

m_present_dt = []
# Augment the data with a GMT datetime string
for t in data_dict['m_present_time']:
    dt = time.gmtime(t); 
    m_present_dt.append(strftime('%Y-%m-%d %H:%M:%S',dt))
data_dict['m_gmt'] = m_present_dt
mission_data['data'] = data_dict
mission_data['units'] =units_dict
mission_data['fields']=data_fields

sio.savemat(MissionOfInterest+'.mat',mission_data)

# Plot the battery data
plt.subplot(3,1,1)
plt.plot((data_dict['m_present_time']-data_dict['m_present_time'][0])/3600.0,data_dict['m_battery'],'y.-',label='Bat')
plt.hold(True)
plt.plot((data_dict['m_present_time']-data_dict['m_present_time'][0])/3600.0,data_dict['m_console_on']* 10,'g+',label='Fwave')
plt.plot((data_dict['m_present_time']-data_dict['m_present_time'][0])/3600.0,data_dict['m_air_pump']* 10,'r+',label='AirPump')
plt.plot((data_dict['m_present_time']-data_dict['m_present_time'][0])/3600.0,data_dict['m_iridium_on']* 10,'m^',label='Irid')
plt.plot((data_dict['m_present_time']-data_dict['m_present_time'][0])/3600.0,data_dict['m_science_on']* 10,'b^',label='Sci')
plt.plot((data_dict['m_present_time']-data_dict['m_present_time'][0])/3600.0,data_dict['m_is_ballast_pump_moving']* 10,'c^',label='Bpump')
plt.legend()
plt.xlabel('Time (hrs)')

plt.subplot(3,1,2)
plt.plot((data_dict['m_present_time']-data_dict['m_present_time'][0])/3600.0,data_dict['m_ballast_pumped_energy'],'b.-')
plt.ylabel('Ballast energy')

plt.subplot(3,1,3)
plt.plot((data_dict['m_present_time']-data_dict['m_present_time'][0])/3600.0,data_dict['m_tot_num_inflections'],'b.-')
plt.ylabel('Tot inflections')

'''
gm = GliderModel(conf.myDataDir+'RiskMap3.shelf',conf.romsDataDir)
gm.PlotNewRiskMapFig(True)
llconv = LLConvert()
m_lat,m_lon = llconv.NpWebbToDecimalDeg(data_dict['m_lat'],data_dict['m_lon'])
m_lat,m_lon = m_lat[~np.isnan(m_lat)],m_lon[~np.isnan(m_lon)]
x,y = gm.GetXYfromLatLon(m_lat,m_lon)
plt.plot(x,y,'y-')
m_gps_lat, m_gps_lon =  llconv.NpWebbToDecimalDeg(data_dict['m_gps_lat'],data_dict['m_gps_lon'])
m_gps_lat,m_gps_lon = m_gps_lat[~np.isnan(m_gps_lat)],m_gps_lon[~np.isnan(m_gps_lon)]
gpsX,gpsY = gm.GetXYfromLatLon(m_gps_lat,m_gps_lon)
plt.plot(gpsX,gpsY,'k^')
c_lat, c_lon = llconv.NpWebbToDecimalDeg(data_dict['c_wpt_lat'],data_dict['c_wpt_lon'])
cX, cY = gm.GetXYfromLatLon(c_lat,c_lon)
plt.plot(cX,cY,'g*')
'''

