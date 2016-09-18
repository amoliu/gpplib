import sys
sys.path.append('..')
from gpplib import *
from gpplib.GenGliderModelUsingRoms import GliderModel
from matplotlib import pyplot as plt
import numpy as np
import math, random
import time
from multiprocessing import Process, Queue, current_process, freeze_support

yy,mm,dd,numDays = 2011,5,2,2

queue = Queue()

def MultiProcessedSimulator(queue):
    conf = GppConfig()
    gm = GliderModel(conf.myDataDir+'RiskMap.shelf',conf.myDataDir+'/roms/')
    u,v,time,depth,lat,lon = gm.GetRomsData(yy,mm,dd,numDays) 
    
    simRuns = []
    FullSimulation,HoldValsOffMap=False,True
    for i in range(0,50):
        '''
        xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist=\
            gm.SimulateDive(gm.lat_pts[1]+random.gauss(0,0.1),gm.lon_pts[6]+random.gauss(0,0.1),gm.lat_pts[5],gm.lon_pts[1],80,u,v,lat,lon,depth,i,False)
        '''
        gm.InitSim(gm.lat_pts[1]+random.gauss(0,0.1),gm.lon_pts[6]+random.gauss(0,0.1),gm.lat_pts[5],gm.lon_pts[1],80,i,FullSimulation,HoldValsOffMap)
        xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist=\
            gm.SimulateDive_R(20)
        print 'Flag for Simulation Completion = ',gm.doneSimulating
        tempX,tempY=None,None
        #xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist=\
        #    gm.SimulateDive_R(True,10)
        #gm.SimulateDive(gm.lat_pts[1]+random.gauss(0,0.1),gm.lon_pts[6]+random.gauss(0,0.1),gm.lat_pts[5],gm.lon_pts[1],80,u,v,lat,lon,depth,i,False)
        if possibleCollision == False:
                    tempX,tempY = gm.GetPxPyFromLatLon(np.array(latArray),np.array(lonArray))
                    x_sims,y_sims = tempX[-1:],tempY[-1:] # TODO: This might be wrong!
                    #plt.plot(tempX,tempY)
        else:
                        
            tempX,tempY = gm.GetPxPyFromLatLon(np.array(latArray),np.array(lonArray))
            #plt.plot(tempX,tempY,'r.-')
            x_sims,y_sims = 0,0    
        simRuns.append((tempX,tempY,possibleCollision))
    queue.put(simRuns)
    
cpuThreads = []
freeze_support() 
if __name__ == "__main__":
    plt.figure()
    conf = GppConfig()
    gm = GliderModel(conf.myDataDir+'RiskMap.shelf',conf.myDataDir+'/roms/')
    plt.imshow(gm.riskMapArray,origin='lower')
    start=time.time()
    for i in range(4):
        p=Process(target=MultiProcessedSimulator, args=(queue,))
        p.start()
        cpuThreads.append(p)
    
x=cpuThreads.pop()
x.join(45)

sim= queue.get()
for x,y,posCol in sim:
    if posCol:
        plt.plot(x,y,'r.-')
    else:
        plt.plot(x,y)
    
stop = time.time()
print 'Time taken is : %.4f secs'%(stop-start)
