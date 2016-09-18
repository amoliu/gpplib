'''
    @author: Arvind Menezes Pereira
    @summary: Utilities to get/store glider data from .asc files
'''
import os
import re
import numpy as np
from LoadAscFile import LoadSelectFieldsFromAscFile, LoadHeadersUnitsFields, GetKMLTimeString

'''
@summary: GetDataFromMissionFile(MissionOfInterest,GliderAscDataDirectory)
        MissionOfInterest is the Mission we want to search for in the
        GliderAscDataDirectory directory.
@return: hdrs, num_hdr_items, num_fields, data_fields, data_units, c_data_values
'''
def GetDataFromMissionFile( GliderAscDataDirectory, MissionOfInterest, FieldsOfInterest ):
    dir_list = os.listdir(GliderAscDataDirectory)
    c_hdrs={}
    c_num_hdr_items=0
    c_num_fields=0
    c_data_fields=[]
    c_data_units=[] 
    c_data_num_bytes=[]
    c_data_values = np.array([])
    
    first_time = 1
    for file in dir_list:
        m_dbd = re.match('[a-zA-Z0-9\_]+.([aA][sS][cC])$',file)
        if m_dbd:
            print file
            headers,data_fields,data_units,data_num_bytes,num_fields = LoadHeadersUnitsFields(GliderAscDataDirectory+file)
            if len(headers):
                if MissionOfInterest.lower() == headers['mission_name'].lower():
                    print 'File Found: %s' %(file)
                    hdrs,num_hdr_items,num_fields,data_fields,data_units, data_num_bytes, data_values = LoadSelectFieldsFromAscFile(GliderAscDataDirectory+file,FieldsOfInterest)
                    if first_time:
                        c_data_values = data_values
                        c_data_fields = data_fields
                        c_hdrs['filename_label']=headers['filename_label']
                        first_time = 0
                    else:
                        c_data_values = np.vstack([c_data_values,data_values])
    return c_hdrs, c_data_fields, c_data_values

'''
FieldsOfInterest = ['m_lat','m_lon','m_gps_lat','m_gps_lon','m_water_vx', 'm_water_vy','m_depth','m_console_cd','m_present_time','m_iridium_console_on','m_certainly_at_surface',
                    'm_roll','m_pitch','c_wpt_lat','c_wpt_lon','c_pitch','c_roll','m_heading','c_heading','c_dive_target_depth','m_mission_avg_speed_climbing','m_mission_avg_speed_diving',
                    'm_num_half_yos_in_segment','m_stable_comms','c_climb_target_depth',
                    'm_altitude','m_altimeter_status',
                    'm_console_on','m_dist_to_wpt','m_gps_dist_from_dr','m_speed','m_surface_est_fw','m_surface_est_gps',
                    'm_water_delta_vx','m_water_delta_vy','m_tot_horz_dist', 'm_tot_num_inflections']
hdrs,data_fields,data_values = GetDataFromMissionFile('/Users/arvind/Documents/data/20110810_GliderData/rusalka/processed-data/','ARV2RYAN.MI',FieldsOfInterest)
'''
