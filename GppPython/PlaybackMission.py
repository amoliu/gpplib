from matplotlib import pyplot as plt
import numpy as np
import sys, math, random, time, datetime

from gpplib import *
from gpplib.Utils import *
from gpplib.LatLonConversions import *
from gpplib.GenGliderModelUsingRoms import GliderModel
from gpplib.MapTools import *

from PseudoWayptGenerator import *

def GetLatLonFromWebb(loc):
    llconv = LLConvert()
    return llconv.WebbToDecimalDeg(loc[0],loc[1])


conf = GppConfig()
# Start 33 31.636, -118 26.478 MER_CTOP Jul 13, 19:18

yy,mm,dd = 2012, 7, 16
# Mission started on Jul 13, 2012 at 19:18 UTC
#start1_w = (3331.636,-11826.478)
#start1_w = (3330.649,-11826.180)
#start1_w = (3338.349,-11825.978) # last start
#start1_w = (3338.183,-11832.192)
start1_w = (3331.252, -11829.394)#(3329.192,-11829.419)
s1Lat,s1Lon = GetLatLonFromWebb(start1_w)
goal1_w = (3333.9917, -11828.2000)
#goal1_w = (3333.4948,-11829.4375) # Last wpt
#goal1_w = (3330.127, -11825.3125)
g1Lat,g1Lon = GetLatLonFromWebb(goal1_w)
#g1Lat,g1Lon = (33.5582,-118.4906)
#start_dt1 = datetime.datetime(2012,7,13,19,18)
#start_dt1 = datetime.datetime(2012,7,14,1,34)
#start_dt1 = datetime.datetime.utcnow()#datetime.datetime(2012,7,15,18,28)
start_dt1 = datetime.datetime.utcnow() #(2012,7,16,20,46)
pwptg = PseudoWayPtGenerator(conf.myDataDir+'RiskMap.shelf',conf.myDataDir+'roms', \
                            roms_yy=yy,roms_mm=mm,roms_dd=dd)
pwptg.no_comms_timeout_secs = 12.5 *3600.
#pwptg.TestKwArgs(glider_vel=0.39)
pwptg.TestKwArgs(glider_vel=0.147, glider_vel_nom=0.3, max_climb_depth=2)
#pwptg.TestKwArgs(glider_vel=0.278, glider_vel_nom=0.278, max_climb_depth=2)

#pwptg.TestKwArgs(glider_vel=0.146,glider_vel_nom=0.278)
startT1 = pwptg.rtc.GetRomsIndexFromDateTime(yy,mm,dd,start_dt1)
latFin,lonFin, doneSimulating = pwptg.SimulateDive((s1Lat,s1Lon), (g1Lat,g1Lon), startT1, plot_figure=True,line_color='r-',goal_marker='k^')
# Glider had surfaced at 33 30.649, -118 26.180 on Jul 14, 1:34
# This is 
#surf_dt1 = datetime.datetime(2012,7,14,1,34)
#surf_dt1 = datetime.datetime(2012,7,14,4,58)
surf_dt1 = datetime.datetime(2012,7,16,7,9)
#surf_lat,surf_lon = pwptg.ll_conv.WebbToDecimalDeg(3330.347,-11825.692)
surf_lat,surf_lon = pwptg.ll_conv.WebbToDecimalDeg(3338.183,-11832.192)
surf_lat,surf_lon = pwptg.ll_conv.WebbToDecimalDeg(3335.080, -11831.013)
surfx,surfy = pwptg.gm.GetPxPyFromLatLon(surf_lat,surf_lon)
plt.plot(surfx,surfy,'k*')

dist2goal1 = pwptg.dc.GetDistBetweenLocs(g1Lat,g1Lon,s1Lat,s1Lon)
time2goal1 = (surf_dt1 - start_dt1).total_seconds()
gNomVel = dist2goal1/time2goal1

print dist2goal1, time2goal1, gNomVel
print latFin, lonFin
print 'Distance between simulated location and actual surfacing is:%.3f'%(pwptg.dc.GetDistBetweenLocs(latFin,lonFin,surf_lat,surf_lon))