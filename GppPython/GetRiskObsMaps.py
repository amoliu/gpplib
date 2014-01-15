'''
This file creates a risk and obstacle map which will be used for all simulations.
It also requires gpp_in_cpp and a couple of files which contain bathymetric and risk information.
'''
#import UseAgg
import numpy as np
import scipy.io as sio
from scipy.ndimage import gaussian_filter
from gpp_in_cpp import ImgMap
from gpp_in_cpp import ImgMapUtils
import matplotlib.pyplot as plt
import math
import shelve
import networkx as nx
import os
import gpplib

conf = gpplib.Utils.GppConfig()
rMapFN,bMapFN = conf.riskPgmMapDir+'SCB_risk_500.map',conf.riskPgmMapDir+'SCB_bathy_500.pgm'

figSaveDir = 'pngs'
try:
    os.mkdir(figSaveDir)
except:
    pass
#rMapFN,bMapFN = '../maps/SCB_risk_100.map','../pgms/SCB_bathy_100.pgm'
rMap = ImgMap.ImgMap(rMapFN)
bMap = ImgMap.ImgMap(bMapFN)
rMapUtil = ImgMapUtils.ImgMapUtil()
options={}
options['ReflectImage']=True
rMapUtil.ConvImgMapToDict(rMap,options)
bMapUtil = ImgMapUtils.ImgMapUtil()
bMapUtil.ConvImgMapToDict(bMap,options)

plt.figure()
bMapArray = bMapUtil.GetImage(bMap).transpose()
plt.imshow(bMapArray)
plt.savefig('%s/ObsmapOriginal.png'%(figSaveDir))

plt.figure()
sMap = ImgMap.ImgMap()
ScaleVal = 1000./4.
rMap.ScaleMapToPgm(sMap,0,ScaleVal)
sMapUtil = ImgMapUtils.ImgMapUtil()
sMapUtil.ConvImgMapToDict(sMap)
sMapArray = rMapUtil.GetImage(sMap).transpose()/ScaleVal
combMapArray = gaussian_filter((1-(bMapArray/255)) + sMapArray,5) +(1-(bMapArray/255)) + 0.1*np.ones(bMapArray.shape)
newArray = np.where(combMapArray>.9,1,combMapArray)
#gBlurArray = gaussian_filter(newArray,20)
plt.imshow(newArray,origin='upper')
numPts = 16
n,s,e,w = rMap.GetOyDeg()+rMap.GetLatDiff(), rMap.GetOyDeg(), rMap.GetOxDeg(), rMap.GetOxDeg()+rMap.GetLonDiff()
hDiff,wDiff = rMap.GetLatDiff()/(numPts), rMap.GetLonDiff()/(numPts)
lat_pts = np.linspace( rMap.GetOyDeg()+hDiff/2, rMap.GetOyDeg()+rMap.GetLatDiff()-hDiff/4, numPts )
lon_pts = np.linspace( rMap.GetOxDeg()+wDiff/2, rMap.GetOxDeg()+rMap.GetLonDiff()-wDiff/2, numPts )
y_pts = (lat_pts - rMap.GetOyDeg())*(np.ones((1,numPts))*(rMap.GetHeight()/rMap.GetLatDiff()))[0]
x_pts = (lon_pts - rMap.GetOxDeg())*(np.ones((1,numPts))*(rMap.GetWidth()/rMap.GetLonDiff()))[0]
riskMap = np.zeros((numPts,numPts))
plt.colorbar()

def IsTooCloseToLand(x,y,R):
    ''' Are we closer to land than R? (where R is in pixels on the risk-map).
    '''
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
        self.riskMap = riskMap[::-1,:].copy()
        self.locMap  = locMap[::-1,:].copy()
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
        plt.imshow(self.riskMap,origin='lower')
        import re
        for node in self.g.nodes():
            m1=re.match('\(([0-9]+),([0-9]+)\)',node)
            if m1:
                i1,j1 = int(m1.group(2)),int(m1.group(1))
                i2,j2 = self.loc2riskXY(i1, j1)
                plt.plot(j2,i2,'m^')
                plt.title('Risk Map and transition graph node. Min dist to land = %.2f km'%(self.howFarInKm))
                

class PotentialMap():
    ''' Potential Map to move the locations on the map around a little.
    '''
    def __init__(self,numPts):
        global newArray, rMap, riskMap
        self.numPts = numPts
        self.kAtt = 0.5
        self.kRep = 0.5
        pass
    
    def GetRepulsivePotentials(self):
        ''' For each location, compute the amount of risk around it by accumulating it and store that 
        within itself..
        '''
        self.repPotMap = np.zeros((numPts,self.numPts))
        self.h,self.w = newArray.shape
        self.hD,self.wD = float(self.h)/self.numPts,float(self.w)/self.numPts
        self.xL,self.xR = self.wD/2,self.wD/2 # How much from opposite sides is not used.
        self.yU,self.yD = self.hD/4,self.hD/2 # How much from north south is not used.
        self.deltaX = (self.w-(self.xL+self.xR))/float(self.numPts-1)
        self.deltaY = (self.h-(self.yU+self.yD))/float(self.numPts-1)
        self.repPotMap = riskMap
        return self.repPotMap
    
    def GetLatLonFromPotMapXY(self,x,y):
        ''' Convert from PotentialMapXY co-ods to Lat-Lon.
        '''
        x0,y0 = self.xL/self.deltaX,self.yD/self.deltaY
        #N,S,E,W = rMap.GetOyDeg()+rMap.GetLatDiff(), rMap.GetOyDeg(), rMap.GetOxDeg(), rMap.GetOxDeg()+rMap.GetLonDiff()
        self.x2lon,self.y2lat = rMap.GetLonDiff()/self.w, rMap.GetLatDiff()/self.h
        self.pX2lon,self.pY2lat = self.x2lon * self.deltaX, self.y2lat * self.deltaY
        return rMap.GetOyDeg()+(y0+y)*self.pY2lat,rMap.GetOxDeg()+(x0+x)*self.pX2lon
   
    def GetRmapXYfromLatLon(self,lat,lon):
       x0,y0 = 0,0
       lon0,lat0 = rMap.GetOxDeg(),rMap.GetOyDeg()
       self.lon2x,self.lat2y = self.w/rMap.GetLonDiff(), self.h/rMap.GetLatDiff()
       return x0+((lon-lon0)*self.lon2x),y0+((lat-lat0)*self.lat2y)
    
    def ComputePotential(self,x0,y0,x1,y1):
        '''
            Loop through all repulsive potential energy centers
            and compute the total repulsive force and resultant
            vector.
        '''
        fRepX,fRepY,fRepRes = 0.,0.,0.
        for y in range(0,numPts):
            for x in range(0,numPts):
                Rsqd = (x-x1)**2. + (y-y1)**2.
                R = math.sqrt(Rsqd)
                if Rsqd>0 and R<3.0:
                    repForce =  (self.kRep*self.repPotMap[y,x])/Rsqd
                    fRepX += -repForce*(x-x1)/R
                    fRepY += -repForce*(y-y1)/R
        fAttX = self.kAtt*(x1-x0)
        fAttY = self.kAtt*(y1-y0)
        
        fResX = fAttX+fRepX
        fResY = fAttY+fRepY
        
        return fResX,fResY
    
    '''
        Run through a few iterations of gradient descent to 
        find the positions where the grid is going to have
        the minimum potential energy.
    '''
    def FindMinEnergyLocations(self):
        plt.figure()
        repPotMap = self.GetRepulsivePotentials()
        plt.imshow(repPotMap,origin='upper')
        self.X,self.Y = np.zeros((self.numPts,self.numPts)),np.zeros((self.numPts,self.numPts))
        self.Xo,self.Yo = np.zeros((self.numPts,self.numPts)),np.zeros((self.numPts,self.numPts))
        self.LatLonLocs = {}
        # Start with all locations where they are...
        for j in range(0,self.numPts):
            for i in range(0,self.numPts):
                self.X[i,j],self.Y[i,j] = float(i),float(j)
                self.Xo[i,j],self.Yo[i,j] = float(i),float(j)
                plt.plot(self.X[i,j],self.Y[i,j],'k.')
        plt.xlim(-0.5,self.numPts-0.5)
        plt.ylim(self.numPts-0.5,-0.5)
        plt.title('Regular Grid.')
        plt.savefig('%s/RegularGrid.png'%(figSaveDir))
        # We want to compute the potentials and move in the direction of the resultants by
        # a small step.
        self.alpha = 0.5
        maxSteps = 1
        for k in range(0,maxSteps):
            plt.figure()
            plt.imshow(repPotMap,origin='upper')
            for j in range(0,self.numPts):
                for i in range(0,self.numPts):
                    if repPotMap[j,i]<0.6:
                        fX,fY = self.ComputePotential(self.Xo[i,j],self.Yo[i,j],self.X[i,j],self.Y[i,j])
                        #print fX,fY
                        self.X[i,j]+=fX*self.alpha; self.Y[i,j]+=fY*self.alpha
                        lat,lon = self.GetLatLonFromPotMapXY(self.X[i,j], self.Y[i,j])
                        tx,ty = self.GetRmapXYfromLatLon(lat, lon)
                        if not IsTooCloseToLand(tx,ty,2):
                            self.LatLonLocs['L(%d,%d)'%(i,j)] = lat,lon
                            plt.plot(self.Xo[i,j],self.Yo[i,j],'k.')
                            plt.plot(self.X[i,j],self.Y[i,j],'ms')
                            self.LatLonLocs['O(%d,%d)'%(i,j)]= (self.Xo[i,j],self.Yo[i,j])
                            self.LatLonLocs['P(%d,%d)'%(i,j)]= (self.X[i,j],self.Y[i,j])
                            print '(%d,%d)=%.4f,%.4f'%(i,j,lat,lon)
        plt.xlim(-0.5,self.numPts-0.5)
        plt.ylim(self.numPts+0.5,-0.5)
        plt.title('Grid after application of Potential Field')
        plt.savefig('%s/GridAfterPotField.png'%(figSaveDir))
        return self.LatLonLocs
    
    def PlotLatLonLocsOnMap(self):
        plt.figure()
        plt.imshow(newArray,origin='upper')
        for j in range(0,self.numPts):
            for i in range(0,self.numPts):
                if self.LatLonLocs.has_key('L(%d,%d)'%(i,j)):
                    lat,lon = self.LatLonLocs['L(%d,%d)'%(i,j)]
                    x,y = self.GetRmapXYfromLatLon(lat,lon)
                    plt.plot(x,y,'k^')
        plt.title('Locations overlaid on original risk-map')
        plt.xlim(-0.5,self.w)
        plt.ylim(self.h+10,-0.5)
        plt.savefig('%s/IrregularGridAfterPotField.png'%(figSaveDir))


np.set_printoptions(suppress=True,precision=2)
for j in range(0,numPts):
    for i in range(0,numPts):
        if IsTooCloseToLand(x_pts[i],y_pts[j],6):
            riskMap[j,i] = 1.
        else:
            riskMap[j,i] = newArray[math.floor(y_pts[j]+0.5),math.floor(x_pts[i]+0.5)]
        plt.plot(math.floor(x_pts[i]),math.floor(y_pts[j]),'k+')
plt.axis([0,rMap.GetWidth(),rMap.GetHeight(),0])
plt.savefig('%s/RiskmapOriginal.png'%(figSaveDir))

#import pdb; pdb.set_trace()
plt.figure()
plt.imshow(riskMap,origin='upper')
plt.colorbar()
plt.savefig('%s/RiskmapForPlanner.png'%(figSaveDir))

riskMapShelf = shelve.open('RiskMap.shelf')
riskMapShelf['riskMap'] = riskMap
riskMapShelf['riskMapArray'] = newArray
riskMapShelf['lat_pts'], riskMapShelf['lon_pts'] = lat_pts, lon_pts
riskMapShelf['x_pts'], riskMapShelf['y_pts'] = x_pts, y_pts
obsMap =  (1-bMapArray/255)
obsMap = np.where(obsMap>.9,1,obsMap)
riskMapShelf['obsMap'] = obsMap
riskMapShelf['lat0deg'],riskMapShelf['lon0deg'] = rMap.GetOyDeg(),rMap.GetOxDeg() # Origins
riskMapShelf['latDeg2m'],riskMapShelf['lonDeg2m'] = rMap.GetLatDeg(), rMap.GetLonDeg() # convert degrees in lat/lon to m.
riskMapShelf['latDiffDeg'],riskMapShelf['lonDiffDeg']= rMap.GetLatDiff(), rMap.GetLonDiff()
riskMapShelf['px2m'],riskMapShelf['py2m'] = rMap.GetLonDeg()/rMap.GetWidth()*rMap.GetLonDiff(), \
                                            rMap.GetLatDeg()/rMap.GetHeight()*rMap.GetLatDiff()
riskMapShelf['px2deg'],riskMapShelf['py2deg'] = rMap.GetLonDiff()/rMap.GetWidth(), rMap.GetLatDiff()/rMap.GetHeight()
pMap = PotentialMap(numPts)
pMap.FindMinEnergyLocations()
LatLonLocs = pMap.PlotLatLonLocsOnMap()

''' Convert Values is an important little dictionary of conversion values.
'''
convVals = {}
convVals['lat0deg'],convVals['lon0deg'] = riskMapShelf['lat0deg'],riskMapShelf['lon0deg']
convVals['latDeg2m'],convVals['lonDeg2m'] = riskMapShelf['latDeg2m'],riskMapShelf['lonDeg2m']
convVals['latDiffDeg'],convVals['lonDiffDeg']= riskMapShelf['latDiffDeg'],riskMapShelf['lonDiffDeg']
convVals['px2m'],convVals['py2m'] = riskMapShelf['px2m'],riskMapShelf['py2m'] 
convVals['px2deg'],convVals['py2deg'] = riskMapShelf['px2deg'],riskMapShelf['py2deg']

howFarInKm = 5 
lp = LandProximity(newArray,riskMap,x_pts,y_pts,convVals)
lp.FindAllNearestLocations()
lp.CreateTransitionGraphOfLocsFarFromLand( howFarInKm )
lp.PlotOurGraph()
plt.savefig('%s/RiskMap_ClosestLand_%.2fkm.png'%(figSaveDir,howFarInKm))
riskMapShelf['LandProxemics']= lp.allNearests
riskMapShelf['NodesInGraph'] = lp.g
riskMapShelf['LatLonLocs'] = LatLonLocs
riskMapShelf['convVals'] = convVals
riskMapShelf.close()



