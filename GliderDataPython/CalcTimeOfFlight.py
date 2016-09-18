'''
    Given current map(s), start time, start location and desired location, calculate TimeOfFlight and TargetToAimFor    
'''

import numpy as np
import matplotlib.pyplot as plt
from LoadAscFile import LoadSelectFieldsFromAscFile, LoadHeadersUnitsFields, GetKMLTimeString
import LatLonConversions
import os, sys, re
sys.path.append('/usr/local/lib/python2.7/site-packages/')
#from pylibkml import Kml,Utilities
from string import replace
#sys.path.append(/ppas')
#import ppas
#from ppas.roms import *

FieldsOfInterest = ['m_lat','m_lon','m_gps_lat','m_gps_lon','m_water_vx', 'm_water_vy','m_depth','m_console_cd','m_present_time','m_iridium_console_on','m_certainly_at_surface',
                    'm_roll','m_pitch','c_wpt_lat','c_wpt_lon','c_pitch','c_roll','m_heading','c_heading','c_dive_target_depth','m_mission_avg_speed_climbing','m_mission_avg_speed_diving',
                    'm_num_half_yos_in_segment','m_stable_comms','c_climb_target_depth',
                    'm_altitude','m_altimeter_status',
                    'm_console_on','m_dist_to_wpt','m_gps_dist_from_dr','m_speed','m_surface_est_fw','m_surface_est_gps',
                    'm_water_delta_vx','m_water_delta_vy','m_tot_horz_dist', 'm_tot_num_inflections']

MissionOfInterest = 'ARV2RYAN.MI'
RusalkaGliderDataDirectory = '/Users/arvind/Documents/data/20110810_GliderData/rusalka/processed-data/'
HeHaPeGliderDataDirectory  = '/Users/arvind/Documents/data/20110810_GliderData/he-ha-pe/processed-data/'

# Go through the directory and keep finding all the ASCII files with this mission name in their header
dir_list = os.listdir(RusalkaGliderDataDirectory)
c_hdrs={}
c_num_hdr_items=0
c_num_fields=0
c_data_fields=[]
c_data_units=[] 
c_data_num_bytes=[]

first_time = 1
for file in dir_list:
    m_dbd = re.match('[a-zA-Z0-9\_]+.(ASC|asc)$',file)
    if m_dbd:
        print file
        headers,data_fields,data_units,data_num_bytes,num_fields = LoadHeadersUnitsFields(RusalkaGliderDataDirectory+file)
        if len(headers):
            if MissionOfInterest.lower() == headers['mission_name'].lower():
                print 'File Found: %s' %(file)
                hdrs,num_hdr_items,num_fields,data_fields,data_units, data_num_bytes, data_values = LoadSelectFieldsFromAscFile(RusalkaGliderDataDirectory+file,FieldsOfInterest)
                if first_time:
                    c_data_values = data_values
                    first_time = 0
                else:
                    c_data_values = np.vstack([c_data_values,data_values])
                #PlotData(data_fields,c_data_values)
                #CreateKML(c_data_values[:,data_fields.index('m_lat')],c_data_values[:,data_fields.index('m_lon')],c_data_values[:,data_fields.index('m_depth')],c_data_values[:,data_fields.index('m_present_time')],file)
