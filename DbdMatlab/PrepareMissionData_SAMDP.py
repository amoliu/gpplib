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


class LoadMissionData(object):
    def __init__(self,**kwargs):
        self.UpdateKwArguments(**kwargs)


    def UpdateKwArguments(self, **kwargs):
        if kwargs.has_key('MissionOfInterest'):
            self.MissionOfInterest = kwargs['MissionOfInterest']

        self.conf = GppConfig()
        ascFileDir= self.conf.myDataDir + 'ProcessedAsc/'
        
        if kwargs.has_key('AscFileDir'):
            self.ascFileDir = kwargs['AscFileDir']
        else:
            self.ascFileDir = ascFileDir
        
        if kwargs.has_key('FieldsOfInterest'):
            self.FieldsOfInterest = kwargs['FieldsOfInterest']
        else:
            self.FieldsOfInterest = [ 'm_lat','m_lon','m_gps_lat','m_gps_lon','m_water_vx',  \
                                     'm_water_vy','m_depth','m_console_cd','m_present_time', \
                                     'm_iridium_console_on','m_certainly_at_surface', \
                                     'm_roll','m_pitch','c_wpt_lat','c_wpt_lon','c_pitch','c_roll','m_heading',\
                                     'c_heading','c_dive_target_depth','m_mission_avg_speed_climbing', \
                                     'm_mission_avg_speed_diving', 'm_num_half_yos_in_segment','m_stable_comms', \
                                     'c_climb_target_depth', 'm_altitude','m_altimeter_status', 'm_console_on', \
                                     'm_dist_to_wpt','m_gps_dist_from_dr', 'm_speed','m_surface_est_fw', \
                                     'm_surface_est_gps', 'm_water_delta_vx','m_water_delta_vy', \
                                     'm_tot_horz_dist', 'm_tot_num_inflections', 'm_avg_climb_rate', 'm_avg_dive_rate' ]
            
    def SaveToMat(self,matFileName):
        ''' Save the loaded data to a Mat-file
        '''
        data_dict = {}
        units_dict = {}
        mission_data = {}

        mission_data['headers'] = self.headers

        for idx, field in enumerate(self.data_fields):
            data_dict[field] = self.c_data_values[:,idx]
            units_dict[field] = self.data_units[idx]
        
        m_present_dt = []
        # Augment the data with a GMT datetime string
        for t in data_dict['m_present_time']:
            dt = time.gmtime(t); 
            m_present_dt.append(strftime('%Y-%m-%d %H:%M:%S',dt))
        data_dict['m_gmt'] = m_present_dt
        mission_data['data'] = data_dict
        mission_data['units'] = units_dict
        mission_data['fields']= self.data_fields
        
        sio.savemat( matFileName, mission_data)


    def ReadDataFromDirectory(self, **kwargs):
        ''' Loop through all the files in the data-directory and find the data that fits the criteria mentioned.
            Args:
                MissionOfInterest (string) : Name of a mission that we are interested in (eg. A_MER27.MI or HFXMDP28.MI)
                FieldsOfInterest (list of strings) : Fields of interest such as ['m_lat','m_lon','m_heading', ... ] etc.
                AscFileDir (string) : Directory in which the processed ASCii files from the glider are stored.
        '''
        self.UpdateKwArguments(**kwargs)
        # Create a list of all the files in teh directory
        self.dir_list = os.listdir( self.ascFileDir )
        self.gafr = GliderAscFileReader()

        self.fileList, self.headers = [], []
        for file in self.dir_list:
            m = re.match('([a-zA-Z0-9\_\-]+.[aAsScC]+)',file)
            if m:
                gliderName,missionName,fileOpenTime,fullFileName = self.gafr.GetGliderMissionTime(self.ascFileDir+m.group(1))
                if self.MissionOfInterest.lower() == missionName.lower():
                    self.fileList.append((fileOpenTime,fullFileName))
                    self.hdrs,self.data_fields,self.data_units,self.data_num_bytes,self.num_fields = \
                            self.gafr.LoadHeadersUnitsFields(self.ascFileDir+m.group(1))
                    self.headers.append(self.hdrs)
        # Sort headers based upon the 8x3 filename
        self.headers = sorted(self.headers, key=lambda k:k['the8x3_filename'],reverse=False)
        
        first_time = 1
        for idx, hdr in enumerate(self.headers):
            #gliderName,missionName,fileOpenTime,fullFileName = gafr.GetGliderMissionTime(ascFileDir+'%s.%s'%(hdr['filename'],hdr['filename_extension']))
            #headers,data_fields,data_units,data_num_bytes,num_fields = gafr.LoadHeadersUnitsFields(ascFileDir+m.group(1))
            self.hdrs,self.num_hdr_items,self.num_fields,self.data_fields,self.data_units, self.data_num_bytes, self.data_values = \
            self.gafr.LoadSelectFieldsFromAscFile(self.ascFileDir+'%s_%s.asc'%(hdr['filename'],hdr['filename_extension']),self.FieldsOfInterest)
            if first_time:
                self.c_data_values = self.data_values; first_time = 0
            else:
                self.c_data_values = np.vstack([self.c_data_values,self.data_values])
        
        
lmd = LoadMissionData(MissionOfInterest='RGPMDP28.MI')
lmd.ReadDataFromDirectory(AscFileDir='../GliderDataPython/ascFiles/')
lmd.SaveToMat('R_GPMDP_28.mat')
