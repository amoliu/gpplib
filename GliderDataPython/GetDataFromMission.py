''' This file is intended to allow us to load up data from a mission, plot and view it.
'''
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
ascFileDir = conf.myDataDir + 'ProcessedAsc/'

dir_list  = os.listdir(ascFileDir)

FieldsOfInterest = ['m_lat','m_lon','m_gps_lat','m_gps_lon','m_water_vx', 'm_water_vy','m_depth','m_console_cd','m_present_time','m_iridium_console_on','m_certainly_at_surface',
                    'm_roll','m_pitch','c_wpt_lat','c_wpt_lon','c_pitch','c_roll','m_heading','c_heading','c_dive_target_depth','m_mission_avg_speed_climbing','m_mission_avg_speed_diving',
                    'm_num_half_yos_in_segment','m_stable_comms','c_climb_target_depth',
                    'm_altitude','m_altimeter_status',
                    'm_console_on','m_dist_to_wpt','m_gps_dist_from_dr','m_speed','m_surface_est_fw','m_surface_est_gps',
                    'm_water_delta_vx','m_water_delta_vy','m_tot_horz_dist', 'm_tot_num_inflections']
MissionOfInterest = 'H_MER_27.MI' #'R_MDP_28.MI' #'H_MER_27.MI' #'HFXMDP28.MI' #'RGPMDP28.MI' #'R_MDP_28.MI'


gafr = GliderAscFileReader.GliderAscFileReader()

fileList = []
headers = []
for file in dir_list:
    m = re.match('([a-zA-Z0-9\_\-]+.[aAsScC]+)',file)
    if m:
        gliderName,missionName,fileOpenTime,fullFileName = gafr.GetGliderMissionTime(ascFileDir+m.group(1))
        if MissionOfInterest.lower() == missionName.lower():
            fileList.append((fileOpenTime,fullFileName))
            
            hdrs,data_fields,data_units,data_num_bytes,num_fields = gafr.LoadHeadersUnitsFields(ascFileDir+m.group(1))
            headers.append(hdrs)

# Sort headers based upon the 8x3 filename

headers = sorted(headers, key=lambda k:k['the8x3_filename'],reverse=False)



first_time = 1
for idx, hdr in enumerate(headers):
        #gliderName,missionName,fileOpenTime,fullFileName = gafr.GetGliderMissionTime(ascFileDir+'%s.%s'%(hdr['filename'],hdr['filename_extension']))
        #headers,data_fields,data_units,data_num_bytes,num_fields = gafr.LoadHeadersUnitsFields(ascFileDir+m.group(1))
        hdrs,num_hdr_items,num_fields,data_fields,data_units, data_num_bytes, data_values = \
            gafr.LoadSelectFieldsFromAscFile(ascFileDir+'%s_%s.asc'%(hdr['filename'],hdr['filename_extension']),FieldsOfInterest)
        if first_time:
                c_data_values = data_values; first_time = 0
        else:
                c_data_values = np.vstack([c_data_values,data_values])
                
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

