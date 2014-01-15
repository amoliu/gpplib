'''
This file creates a risk and obstacle map which will be used for all simulations.
It also requires gpp_in_cpp and a couple of files which contain bathymetric and risk information.
'''
#import UseAgg
import numpy as np
import scipy.io as sio
from scipy.ndimage import gaussian_filter
from scipy import ndimage
import matplotlib.pyplot as plt
import math
import shelve
import networkx as nx
import os
import gpplib
from gpplib.MapTools import *
from gpp_in_cpp import ImgMap
#from gpplib.gpp_in_cpp import ImgMapUtils
from gpp_in_cpp import ImgMapUtils


#rMapFN,bMapFN = conf.riskPgmMapDir+'SCB_risk_250.map',conf.riskPgmMapDir+'SCB_bathy_250.pgm'

figSaveDir = 'pngs'
riskMapName = 'RiskMap6.shelf'
riskPngName = 'SCB_Sbox3.png'
try:
    os.mkdir(figSaveDir)
except:
    pass

conf = gpplib.Utils.GppConfig()

newArray=ndimage.io.imread('../RiskMaps/%s'%(riskPngName),flatten=True)
newArray=newArray/255.
newArray=np.where(newArray>0.9,1,newArray)
# Add some risk all over....
newArray+= 0.01 * np.ones(newArray.shape)
newArray = np.where(newArray>0.9,1,newArray)


plt.imshow(newArray,origin='lower')
numPts = 20
n,s,e,w = 33.6, 33.25, -118.236, -118.8
map_res = 250. # 1px=250m
height,width = newArray.shape
#width, height = newArray.shape
hDiff,wDiff = (n-s)/numPts, (e-w)/numPts
lat_pts = np.linspace(s+hDiff/2,n-hDiff/4,numPts)
lon_pts = np.linspace(w+wDiff/2,e-wDiff/2,numPts)
y_pts = ((n-lat_pts))*(np.ones((1,numPts))*(height/(n-s)))[0]
x_pts = (lon_pts-w)*(np.ones((1,numPts))*(width/(e-w)))[0]
riskMap = np.zeros((numPts,numPts))
plt.colorbar()
mc = MapConversions(n,s,w,e,map_res)


class GraphFromVariableSizeGrid(object):
    ''' Here we are going to produce grids as a function 
        of the risk value at each sampled location. i.e. we will have
        a min-resolution and a max-resolution. We will choose the resolution
        of the grid in an area based upon how risky that area is '''
    def __init__(self,riskMapArray,n,s,e,w,numPts):
            self.n,self.s,self.e,self.w,self.numPts = n,s,e,w,numPts
            self.riskMapArray = riskMapArray
            self.height,self.width = riskMapArray.shape
            hDiff,wDiff = (n-s)/numPts, (e-w)/numPts
            self.hDiff, self.wDiff = hDiff, wDiff
            lat_pts = np.linspace(s+hDiff/2,n-hDiff/4,numPts)
            lon_pts = np.linspace(w+wDiff/2,e-wDiff/2,numPts)
            y_pts = ((n-lat_pts))*(np.ones((1,numPts))*(height/(n-s)))[0]
            x_pts = (lon_pts-w)*(np.ones((1,numPts))*(width/(e-w)))[0]
            
            
            self.hD,self.wD = float(self.height)/self.numPts,float(self.width)/self.numPts
            self.xL,self.xR = self.wD/2,self.wD/2 # How much from opposite sides is not used.
            self.yU,self.yD = self.hD/4,self.hD/2 # How much from north south is not used.
            self.deltaX = (self.width-(self.xL+self.xR))/float(self.numPts-1)
            self.deltaY = (self.height-(self.yU+self.yD))/float(self.numPts-1)
            
            self.lat_pts, self.lon_pts, self.x_pts, self.y_pts = lat_pts, lon_pts, x_pts, y_pts
        
            self.minGridRes, self.maxGridRes = 5, 10
            
            




class GraphFromMinRiskPatches(object):
    def __init__(self,riskMapArray,n,s,e,w,numPts):
        self.n,self.s,self.e,self.w,self.numPts = n,s,e,w,numPts
        self.riskMapArray = riskMapArray
        self.height,self.width = riskMapArray.shape
        hDiff,wDiff = (n-s)/numPts, (e-w)/numPts
        self.hDiff, self.wDiff = hDiff, wDiff
        
        lat_pts = np.linspace(s+hDiff/2,n-hDiff/4,numPts)
        lon_pts = np.linspace(w+wDiff/2,e-wDiff/2,numPts)
        y_pts = ((n-lat_pts))*(np.ones((1,numPts))*(height/(n-s)))[0]
        x_pts = (lon_pts-w)*(np.ones((1,numPts))*(width/(e-w)))[0]
        self.hD,self.wD = float(self.height)/self.numPts,float(self.width)/self.numPts
        self.xL,self.xR = self.wD/2,self.wD/2 # How much from opposite sides is not used.
        self.yU,self.yD = self.hD/4,self.hD/2 # How much from north south is not used.
        self.deltaX = (self.width-(self.xL+self.xR))/float(self.numPts-1)
        self.deltaY = (self.height-(self.yU+self.yD))/float(self.numPts-1)
        
        self.lat_pts, self.lon_pts, self.x_pts, self.y_pts = lat_pts, lon_pts, x_pts, y_pts
    
    
    def GetPatchRisk(self,x,y,r):
        # We're going to look around this location to compute the risk-score
        totRisk,totSum,avgRisk=0.,0.,0.
        height, width = self.riskMapArray.shape
        
        minX,minY,minRisk = x,y,float('inf')
        for j in range(y-r,y+r+1):
            if j>=0 and j<height:
                for i in range(x-r,x+r+1):
                    if i>=0 and i<width:
                        totRisk+=self.riskMapArray[j,i]
                        totSum+=1
        avgRisk = totRisk/totSum
        
        return avgRisk
    
    def LookForLowestRiskPatch(self,x,y,r):
        # Search for the location with the lowest avg. risk patch around location x,y
        # within radius r2 around it
        
        minX,minY,minRisk = x,y,float('inf')
        for j in range(int(y-r),int(y+r+1)):
            if j>=0 and j<self.height:
                for i in range(int(x-r),int(x+r+1)):
                    if i>=0 and i<self.width:
                        avgRisk=self.GetPatchRisk(i,j,r)
                        if avgRisk<minRisk:
                            minX,minY,minRisk = i,j,avgRisk
                            
        return minX, minY, minRisk
    
    
    def CreateGraphOfLowRiskPatches(self):
        self.riskMapX,self.riskMapY=np.zeros((self.numPts,self.numPts)),np.zeros((self.numPts,self.numPts))
        self.riskMapLat,self.riskMapLon=np.zeros((self.numPts,self.numPts)),np.zeros((self.numPts,self.numPts))
        self.riskMapValue = np.zeros((self.numPts,self.numPts))
        
        r = 2
        
        plt.imshow(self.riskMapArray)
        for j in range(0,self.numPts):
            for i in range(0,self.numPts):
                self.riskMapX[j,i],self.riskMapY[j,i],self.riskMapValue[j,i] = self.LookForLowestRiskPatch(self.x_pts[i],self.y_pts[j],r)
                self.riskMapLat[j,i],self.riskMapLon[j,i] = self.GetLatLonFromRmapXY(self.riskMapX[j,i],self.riskMapY[j,i])
                print 'Finding Min-risk location at %d,%d. This location is: %f,%f value=%f'%(i,j,self.riskMapX[j,i],self.riskMapY[j,i],self.riskMapValue[j,i])
                if self.riskMapValue[j,i]<0.5:
                    plt.plot(self.x_pts[i],self.y_pts[j],'k.')
                    plt.plot(self.riskMapX[j,i],self.riskMapY[j,i],'r.')
    
    
    def GetLatLonFromRmapXY(self,px,py):
        lon0, lat0 = self.w,self.s
        self.px2lon,self.py2lat = (self.e-self.w)/self.width,(self.n-self.s)/self.height
        #self.w/rMap.GetLonDiff(), self.h/rMap.GetLatDiff()
        return lat0+(py*self.py2lat),lon0+(px*self.px2lon)
        
    def GetRmapXYfromLatLon(self,lat,lon):
        x0,y0 = 0,0
        lon0,lat0 = self.w,self.s #rMap.GetOxDeg(),rMap.GetOyDeg()
        self.lon2x,self.lat2y = self.width/(self.e-self.w),self.height/(self.n-self.s)
        return x0+((lon-lon0)*self.lon2x),y0+((lat-lat0)*self.lat2y)
    
    def GetLatLonFromGraphXY(self,x,y):
        ''' Convert from PotentialMapXY co-ods to Lat-Lon.
        '''
        self.gx2lon, self.gy2lat = math.fabs(self.lon_pts[-1]-self.lon_pts[0])/(self.numPts-1.), \
                                    math.fabs(self.lat_pts[-1]-self.lat_pts[0])/(self.numPts-1.)
        return lat_pts[0]+(y*self.gy2lat), lon_pts[0]+(x*self.gx2lon)
       
    def GetGraphXYfromLatLon(self,lat,lon):
        self.lon2gx, self.lat2gy = (self.numPts-1.)/math.fabs(self.lon_pts[-1]-self.lon_pts[0]), \
                                (self.numPts-1.)/math.fabs(self.lat_pts[-1]-self.lat_pts[0])
        
        return self.x_pts[0]+lon*self.lon2gx, self.y_pts[0]+lat*self.lat2gy


def IsTooCloseToLand(x,y,R):
    # Are we closer to land than R? (where R is in pixels on the risk-map).
    
    height,width = newArray.shape
    for r in range(0,R):
        for j in range(-r,r+1):
            for i in range(-r,r+1):
                x1,y1 = math.floor(x+0.5)+i,math.floor(y+0.5)+j
                if x1<0:
                    x1=0
                if x1>=width-1:
                    x1 = width-1
                if y1<0:
                    y1=0
                if y1>=height-1:
                    y1 = height-1
                if newArray[y1,x1]>0.9:
                    return True
    return False

class LandProximity():
    ''' I am doing this all wrong - the best way to do this would be to use
    a logistic classifier with the map as test-data and fit a polynomial to it.
    I don't have the time to fix this right now though, so let us go with this.
    '''
    def __init__(self,riskMap,locMap,x_pts,y_pts, convVals):
        self.riskMap = riskMap.copy() #[::-1,:].copy()
        self.locMap  = locMap.copy() #[::-1,:].copy()
        self.height,self.width = riskMap.shape
        self.locH, self.locW = locMap.shape
        self.maxDist = max(self.height,self.width)
        self.x_pts,self.y_pts = x_pts,y_pts
        self.allNearests = {}
        self.g = nx.DiGraph()
        self.convVals = convVals
    
    def GetRangeToLand(self,x,y,R):
        ''' Find out how far away the nearest land mass is.
        Args:
            x,y (float) : x, y co-ods in risk-map image co-od system.
            R (float) : maximum distance to look for land in around (x,y)
            
        Returns:
            x1,y1,dist 
            x1,y1 (float): (x1,y1) - Location of neares land pixel
            dist (float): distance of (x1,y1) from (x,y)
        '''
        if self.riskMap[y,x]>0.9:
            return x,y,0.0
        
        for r in range(0,R):
            for j in range(-r,r+1):
                for i in range(-r,r+1):
                    x1,y1 = int(x+0.5+i),int(y+0.5+j)
                    if x1<0:
                        x1=0
                    if x1>=self.width-1:
                        x1 = self.width-1
                    if y1<0:
                        y1=0
                    if y1>=self.height-1:
                        y1 = self.height-1
                    if self.riskMap[y1,x1]>0.9:
                        return x1,y1,self.distInRiskPixToKm(math.sqrt((y-y1)**2+(x-x1)**2))
        return None, None, None

    def loc2riskXY(self,lx,ly):
        ''' Convert (lx,ly) from graph-coods to risk-map coods.
        Args:
            lx,ly (int): location coordinates
        
        Returns:
            rx,ry (float): risk-map pixel coordinates
        '''
        return self.x_pts[int(lx)],self.y_pts[int(ly)]
    
    def risk2locXY(self,rx,ry):
        ''' Convert (rx,ry) from risk-map coods to graph-coods.
        Args:
            rx,ry (float): risk-map pixel coordinates
        
        Returns:
            lx,ly (int): graph-map coordinates
        '''
        lx,ly = 0,0
        for i in range(0,len(self.x_pts)):
            if rx==math.floor(self.x_pts[i]+0.5):
                lx = i; break
        for j in range(0,len(self.y_pts)):
            if ry==math.floor(self.y_pts[j]+0.5):
                ly = j; break
        return lx,ly # Y-axis is in image coods.
    
    def riskXYtoLatLon(self,x,y):
        lat0deg,lon0deg,latDiffDeg,lonDiffDeg = \
            self.convVals['lat0deg'],self.convVals['lon0deg'], \
            self.convVals['latDiffDeg'],self.convVals['lonDiffDeg']
        return lat0deg+y*latDiffDeg, lon0deg+x*lonDiffDeg
    
    def distInRiskPixToKm(self,riskDist):
        return (self.convVals['px2m'] * riskDist)/1000.
    
    def distInKmToRiskPix(self,kmDist):
        return (kmDist*1000.)/self.convVals['px2m']
    
    
    def FindAllNearestLocations(self):
        ''' Find all the nearest locations by computing the range 
        '''
        for j in range(0,len(self.y_pts)):
            for i in range(0,len(self.x_pts)):
                lat,lon = self.riskXYtoLatLon(self.x_pts[i], self.y_pts[j])
                self.allNearests['(%d,%d)'%(i,j)] = (self.GetRangeToLand(self.x_pts[i], self.y_pts[j],self.maxDist ), lat, lon)
                print '(%d,%d) = %d,%d,%f'%(i,j,i,j,self.allNearests['(%d,%d)'%(i,j)][0][2])
                

    def CreateTransitionGraphOfLocsFarFromLand(self,howFarInKm):
        ''' Thresholds nodes away from land and creates a graph which is compatible
        with the Replanner and MDP with these.
        
        Args:
            howFarInKm (float): how far away the location should be in km from nearest land-mass
        
        Returns:
            graph g, containing all nodes which fulfill the criteria of being atleast 'howFarInKm' from land.
        '''
        self.howFarInKm = howFarInKm
        distIndx = 2
        for j in range(0,len(self.y_pts)):
            for i in range(0,len(self.x_pts)):
                if (self.allNearests['(%d,%d)'%(i,j)][0][distIndx]) >= howFarInKm:
                    print '(%d,%d)'%(i,j)
                    self.g.add_node('(%d,%d)'%(i,j))
        return self.g
        
    def PlotOurGraph(self):
        ''' Plot the locations of all the nodes in our graph. (We have only got nodes but no edges).
        '''
        plt.figure()
        plt.imshow(self.riskMap,origin='upper')
        import re
        for node in self.g.nodes():
            m1=re.match('\(([0-9]+),([0-9]+)\)',node)
            if m1:
                i1,j1 = int(m1.group(2)),int(m1.group(1))
                i2,j2 = self.loc2riskXY(j1, i1)
                plt.plot(i2,j2,'m^')
        #plt.title('Risk Map and transition graph node. Min dist to land = %.2f km'%(self.howFarInKm))
                
gfmrp = GraphFromMinRiskPatches(newArray,n,s,e,w,numPts)
gfmrp.CreateGraphOfLowRiskPatches()


np.set_printoptions(suppress=True,precision=2)
for j in range(0,numPts):
    for i in range(0,numPts):
        if IsTooCloseToLand(x_pts[i],y_pts[j],6):
            riskMap[j,i] = 1.
        else:
            riskMap[j,i] = newArray[math.floor(y_pts[j]+0.5),math.floor(x_pts[i]+0.5)]
        plt.plot(math.floor(x_pts[i]),math.floor(y_pts[j]),'k+')
plt.axis([0,width,height,0])
plt.savefig('%s/RiskmapOriginal.png'%(figSaveDir))

#import pdb; pdb.set_trace()
plt.figure()
plt.imshow(riskMap,origin='upper')
plt.colorbar()
plt.savefig('%s/Riskmap2ForPlanner.png'%(figSaveDir))

riskMapShelf = shelve.open(riskMapName)
riskMapShelf['riskMap'] = riskMap#[::-1,:]
riskMapShelf['riskMapArray'] = newArray#[::-1,:]
riskMapShelf['lat_pts'], riskMapShelf['lon_pts'] = lat_pts, lon_pts
riskMapShelf['x_pts'], riskMapShelf['y_pts'] = x_pts, y_pts
obsMap =  newArray #(1-bMapArray/255)
obsMap = np.where(obsMap>.9,1,0.)
riskMapShelf['obsMap'] = obsMap #[::-1,:]
riskMapShelf['lat0deg'],riskMapShelf['lon0deg'] = s,w # Origins
latDeg2m, lonDeg2m = mc.dc.GetDistBetweenLocs(n,w,s,w)/(n-s), mc.dc.GetDistBetweenLocs(n,w,n,e)/(e-w)
riskMapShelf['latDeg2m'],riskMapShelf['lonDeg2m'] = latDeg2m, lonDeg2m # convert degrees in lat/lon to m.
riskMapShelf['latDiffDeg'],riskMapShelf['lonDiffDeg']= n-s, e-w
riskMapShelf['px2m'],riskMapShelf['py2m'] = map_res, map_res
riskMapShelf['px2deg'],riskMapShelf['py2deg'] = (e-w)/width, (n-s)/height
#pMap = PotentialMap(numPts)
#pMap.FindMinEnergyLocations()
#LatLonLocs = pMap.PlotLatLonLocsOnMap()

# Convert Values is an important little dictionary of conversion values.

convVals = {}
convVals['lat0deg'],convVals['lon0deg'] = riskMapShelf['lat0deg'],riskMapShelf['lon0deg']
convVals['latDeg2m'],convVals['lonDeg2m'] = riskMapShelf['latDeg2m'],riskMapShelf['lonDeg2m']
convVals['latDiffDeg'],convVals['lonDiffDeg']= riskMapShelf['latDiffDeg'],riskMapShelf['lonDiffDeg']
convVals['px2m'],convVals['py2m'] = riskMapShelf['px2m'],riskMapShelf['py2m'] 
convVals['px2deg'],convVals['py2deg'] = riskMapShelf['px2deg'],riskMapShelf['py2deg']


howFarInKm = 1.5 
lp = LandProximity(newArray,riskMap,x_pts,y_pts,convVals)
lp.FindAllNearestLocations()
lp.CreateTransitionGraphOfLocsFarFromLand( howFarInKm )
lp.PlotOurGraph()
plt.savefig('%s/RiskMap2_ClosestLand_%.2fkm.png'%(figSaveDir,howFarInKm))
riskMapShelf['LandProxemics']= lp.allNearests
riskMapShelf['NodesInGraph'] = lp.g
#riskMapShelf['LatLonLocs'] = LatLonLocs
riskMapShelf['convVals'] = convVals
riskMapShelf.close()

overWriteRiskMapShelf = raw_input('Overwrite %s (Y/N)?'%(riskMapName))
if overWriteRiskMapShelf=='y' or overWriteRiskMapShelf=='Y':
    moveCmd= 'mv %s %s'%(riskMapName,conf.myDataDir)
    print moveCmd
    os.system(moveCmd)

from gpplib.KmlTools import *
from gpplib.Utils import *

kmzImageName= 'SCB_Box2.png'
kmlOverlay = GppKmlGroundOverlay()
SaveFigureAsImage('%s'%(kmzImageName),plt.gcf(),orig_size=newArray.shape)
kmlOverlay.CreateGroundOverlay('%s'%(kmzImageName),n,s,e,w)
kmlOverlay.SaveKmzFile('%s.kmz'%(kmzImageName))

