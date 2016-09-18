import sys
sys.path.append('..')
from gpplib import *
from gpplib.GenGliderModelUsingRoms import GliderModel
from matplotlib import pyplot as plt
import numpy as np
import math, random
import time
from gpplib.LatLonConversions import *
import datetime
from gpplib.Utils import *

conf = GppConfig()
gm = GliderModel(conf.myDataDir+'RiskMap.shelf',conf.myDataDir+'roms')
dt = datetime.datetime.today()
yy,mm,dd,numDays = 2012,7,13,2 #dt.year, dt.month, dt.day -1
u,v,time1,depth,lat,lon = gm.GetRomsData(yy,mm,dd,numDays,True,True)
#yy,mm,dd,numDays = 2012,1,1,2

util = LLConvert()
rtc = RomsTimeConversion()
# Pt. Fermin (GOAL) is at: 33.6745, -118.362235
#goalLat, goalLon = 33.6745, -118.362235
#goalX,goalY = sarp.gm.GetXYfromLatLon(goalLat,goalLon)

''' GOTO_L25.MA
-11825.3125     3330.1271
-11821.1875     3333.4948
-11821.1875     3336.8625
-11821.1875     3340.2302
'''

# Un-comment when we have the real glider surfacing location.
#start_wLat,start_wLon = 3330.347, -11825.692
#goal_wlat, goal_wlon =  3333.4948, -11821.1875 #3330.1271, -11825.3125

goal_wlat,goal_wlon = 3336.8626, -11821.1875
goalLat,goalLon = util.WebbToDecimalDeg(goal_wlat,goal_wlon)

#start_wlat, start_wlon = 3333.325, -11823.000 #3331.636, -11826.478

start_wlat, start_wlon = 3333.73,-11821.670974 # util.WebbToDecimalDeg(3333.73,-11821.670974)
startLat,startLon = util.WebbToDecimalDeg(start_wlat, start_wlon)
#startLat, startLon = 33.50815, -118.4343
#startX, startY = sarp.gm.GetXYfromLatLon(startLat,startLon)
#start_dt = datetime.datetime(2012,7,14,13,12)
start_dt = datetime.datetime.utcnow()
startT=rtc.GetRomsIndexFromDateTime(yy,mm,dd,start_dt)


def runSimulation( start, goal, startT, maxTimeToRun=8.0, maxDepth=80 ):
    conf = GppConfig()
    #gm = GliderModel(conf.myDataDir+'RiskMap.shelf',conf.myDataDir+'/roms/')
    #u,v,time1,depth,lat,lon = gm.GetRomsData(yy,mm,dd,numDays,True,True)
    
    plt.figure(),plt.imshow(gm.riskMapArray,origin='lower')
    FullSimulation,HoldValsOffMap=False,True
    #for i in range(0,2):
    '''
    xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist=\
        gm.SimulateDive(gm.lat_pts[1]+random.gauss(0,0.1),gm.lon_pts[6]+random.gauss(0,0.1),gm.lat_pts[5],gm.lon_pts[1],80,u,v,lat,lon,depth,i,False)
    '''
    goalx,goaly = gm.GetPxPyFromLatLon(goal[0],goal[1])
    print goalx, goaly
    plt.plot(goalx,goaly,'g^')
    
    gm.gVel = 0.278 * 0.7
    gm.InitSim(start[0],start[1],goal[0],goal[1],maxDepth,startT,FullSimulation,HoldValsOffMap)
    xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist=\
        gm.SimulateDive_R(maxTimeToRun)
    
    print 'Flag for Simulation Completion = ',gm.doneSimulating
    #xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist=\
    #    gm.SimulateDive_R(True,10)
    #gm.SimulateDive(gm.lat_pts[1]+random.gauss(0,0.1),gm.lon_pts[6]+random.gauss(0,0.1),gm.lat_pts[5],gm.lon_pts[1],80,u,v,lat,lon,depth,i,False)
    if possibleCollision == False:
                tempX,tempY = gm.GetPxPyFromLatLon(np.array(latArray),np.array(lonArray))
                x_sims,y_sims = tempX[-1:],tempY[-1:] # TODO: This might be wrong!
                plt.plot(tempX,tempY,'r-')
    else:
                    
        tempX,tempY = gm.GetPxPyFromLatLon(np.array(latArray),np.array(lonArray))
        plt.plot(tempX,tempY,'r.-')
        x_sims,y_sims = 0,0
    plt.figure();
    plt.plot(gm.tArray[0:gm.lastIndx],gm.depthArray[0:gm.lastIndx])
    print 'Time in simulTime: %.2f hrs'%(gm.t_prime-startT)
    print 'Final Lat-lon =%f,%f'%(gm.latFin[0], gm.lonFin[0])
    
    
            
if __name__ == "__main__":
    start=time.time()
    runSimulation((startLat,startLon),(goalLat,goalLon),startT,8.0,84)
    stop = time.time()
    print 'Time taken is : %.4f secs'%(stop-start)