'''
Created on Aug 31, 2011

@author: Arvind Antonio de Menezes
'''
import re
import os
import numpy as np
import math
#import scipy.io
#import shelve
from LoadAscFile import LoadSelectFieldsFromAscFile, LoadHeadersUnitsFields, GetKMLTimeString
import matplotlib.pyplot as plt
import sys
import LatLonConversions

sys.path.append('/usr/local/lib/python2.7/site-packages/')
from pylibkml import Kml,Utilities
from string import replace

sys.path.append('/Users/arvind/Documents/code/workspace/ppas/src/ppas')
from roms import *

import GetDataFromDir

def process_datetime(datestr):
    '''
    Takes the string value and processes it into something that Google Earth
    can use in its <TimeStamp>
    
    Keyword arguments:
    datestr -- (string) The DateTime string
    '''
    #Get rid of the extra space between the day and month
    datestr = replace(datestr,'  ',' ')
    #Get rid of the commas
    datestr = replace(datestr,',','')
    #Turn the string into a list
    datestr = datestr.split(' ')
    #Create a list of months to search though
    month = ['January','February','March','April','May','June',
        'July','August','September','October','November','December']
    #Find the numerical value of the month
    month_index = month.index(datestr[1])+1
    #Create the string for the <TimeStamp>
    retstring = datestr[3]+'-'+str(month_index).zfill(2)+'-'+datestr[2].zfill(2)
    return retstring+'T'+datestr[4]+'Z'


def CreateKML(lat,lon,depth,mytime,fileName):
    llConv = LatLonConversions.LLConvert()
    # Here the lat,lon data is in webb format...
    placemark = []
    for i in range(0,len(lat),15):
        if not math.isnan(lat[i]) and not math.isnan(lon[i]) and not math.isnan(depth[i]) and not math.isnan(mytime[i]):
            if abs(depth[i]) < 1.0:
                d_lat,d_lon = llConv.WebbToDecimalDeg(lat[i], lon[i] )
                coordinate = Kml().create_coordinates(d_lon,d_lat,-depth[i])
                # Create a <Point> object
                point=Kml().create_point({'coordinates':coordinate,'altitudemode':'absolute'})
                # Create a <TimeStamp> object
                timestamp = Kml().create_timestamp({'when':GetKMLTimeString(mytime[i])})
                # Create the <Data> objects and place them in <ExtendedData>
                data = []
                #data.append(Kml().create_data({'name':'eqid','value':Eqid[i]}))
                data.append(Kml().create_data({'name':'lat','value':d_lat}))
                data.append(Kml().create_data({'name':'lon','value':d_lon}))
                data.append(Kml().create_data({'name':'time','value':GetKMLTimeString(mytime[i])}))
                data.append(Kml().create_data({'name':'depth','value':'%.2f'%(-depth[i])}))
                extendeddata=Kml().create_extendeddata({'data':data})
                #Create the <Placemark> object
                placemark.append(Kml().create_placemark({'point':point,
                                                         'extendeddata':extendeddata,
                                                        'styleurl':'#primary-style'}))
    #Create the <Icon> object for the <IconStyle>
    icon_href = 'http://cinaps.usc.edu/gliders/img/glider7.png'
    iconstyleicon = Kml().create_iconstyleicon({'href':icon_href})
    #Create the <IconStyle> object
    iconstyle =Kml().create_iconstyle({'icon':iconstyleicon})
    style = []
    style.append(Kml().create_style({'id':'primary-style','iconstyle':iconstyle,'color':'ff0400ff'}))
    #Put the Placemarks in a <Folder> object
    folder = []
    folder.append(Kml().create_folder({'name':'DR-data', 'placemark':placemark }))
    # Put it into a <Document> object
    document = Kml().create_document({'folder':folder,'style':style})
    
    # Create the Final <Kml> object
    kml = Kml().create_kml({'document':document})
    fName = re.match('([0-9a-zA-Z\_]+).([aA][sS][cC])$',fileName)
    kmlFileName = fName.group(1)+'.kml'
    print "Writing KML file to: %s"%(kmlFileName)
    
    #Write the Kml object to GPStest.kml
    toFile = open(kmlFileName,'w')
    toFile.write(Utilities().SerializePretty(kml))
    toFile.close()
    
        

def PlotData(data_fields,data_values):
    plt.figure(1)
    plt.title('Glider Path Lon vs. Lat')
    #plt.plot(Data['m_present_time']-Data['m_present_time'][0],Data['m_console_cd'],'*-')
    plt.plot(data_values[:,data_fields.index('m_lon')],data_values[:,data_fields.index('m_lat')],'b.')
    plt.plot(data_values[:,data_fields.index('m_gps_lon')],data_values[:,data_fields.index('m_gps_lat')],'r*')  
    plt.plot(data_values[:,data_fields.index('c_wpt_lon')],data_values[:,data_fields.index('c_wpt_lat')],'g*')
    plt.xlabel('longitude')
    plt.ylabel('latitude')
    plt.legend(('Glider DR Lat-Lon' ,'GPS Lat-Lon', 'Commanded Lat-Lon') )
    
    plt.figure(2) 
    plt.title('Console CD vs. time')
    plt.plot(data_values[:,data_fields.index('m_present_time')]-data_values[0,data_fields.index('m_present_time')],data_values[:,data_fields.index('m_console_cd')],'b+')
    plt.plot(data_values[:,data_fields.index('m_present_time')]-data_values[0,data_fields.index('m_present_time')],data_values[:,data_fields.index('m_certainly_at_surface')],'r+-')
    plt.legend(('Console Carrier-Detect','At Surface'))
    #plt.plot(data_values[:,data_fields.index('m_gps_lon')],data_values[:,data_fields.index('m_gps_lat')],'r*')  
    plt.figure(3)
    plt.title('Depth and Altitude vs. time'),plt.xlabel('Time'),plt.ylabel('Depth')
    plt.plot(data_values[:,data_fields.index('m_present_time')]-data_values[0,data_fields.index('m_present_time')],-data_values[:,data_fields.index('m_depth')],'b+-')
    plt.plot(data_values[:,data_fields.index('m_present_time')]-data_values[0,data_fields.index('m_present_time')],-data_values[:,data_fields.index('c_dive_target_depth')],'g.-')
    plt.plot(data_values[:,data_fields.index('m_present_time')]-data_values[0,data_fields.index('m_present_time')],-data_values[:,data_fields.index('c_climb_target_depth')],'k.-')
    plt.plot(data_values[:,data_fields.index('m_present_time')]-data_values[0,data_fields.index('m_present_time')],-data_values[:,data_fields.index('m_altitude')],'m.-')
    plt.legend(('Depth','DiveTargetDepth','ClimbTargetDepth','Altitude'))
    
    plt.figure(4)
    plt.title('Heading vs. time'),plt.xlabel('Time'),plt.ylabel('Heading in degrees')
    plt.plot(data_values[:,data_fields.index('m_present_time')]-data_values[0,data_fields.index('m_present_time')],data_values[:,data_fields.index('m_heading')]*180./math.pi,'b.-')
    plt.plot(data_values[:,data_fields.index('m_present_time')]-data_values[0,data_fields.index('m_present_time')],data_values[:,data_fields.index('c_heading')]*180./math.pi,'g.-')
    plt.legend(('Measured Heading','Commanded Heading'))
    #plt.plot(data_values[:,data_fields.index('m_water_vx')],data_values[:,data_fields.index('m_water_vy')])
    
    plt.figure(5)
    plt.title('Roll and Pitch vs. time'),plt.xlabel('Time'),plt.ylabel('Roll/Pitch in degrees')
    plt.plot(data_values[:,data_fields.index('m_present_time')]-data_values[0,data_fields.index('m_present_time')],data_values[:,data_fields.index('m_pitch')]*180./math.pi,'b-')
    plt.plot(data_values[:,data_fields.index('m_present_time')]-data_values[0,data_fields.index('m_present_time')],data_values[:,data_fields.index('m_roll')]*180./math.pi,'g.-')
    plt.plot(data_values[:,data_fields.index('m_present_time')]-data_values[0,data_fields.index('m_present_time')],data_values[:,data_fields.index('c_pitch')]*180./math.pi,'y-')
    plt.plot(data_values[:,data_fields.index('m_present_time')]-data_values[0,data_fields.index('m_present_time')],data_values[:,data_fields.index('c_roll')]*180./math.pi,'m.-')
    plt.legend(('Measured Pitch','Measured Roll','Commanded Pitch','Commanded Roll'))
    
FieldsOfInterest = ['m_lat','m_lon','m_gps_lat','m_gps_lon','m_water_vx', 'm_water_vy','m_depth','m_console_cd','m_present_time','m_iridium_console_on','m_certainly_at_surface',
                    'm_roll','m_pitch','c_wpt_lat','c_wpt_lon','c_pitch','c_roll','m_heading','c_heading','c_dive_target_depth','m_mission_avg_speed_climbing','m_mission_avg_speed_diving',
                    'm_num_half_yos_in_segment','m_stable_comms','c_climb_target_depth',
                    'm_altitude','m_altimeter_status','m_console_on','m_dist_to_wpt','m_gps_dist_from_dr','m_speed',
                    'm_surface_est_fw','m_surface_est_gps','m_water_delta_vx','m_water_delta_vy','m_tot_horz_dist', 'm_tot_num_inflections']
CommsDetails=['m_certainly_at_surface', 'm_console_cd','m_stable_comms','m_iridium_status','m_iridium_on','m_iridium_console_on','m_iridium_redials', 'm_iridium_signal_strength' ]
MissionDetails=['m_dist_to_wpt','m_depth','m_lat','m_lon','m_pitch','m_speed',]


KeywordsOfInterest = [ 'depth', 'vx', 'vy', 'surface', 'console', 'iridium', 'lat', 'lon', 'fw', 'freewave','wpt' ,'present_time']

RusalkaGliderDataDirectory = '/Users/arvind/Documents/data/20110810_GliderData/rusalka/processed-data/'
HeHaPeGliderDataDirectory  = '/Users/arvind/Documents/data/20110810_GliderData/he-ha-pe/processed-data/'
AscFileName = RusalkaGliderDataDirectory+'00600000.ASC'

MissionOfInterest = 'ARV2RYAN.MI'

hdrs,data_fields,data_values =GetDataFromDir.GetDataFromMissionFile( RusalkaGliderDataDirectory, MissionOfInterest, FieldsOfInterest )
PlotData(data_fields, data_values)
CreateKML(data_values[:,data_fields.index('m_lat')],data_values[:,data_fields.index('m_lon')],data_values[:,data_fields.index('m_depth')],data_values[:,data_fields.index('m_present_time')],'001100XX.ASC')
'''
FileList = ['00110000.ASC','00110001.ASC','00110002.ASC'] # All the way till '001100110.ASC'

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
                PlotData(data_fields,c_data_values)
                CreateKML(c_data_values[:,data_fields.index('m_lat')],c_data_values[:,data_fields.index('m_lon')],c_data_values[:,data_fields.index('m_depth')],c_data_values[:,data_fields.index('m_present_time')],file)
'''



if __name__ == '__main__':
    print KeywordsOfInterest
    
    # Load the file
    #hdrs,num_hdr_items,num_fields,data_fields,data_units, data_num_bytes, data_values = LoadSelectFieldsFromAscFile(AscFileName,FieldsOfInterest)
    
    # Now find all the keywords we have been looking for and the data associated with them.
    '''
    FieldOfInterestSet = []
    for data_field in data_fields:
        for keyword in KeywordsOfInterest:
            m_keyword = re.match('[a-zA-Z]'+'[a-zA-Z\_0-9]*'+keyword+'[a-zA-Z0-9\_]*',data_field)
            if m_keyword:
                FieldOfInterestSet.append(data_field)
                
                
    print FieldOfInterestSet
    FOI_indices = []
    Data = {}
    '''
    # Get the data for each of these fields of interest and store it in a .csv file
    '''
    for fieldOfInterest in FieldOfInterestSet:
        Data[fieldOfInterest] = GetDataForField(fieldOfInterest,data_fields,data_values)
        
    print Data.keys()
    '''
    #plt.plot(data_values[:,data_fields.index('m_present_time')],data_values[:,data_fields.index('sci_fl3slov2_rhod_units')],'*')
