import gpplib
from gpplib.SA_Replanner2 import *
from gpplib.SwitchingGP_MDP import *
from gpplib.Utils import *
from gpplib.LatLonConversions import *
from gpplib.PseudoWayptGenerator import *
import os, sys
import time, datetime


llconv = LLConvert()
yy,mm,dd,hr,mi = 2012,8,17,19,24
posNoise, curNoise1 = 0.01, 0.01
numDays = 0

rmdpr = SwitchingMdpGP()
#rmdpr.LoadTransitionModelsFromShelf(yy, mm, dd, hr, mi, posNoise, curNoise1 )

start_wLat, start_wLon = 3331.063, -11820.310 # Real Start
#start_wLat, start_wLon = 3330.150, -11843.898 # Reversed Start

start_Lat, start_Lon = llconv.WebbToDecimalDeg(start_wLat, start_wLon)
startX,startY = rmdpr.saMdp.gm.GetXYfromLatLon(start_Lat,start_Lon)
goal_wLat, goal_wLon = 3330.150, -11843.898 # Real Goal
#goal_wLat, goal_wLon = 3331.063, -11820.310 # Reversed Goal
goal_Lat, goal_Lon = llconv.WebbToDecimalDeg(goal_wLat, goal_wLon)
goalX,goalY = rmdpr.saMdp.gm.GetXYfromLatLon(goal_Lat,goal_Lon)
start = (int(startX+0.5),int(startY+0.5))
goal = (int(goalX+0.5),int(goalY+0.5))
print 'Start is: (%d,%d)'%(start[0],start[1])
print 'Goal is: (%d,%d)'%(goal[0],goal[1])


dt = datetime.datetime(yy,mm,dd,hr,mi)

thetaVal = {'w_r':-1.,'w_g':100.}
#rmdpr.GetIndexedPolicy(yy,mm,dd,hr,mi,goal,theta=thetaVal)
#rmdpr.saMdp.DisplayPolicy()
#plt.title('MDP Policy with goal (%d,%d)'%(goal[0],goal[1]))
#plt.savefig('SAmdp_execution_%s.png'%(str(dt)))
rtc = RomsTimeConversion()
s_indx = rtc.GetRomsIndexFromDateTime(yy,mm,dd,dt)
rmdpr.RunSwitchingMDPforNhours(yy,mm,dd,hr,mi,start,goal,150,posNoise=posNoise,curNoise=curNoise1)
#plt.figure(); rmdpr.saMdp.gm.PlotNewRiskMapFig(); rmdpr.saMdp.gm.PlotCurrentField(s_indx)
#rmdpr.saMdp.SimulateAndPlotMDP_PolicyExecution(start,goal,s_indx,False,'r-')
        