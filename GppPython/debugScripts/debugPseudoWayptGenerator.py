from matplotlib import pyplot as plt
import sys
import numpy as np
import math, random
import time, datetime

from gpplib import *
from gpplib.Utils import *
from gpplib.LatLonConversions import *
from gpplib.GenGliderModelUsingRoms import GliderModel
from gpplib.MapTools import *
from gpplib.GliderFileTools import *



goto_file_num = 26
conf = GppConfig()
yy,mm,dd = 2012,7,18
start_dt = datetime.datetime.utcnow()

pwptg = PseudoWayPtGenerator(conf.myDataDir+'RiskMap.shelf',conf.myDataDir+'roms', \
                            roms_yy=yy,roms_mm=mm,roms_dd=dd)

pwptg.no_comms_timeout_secs = 6 * 3600.

start_wlat, start_wlon = 3330.291,-11824.928 #3329.157, -11829.444 #3329.670, -11825.695#3340.2302, -11821.1875 #3333.73,-11821.670974 # util.WebbToDecimalDeg(3333.73,-11821.670974)
startLat,startLon = pwptg.ll_conv.WebbToDecimalDeg(start_wlat, start_wlon)

goal_wlat,goal_wlon =  3328.218, -11825.861 #3333.9917, -11828.2000 # 3336.8625, -11825.3125
goalLat,goalLon = pwptg.ll_conv.WebbToDecimalDeg(goal_wlat,goal_wlon)
#goalLat,goalLon = 33.5185, -118.4866 #33.5582,-118.4906 #
print 'Goal is %f,%f'%(goalLat,goalLon)
startT=pwptg.rtc.GetRomsIndexFromDateTime(yy,mm,dd,start_dt)


latFin,lonFin, doneSimulating = pwptg.SimulateDive((startLat,startLon), (goalLat,goalLon), startT, plot_figure=True,goal_marker='g^')
print 'Without pseudo waypt. distance between Goal and Final location is: %.1f'%(pwptg.dc.GetDistBetweenLocs(goalLat,goalLon,latFin,lonFin))
pLat,pLon,doneSimulating = pwptg.GetPseudoWayPt((startLat,startLon),(goalLat,goalLon),startT)
latFin,lonFin,doneSimulating = pwptg.SimulateDive((startLat,startLon),(pLat,pLon),startT,plot_figure=True,line_color='g',goal_marker='b.')
print 'Dist between Goal and Final location is: %.1f'%(pwptg.dc.GetDistBetweenLocs(goalLat,goalLon,latFin,lonFin))

num_iter = 15
plt.figure()
latFin,lonFin,doneSimulating = pwptg.SimulateDive((startLat,startLon), (goalLat,goalLon), startT, plot_figure=True,goal_marker='g^')
print 'Without pseudo waypt. distance between Goal and Final location is: %.1f'%(pwptg.dc.GetDistBetweenLocs(goalLat,goalLon,latFin,lonFin))
pLat,pLon = pwptg.IteratePseudoWptCalculation((startLat,startLon),(goalLat,goalLon), startT, num_iter)
latFin,lonFin,doneSimulating = pwptg.SimulateDive((startLat,startLon),(pLat,pLon),startT,plot_figure=True,line_color='g',goal_marker='b.')
print 'After %d iterations, Dist between Goal and Final location is: %.1f'%(num_iter,pwptg.dc.GetDistBetweenLocs(goalLat,goalLon,latFin,lonFin))
print pLat,pLon

# Create a GOTO_LXX.MA file
new_goto_beh = GotoListFromGotoLfileGliderBehavior()
gldrEnums = GliderWhenEnums()
new_goto_beh.SetNumLegsToRun(gldrEnums.num_legs_to_run_enums['TRAVERSE_LIST_ONCE'])
new_goto_beh.SetStartWhen(gldrEnums.start_when_enums['BAW_IMMEDIATELY'])
new_goto_beh.SetStopWhen(gldrEnums.stop_when_enums['BAW_WHEN_WPT_DIST'])
new_goto_beh.SetInitialWaypoint(gldrEnums.initial_wpt_enums['CLOSEST'])
w_lat,w_lon = [],[]
wlat, wlon = pwptg.ll_conv.DecimalDegToWebb(pLat,pLon)
w_lat.append(wlat); w_lon.append(wlon)
new_goto_beh.SetWaypointListInWebbCoods(w_lat,w_lon)
AutoGenerateGotoLLfile(new_goto_beh,goto_file_num)

# Upload the file to the server.
gliderName = 'rusalka'
goto_file_name = 'GOTO_L%02d.MA'%(goto_file_num)
ggmail = GliderGMail('usc.glider','cinaps123')
dockServerDirectory = '/var/opt/gmc/gliders/%s/to-glider/'%(gliderName)     
gftp = GliderFTP(dockServerDirectory)
if gftp.DoesFileExist(goto_file_name):
    gftp.deleteFile(goto_file_name)
gftp.SaveFile(goto_file_name,goto_file_name)
gftp.Close()

f2 = open(goto_file_name,'r')
msg = 'Pseudo-WaypointGenerator.py auto-generated this file. (For use with VALSTART.MI).\n'
for line in f2.readlines():
    msg+=line
f2.close()
ggmail.mail('arvind.pereira@gmail.com','%s generated for glider: %s '%(goto_file_name,gliderName),msg,goto_file_name)
#ggmail.mail('valerio.ortenzi@googlemail.com','%s generated for glider: %s '%(goto_file_name,gliderName),msg,goto_file_name)
