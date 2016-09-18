import numpy as np
import scipy.io as sio
import math
import shelve
from TriInterpolate import TriLinearInterpolate # This has our Trilinear interpolation
import os, re
from SfcstOpener import SfcstOpen

class ROMSvariability:
    def __init__(self,shelfName='RiskMap.shelf'):
        self.scale = 1              # 1 unit = 1 km
        self.latDegInM,self.lonDegInM,self.gVel = 110913.73, 92901.14,0.278
        self.gVelVar  = 0.1
        self.gDirVar  = 0.1
        self.numTrials = 24
        self.maxTimeSteps = 100.
        self.maxDepth = 60.
        self.TransModel={}
        self.Initialized = False
        self.InitFromRiskMapShelf(shelfName)
        self.sfcst_directory = '../../../matlab/'
        self.sfOpen = SfcstOpen()
        pass

    def GetRomsData(self,yy,mm,dd,numDays):
        daysInMonths = [31,28,31,30,31,30,31,31,30,31,30,31]
        if yy%4 == 0:
            daysInMonths[1] = 29
        #u,v,time,depth,lat,lon = self.OpenSfcstFile(self.sfcst_directory,yy,mm,dd)
        #import pdb; pdb.set_trace()
        u,v,time,depth,lat,lon = self.sfOpen.LoadFile('%s/sfcst_%04d%02d%02d.mat'%(self.sfcst_directory,yy,mm,dd))
        myDay, myMonth, myYear = dd,mm,yy
        for day in range(1,numDays):
            myDay = myDay+1
            if myDay>daysInMonths[mm-1]:
                myDay = 1
                myMonth = myMonth+1
                if myMonth>12:
                    myMonth = 1
                    myYear = myYear+1
            # TODO: Write a test for the file, so we can break if we cannot open the file.
            u1,v1,time1,depth1,lat1,lon1 = self.sfOpen.LoadFile('%s/sfcst_%04d%02d%02d.mat'%(self.sfcst_directory,myYear,myMonth,myDay))
            u,v=np.concatenate((u,u1),axis=0),np.concatenate((v,v1),axis=0)
            time1=time1+np.ones((24,1))*24*day
            time=np.concatenate((time,time1),axis=0)
        return u,v,time,depth,lat,lon
    
    def InitFromRiskMapShelf(self,shelfName):
        riskMapShelf = shelve.open(shelfName,writeback=False)
        self.riskMap = riskMapShelf['riskMap'][::-1,:]
        self.riskMapArray = riskMapShelf['riskMapArray']
        self.lat_pts, self.lon_pts = riskMapShelf['lat_pts'], riskMapShelf['lon_pts']
        self.x_pts, self.y_pts = riskMapShelf['x_pts'], riskMapShelf['y_pts']
        self.obsMap = riskMapShelf['obsMap'] 
        riskMapShelf.close()
        self.Width,self.Height = self.riskMap.shape
        self.Initialized = True
    
    def DoVariabilityAnalysis(self,u,v,time,depth,lat,lon,tInit,tFinal):
        '''
         Compute the variability between tInit and tFinal.
        '''
        maxDepthIndex = 11
        totalU, totalV = 0,0
        tMax,dMax,yMax,xMax = u.shape
        if tFinal>tMax:
            tFinal = tMax
        if tInit<0:
            tInit = 0
            
        S = np.zeros((yMax,xMax))
        Var = np.zeros((yMax,xMax))
        totU = np.zeros((yMax,xMax))
        totV = np.zeros((yMax,xMax))
        totalNum = 0.
        for t in range(tInit,tFinal):
            for d in range(0,maxDepthIndex):
                totU = totU + u[t,d]
                totV = totV + v[t,d]
                totalNum += 1.
        
        S = np.sqrt(np.multiply(totU,totU)+np.multiply(totV,totV))
        Var = S/totalNum
        return totU,totV,S,Var
        