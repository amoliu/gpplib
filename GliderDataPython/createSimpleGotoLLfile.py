'''
 This file tests the GOTO_LXY.MA file creation aspects of GliderFileTools
'''
from gpplib.GliderFileTools import *
import random
from sets import Set
import gpplib
from gpplib.Utils import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.SA_Replanner import *
from gpplib.LatLonConversions import *

''' Code to write out a goto_lXY.ma file. Here we are going to write out to GOTO_L16.MA
'''
goto_ll_file_num = 96 # Works with Hold missions for Rusalka and HeHaPe
# Create our own .MA file from scratch.
new_goto_beh = GotoListFromGotoLfileGliderBehavior()

gldrEnums=GliderWhenEnums()
#new_goto_beh.SetNumLegsToRun(gldrEnums.num_legs_to_run_enums['LOOP_FOREVER'])  # Use this to loop forever.
new_goto_beh.SetNumLegsToRun(gldrEnums.num_legs_to_run_enums['TRAVERSE_LIST_ONCE'])
new_goto_beh.SetStartWhen(gldrEnums.start_when_enums['BAW_IMMEDIATELY'])
new_goto_beh.SetStopWhen(gldrEnums.stop_when_enums['BAW_WHEN_WPT_DIST'])
new_goto_beh.SetInitialWaypoint(gldrEnums.initial_wpt_enums['CLOSEST'])

'''
lat,lon = [],[]
lat.append( 33.476299); lon.append(-118.491195)
lat.append( 33.473344); lon.append(-118.485051)
lat.append( 33.469625); lon.append(-118.491003)
lat.append( 33.472600); lon.append(-118.497328)

#lat,lon = 33.548370359111111, -118.55799999999999
#lat,lon = 33.50815, -118.4343 # Catalina start
#lat,lon = 33.674050, -118.362235 # Pt.Fermin start
llconv = LLConvert()
w_lat,w_lon = [],[]
for (lat1,lon1) in zip(lat,lon):
    wlat, wlon = llconv.DecimalDegToWebb(lat1,lon1)
    w_lat.append(wlat); w_lon.append(wlon)
'''

#lat, lon = 33.50575, -118.729895 # WP1
#lat, lon =  33.5643, -118.3078 #33.479671, -118.501011 # WP2
#lat,lon = 33.435377, -118.335061
#lat,lon = 33.45266, -118.330768
#lat,lon = 33.47, -118.42
lat,lon = 33.505, -118.531 # MISSTRTC.MI for 2nd experiment.
lat,lon =  33.474300, -118.48526 # Recovery Location.
w_lat, w_lon = [], []

llconv = LLConvert()
wlat,wlon = llconv.DecimalDegToWebb(lat,lon)
w_lat.append(wlat); w_lon.append(wlon)


#w_lat.append(3329.356); w_lon.append(-11831.019)
#w_lat.append(3334.389); w_lon.append(-11828.068)


''' # The following points were used for the test which started on Jul 27 and ended Jul 29
w_lat.append(3326.830); w_lon.append(-11819.922)
w_lat.append(3326.830); w_lon.append(-11820.564)
w_lat.append(3327.332); w_lon.append(-11820.564)
w_lat.append(3327.332); w_lon.append(-11819.922)
'''
'''
# The following points were used for the test which started on Jul 29.
w_lat.append(3331.562); w_lon.append(-11844.103)
w_lat.append(3331.562); w_lon.append(-11843.493)
w_lat.append(3331.293); w_lon.append(-11843.493)
w_lat.append(3331.293); w_lon.append(-11844.103)
'''

#w_lat.append(3331.562); w_lon.append(-11844.103) # Just go to the start location

#v_hold_lat,v_hold_lon =  33.546182, -118.573865
#wlat, wlon = llconv.DecimalDegToWebb(v_hold_lat,v_hold_lon)
#w_lat.append(wlat); w_lon.append(wlon)

new_goto_beh.SetWaypointListInWebbCoods(w_lat,w_lon)
AutoGenerateGotoLLfile(new_goto_beh,goto_ll_file_num)

''' Might want to go to http://cinaps.usc.edu/gliders/waypoints.php to test the output GOTO_L16.MA file.
'''
ggmail = GliderGMail('usc.glider','cinaps123')
 
gliderName = 'rusalka'       
#gliderName = 'he-ha-pe'
#gliderName = 'he-ha-pe'
#gliderName = 'sim_039'
dockServerDirectory = '/var/opt/gmc/gliders/%s/to-glider/'%(gliderName)     
gftp = GliderFTP(dockServerDirectory)
gotoLfile = 'GOTO_L%02d.MA'%(goto_ll_file_num)
try:
    gftp.deleteFile(gotoLfile)
except:
    pass
gftp.SaveFile(gotoLfile,gotoLfile)
gftp.Close()

f2 = open('GOTO_L%02d.MA'%(goto_ll_file_num))
msg = ''
for line in f2.readlines():
    msg+=line
f2.close()
ggmail.mail('arvind.pereira@gmail.com','GOTO_L%02d.MA generated for glider %s, (start=%.5f,%.5f)'%(goto_ll_file_num,gliderName,w_lat[0],w_lon[0]),msg,gotoLfile)
#ggmail.mail('ryan.smith@qut.edu.au','GOTO_L%02d.MA generated for glider %s, (start=%.5f,%.5f)'%(goto_ll_file_num,gliderName,w_lat[0],w_lon[0]),msg,gotoLfile)
#ggmail.mail('arvind.pereira@gmail.com','GOTO_L%02d.MA generated (start=%.5f,%.5f)'%(goto_ll_file_num,lat[0],lon[0]),msg,gotoLfile)
#ggmail.mail('mragan@usc.edu','GOTO_L%02d.MA generated (start=%.5f,%.5f)'%(goto_ll_file_num,lat[0],lon[0]),msg,gotoLfile)