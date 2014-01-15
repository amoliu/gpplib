from matplotlib import pyplot as plt
import numpy as np
import sys, math, random, time, datetime, pytz

from gpplib import *
from gpplib.Utils import *
from gpplib.LatLonConversions import *
from gpplib.GenGliderModelUsingRoms import GliderModel
from gpplib.GliderFileTools import *
from gpplib.MapTools import *
from gpplib.KmlTools import *
from gpplib.PseudoWayptGenerator import *


def GetLocalTime(dt,**kwargs):
    locTimezone = pytz.timezone('America/Los_Angeles')
    if kwargs.has_key('timezone'):
        locTimezone = pytz.timezone(kwargs['timezone'])
    return dt.replace(tzinfo=pytz.utc).astimezone(locTimezone)

miFileDir, maFileDir = '../GliderDataPython/','./'

#mission_filename = 'A_MDP_28.MI'
mission_filename = 'A_MER_27.MI'

gldrEnums = GliderWhenEnums()
conf = GppConfig()
yy,mm,dd = 2012,7,27 # ROMS data to use
numDays = 3
no_comms_time = 6 # 5 hours of no-comms
mission_file = miFileDir+ mission_filename #ARV_STRT.MI'
goto_filenum = 25#20
goto_filename = 'GOTO_L%02d.MA'%(goto_filenum)

today = datetime.datetime(yy,mm,dd,0,0) #datetime.datetime.utcnow()
today = datetime.datetime.utcnow()
print 'Time locally right now is: %s'%( str(GetLocalTime(today)))

gliderBehList = LoadMissionFile(mission_file)
for beh in gliderBehList:
    if beh.behavior=='goto_list':
        goto_filenum = int(beh.beh_vals['args_from_file'])
        goto_file = maFileDir+'GOTO_L%02d.MA'%(goto_filenum)
        goto_filename = 'GOTO_L%02d.MA'%(goto_filenum)
        print 'GOTO file referenced by mission %s is %s'%(mission_file,goto_file)
        
    if beh.behavior=='surface' and beh.beh_vals['start_when']=='%d'%(gldrEnums.start_when_enums['BAW_NOCOMM_SECS']):
        no_comms_time = int(beh.beh_vals['when_secs'])/3600.
        print 'No comms time in mission is: %.2f hours'%(no_comms_time)
        
        
goto_beh = GetGoto_Lfile(goto_file)
initial_wpt = goto_beh.beh_vals['initial_wpt']
num_legs_to_run = goto_beh.beh_vals['num_legs_to_run']
list_stop_when = goto_beh.beh_vals['list_stop_when']
print zip(goto_beh.WptLatList,goto_beh.WptLonList)

pwptg = PseudoWayPtGenerator(conf.myDataDir+'RiskMap3.shelf',conf.myDataDir+'roms', \
                            roms_yy=yy,roms_mm=mm,roms_dd=dd,roms_numDays=numDays, \
                            glider_vel=0.17, glider_vel_nom=0.278,max_dive_depth=65,min_climb_depth=5 )
pwptg.no_comms_timeout_secs = no_comms_time * 3600.
surf_delay = 15 # 5 mins delay at surface

start_wlat, start_wlon = 3332.310, -11822.255 #3330.291, -11824.928 #3329.157, -11829.444

start_wlat, start_wlon = 3332.161, -11820.698 # Saturday night. Just before starting out on the MDP.


start_wlat, start_wlon = 3330.384, -11832.579 # Sunday night.
start_wlat, start_wlon = 3332.628, -11835.557 # Monday morning *(Used 2012-7-22 till here)
start_wlat, start_wlon = 3332.530, -11834.147 # Monday afternoon. (Actual start of 2012-7-23 here)
start_wlat, start_wlon = 3334.136, -11833.233 # Monday night.
startLat,startLon = pwptg.ll_conv.WebbToDecimalDeg(start_wlat, start_wlon)

#dt = datetime.datetime.utcnow()
dt = datetime.datetime(2012,7,23,23,45,0) # Ensure this is in UTC!!!
dt = datetime.datetime(2012,7,24,4,18,40) # Monday night time.
start_wlat, start_wlon = 3331.918, -11830.826 # Tuesday afternoon (hi-jack to pickup)
startLat,startLon = pwptg.ll_conv.WebbToDecimalDeg(start_wlat, start_wlon)
startLat,startLon = 33.454466, -118.513766
#dt = datetime.datetime.utcnow()
dt = datetime.datetime(2012,7,27,21,12,0) # Ensure this is in UTC!!!

#dt = datetime.datetime.utcnow()
#dt = datetime.datetime(2012,7,21,16,36,0) # Ensure this is in UTC!!!
start_dt = dt
myTime = time.mktime(dt.timetuple())
surfTimes,surfLats,surfLons,surfDepths = [], [], [], []
surfTimes.append(myTime); surfLats.append(startLat); surfLons.append(startLon); surfDepths.append(0.)
wptLatList,wptLonList = [startLat],[startLon]

# Find the closest waypoint
closest_dist = float('inf')
closest_idx = 0
for idx,(goal_wlat,goal_wlon) in enumerate(zip(goto_beh.WptLatList,goto_beh.WptLonList)):
    goalLat,goalLon = pwptg.ll_conv.WebbToDecimalDeg(goal_wlat,goal_wlon)
    dist = pwptg.dc.GetDistBetweenLocs(goalLat,goalLon,startLat,startLon)
    if dist<closest_dist:
        closest_dist = dist
        closest_idx = idx
        closestLat,closestLon = goalLat,goalLon

if initial_wpt == '%d'%gldrEnums.initial_wpt_enums['CLOSEST']:
    start_idx = closest_idx
    print 'Initial waypoint is CLOSEST, which is: Waypoint %d (%.5f, %.5f).'%(closest_idx,closestLat,closestLon)    
elif initial_wpt == '%d'%(gldrEnums.initial_wpt_enums['ONE_AFTER_LAST_WPT_ACHIEVED']):
    start_idx = closest_idx+1 # We don't know which waypoint we last achieved do we?
    print 'Initial waypoint is ONE_AFTER_LAST, which is: Waypoint %d (%.5f, %.5f).'%(start_idx,closestLat,closestLon)    
else:
    start_idx = int(initial_wpt)
pltCurrents = True

predLats, predLons, predTimes, predDepths = None, None, None, None

for goal_wlat, goal_wlon in zip(goto_beh.WptLatList,goto_beh.WptLonList)[start_idx:]:
    #for goal_wlat, goal_wlon in zip(goto_beh.WptLatList,goto_beh.WptLonList)[start_idx:-1]:
    done = False
    while not done:
        startT=pwptg.rtc.GetRomsIndexFromDateTime(yy,mm,dd,dt)
        goalLat,goalLon = pwptg.ll_conv.WebbToDecimalDeg(goal_wlat,goal_wlon)
        wptLatList.append(goalLat); wptLonList.append(goalLon)
        #import pdb; pdb.set_trace()
        latFin,lonFin,doneSimulating = pwptg.SimulateDive((startLat,startLon), \
                (goalLat,goalLon),startT,plot_figure=True,line_color='r-',goal_marker='g*',line_width=2.5,plot_currents=pltCurrents)
        if predLats == None:
            predTimes, predLats, predLons, predDepths = pwptg.gm.tArray, pwptg.gm.latArray, pwptg.gm.lonArray, pwptg.depthArray
        else:
            lastTime = predTimes[-1]
            predTimes,predLats,predLons,predDepths = np.concatenate((predTimes,lastTime+pwptg.gm.tArray),axis=0), \
                np.concatenate((predLats,pwptg.gm.latArray),axis=0), np.concatenate((predLons,pwptg.gm.lonArray),axis=0), \
                np.concatenate((predDepths,pwptg.gm.depthArray),axis=0)
        surf_time = dt+datetime.timedelta(hours=pwptg.diveTime)
        surfTimes.append(time.mktime(surf_time.timetuple())); 
        try:
            surfLats.append(latFin[0]); surfLons.append(lonFin[0]); 
        except TypeError:
            surfLats.append(latFin); surfLons.append(lonFin)
        surfDepths.append(0.)
        print 'Started at (%.4f,%.4f), aiming for goal (%.4f,%.4f), but surfaced at (%.4f,%.4f).'%(startLat,startLon,goalLat,goalLon,latFin,lonFin)
        print 'Expected surfacing time is: %s UTC, or %s Locally'%(str(surf_time),str(GetLocalTime(surf_time)))
        print 'Dist between Goal and Final location is: %.1f m'%(pwptg.dc.GetDistBetweenLocs(goalLat,goalLon,latFin,lonFin))
        if pwptg.gm.doneSimulating:
            done = True
            print 'Hit Waypoint! Yay!'
        else:
            done = False
            print 'Surfaced due to no-comms, continuing again.'
        dt = surf_time + datetime.timedelta(seconds=surf_delay*60)
        startLat,startLon = latFin, lonFin
        
glider_name='rusalka'
ktc = KmlTools.KmlTrackCreator()
ktc.CreateLatLonKmlTrack(surfTimes,surfLats,surfLons,surfDepths,'relativeToGround','Pred_%s'%(glider_name), \
                        'Prediction_%s'%(mission_filename))
ktc.WriteKml('%s.kml'%(glider_name))

wptKml = KmlTools.WaypointListKML()
wptKml.CreateWaypointList(wptLatList,wptLonList)
wptKml.SaveKmlFile('%s_%s.kml'%(mission_filename,goto_filename))

gldrTrk = KmlTools.GppKmlTrack()
gldrTrk.CreateGxTrack(surfTimes,surfLats,surfLons,surfDepths)
gldrTrk.SaveKmlFile('%s_%s_trk.kml'%(mission_filename,goto_filename))

newPredTimes = []
start_t = time.mktime(start_dt.timetuple())-time.timezone
for t in predTimes:
    newPredTimes.append(start_t+t)
newPredLats,newPredLons,newPredDepths = list(predLats[:,0]), list(predLons[:,0]), list(predDepths)
predTrk = KmlTools.GppKmlTrack()
predTrk.CreateGxTrack(newPredTimes,newPredLats,newPredLons,newPredDepths)
predTrk.SaveKmzFile('%s_%s_predTrk.kmz'%(mission_filename,goto_filename))
