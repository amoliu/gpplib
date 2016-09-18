'''
@author: Arvind Pereira
@contact: arvind.pereira@gmail.com
@summary: Create plots of some of the data collected in Jul, Aug 2011.
'''
import GliderFileTools
import LatLonConversions
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages/')
from pylibkml import Kml,Utilities
import KmlCreator
import GetDataFromDir
import KmlTrackCreator

# Program starts here...

MissionsDirectory = '/Users/arvind/Documents/data/20110810_GliderData/Rusalka_Flight/missions/'
MaFilesDirectory = '/Users/arvind/Documents/data/20110810_GliderData/Rusalka_Flight/mafiles/'
MissionFileName = 'ARV2RYAN.MI'   
Behavior_list = GliderFileTools.LoadMissionFile(MissionsDirectory+MissionFileName)
#GliderFileTools.PrintBehaviors(Behavior_list)

WptKml = KmlCreator.KmlCreator()

WptKml.SetIconHrefStyle('rusalka-glider-list-style','http://cinaps.usc.edu/gliders/img/glider1.png')
WptKml.SetIconHrefStyle('hehape-glider-list-style','http://cinaps.usc.edu/gliders/img/glider2.png')
WptKml.SetIconHrefStyle('start-wpt-list-style','http://maps.google.com/mapfiles/kml/paddle/grn-stars.png')
WptKml.SetIconHrefStyle('wpt-list-style','http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png')
WptKml.SetIconHrefStyle('stop-wpt-list-style','http://maps.google.com/mapfiles/kml/paddle/G.png')


# First let us save the 
for beh in Behavior_list:
    if beh.behavior=='goto_list':
        WptLatList,WptLonList = GliderFileTools.GetWptList(MaFilesDirectory+'GOTO_L'+beh.beh_vals['args_from_file']+'.MA')
        WptKml.WriteWptListToKml(WptLatList,WptLonList)
WptKml.CreateAndSaveKml('ARV2RYAN_mission.kml')




# Now let us get the data and plot the surfacing locations of the gliders

MissionOfInterest = 'ARV2RYAN.MI'
FieldsOfInterest = ['m_lat','m_lon','m_gps_lat','m_gps_lon','m_water_vx', 'm_water_vy','m_depth','m_console_cd','m_present_time',
                    #'m_iridium_console_on','m_certainly_at_surface',
                    #'m_roll','m_pitch','c_wpt_lat','c_wpt_lon','c_pitch','c_roll','m_heading','c_heading','c_dive_target_depth','m_mission_avg_speed_climbing','m_mission_avg_speed_diving',
                    #'m_num_half_yos_in_segment','m_stable_comms','c_climb_target_depth',
                    #'m_altitude','m_altimeter_status','m_console_on','m_dist_to_wpt','m_gps_dist_from_dr','m_speed',
                    #'m_surface_est_fw','m_surface_est_gps','m_water_delta_vx','m_water_delta_vy','m_tot_horz_dist', 'm_tot_num_inflections'
                    ]

GliderDataDirectory = '/Users/arvind/Documents/data/20110810_GliderData/rusalka/processed-data/'
hdrs,data_fields,data_values =GetDataFromDir.GetDataFromMissionFile( GliderDataDirectory, MissionOfInterest, FieldsOfInterest )
#PlotData(data_fields, data_values)
#CreateKML(data_values[:,data_fields.index('m_lat')],data_values[:,data_fields.index('m_lon')],data_values[:,data_fields.index('m_depth')],data_values[:,data_fields.index('m_present_time')],'001100XX.ASC')




time = data_values[:,data_fields.index('m_present_time')]
lat = data_values[:,data_fields.index('m_lat')]
lon = data_values[:,data_fields.index('m_lon')]
depth = data_values[:,data_fields.index('m_depth')]
folderName,placeMarkName = 'ARV2RYAN.MI','GliderTrack'

a = KmlTrackCreator.KmlTrackCreator()  
a.CreateKmlTrack(time,lat,lon,depth,'absolute',folderName,placeMarkName)
print a.kml
a.WriteKml('ARV2RYAN_data.kml')
