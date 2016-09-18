import sys
sys.path.append('..')
from gpplib import *
from gpplib.GenGliderModelUsingRoms import GliderModel
from matplotlib import pyplot as plt
import numpy as np
import math, random
import time
import threading
import Queue

yy,mm,dd,numDays = 2011,5,2,2

queue = Queue.Queue()

class ThreadedSimulator(GliderModel,threading.Thread):
    def __init__(self,queue,shelfName='RiskMap.shelf',sfcst_directory='./',dMax=1.5):
        super(ThreadedSimulator,self).__init__(shelfName,sfcst_directory)
        threading.Thread.__init__(self)
        conf = GppConfig()
        plt.imshow(self.riskMapArray,origin='lower')
        self.gm = GliderModel(conf.myDataDir+'RiskMap.shelf',conf.myDataDir+'/roms/')
        self.u,self.v,self.time,self.depth,self.lat,self.lon = self.GetRomsData(yy,mm,dd,numDays) 
        self.FullSimulation, self.HoldValsOffMap=False,True
        self.queue = queue

    
    def run(self):
        for i in range(0,100):
            '''
            xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist=\
                gm.SimulateDive(gm.lat_pts[1]+random.gauss(0,0.1),gm.lon_pts[6]+random.gauss(0,0.1),gm.lat_pts[5],gm.lon_pts[1],80,u,v,lat,lon,depth,i,False)
            '''
            self.InitSim(self.lat_pts[1]+random.gauss(0,0.1),self.lon_pts[6]+random.gauss(0,0.1),self.lat_pts[5],self.lon_pts[1],80,i,self.FullSimulation,self.HoldValsOffMap)
            xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist=\
                self.SimulateDive_R(20)
            print 'Flag for Simulation Completion = ',self.doneSimulating
            #xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist=\
            #    gm.SimulateDive_R(True,10)
            #gm.SimulateDive(gm.lat_pts[1]+random.gauss(0,0.1),gm.lon_pts[6]+random.gauss(0,0.1),gm.lat_pts[5],gm.lon_pts[1],80,u,v,lat,lon,depth,i,False)
            if possibleCollision == False:
                        tempX,tempY = self.GetPxPyFromLatLon(np.array(latArray),np.array(lonArray))
                        x_sims,y_sims = tempX[-1:],tempY[-1:] # TODO: This might be wrong!
                        plt.plot(tempX,tempY)
            else:
                            
                tempX,tempY = self.GetPxPyFromLatLon(np.array(latArray),np.array(lonArray))
                plt.plot(tempX,tempY,'r.-')
                x_sims,y_sims = 0,0
        self.queue.task_done()
        
        
cpuThreads = [1,2,3,4]
            
if __name__ == "__main__":
    plt.figure()

    conf =GppConfig()
    start=time.time()
    for i in range(2):
        ts = ThreadedSimulator(queue,'RiskMap.shelf',conf.myDataDir+'/roms/')
        ts.setDaemon(True)
        queue.put(cpuThreads[i])
        ts.start()
    
queue.join()
    
stop = time.time()
print 'Time taken is : %.4f secs'%(stop-start)
