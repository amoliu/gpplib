''' This file is going to simulate the runs of a GP-MDP planner as well as a Fixed MDP planner going from a particular start location to a
particular goal location '''
from gpplib.GliderFileTools import *
import random
from sets import Set
import gpplib
from gpplib.Utils import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.StateActionMDP2 import SA_MDP2
from gpplib.LatLonConversions import *
from gpplib.PseudoWayptGenerator import *
import datetime

rtc = RomsTimeConversion()

conf = GppConfig()
yy,mm,dd = 2012,8,17
numDays = 0
posNoise = 0.01
saMdp = SA_MDP2(conf.myDataDir )
saMdp.GetTransitionModelFromShelf(yy, mm, dd, numDays, posNoise, conf.myDataDir+'NoisyGliderModels4' )
saMdp.GetRomsData(yy,mm,dd,numDays,True,True)
util = LLConvert()

goal_wLat, goal_wLon =  3330.150, -11843.898 # Goal location for Expt 3: starting on Aug 17, 2012.
goalLat, goalLon = util.WebbToDecimalDeg(goal_wLat,goal_wLon)
goalX,goalY = saMdp.gm.GetXYfromLatLon(goalLat,goalLon)

start_wLat, start_wLon = 3331.017, -11843.499 
startLat,startLon = util.WebbToDecimalDeg(start_wLat, start_wLon)
startX, startY = saMdp.gm.GetXYfromLatLon(startLat,startLon)

start = (int(startX+0.5),int(startY+0.5))
goal = (int(goalX+0.5),int(goalY+0.5))
print 'Start is: (%d,%d)'%(start[0],start[1])
print 'Goal is: (%d,%d)'%(goal[0],goal[1])

thetaVal = {'w_r':-1.,'w_g':100.}
saMdp.GetIndexedPolicy(yy,mm,dd,numDays,goal,theta=thetaVal)
saMdp.DisplayPolicy()
plt.title('MDP Policy with goal (%d,%d)'%(goal[0],goal[1]))
plt.savefig('SAmdp_execution_%s.png'%(str(dt)))
saMdp.GetRomsData(yy, mm, dd, numDays, True, True)

no_comms_time = 5.0
