#import UseAgg
import math
import shelve
import numpy as np
import os
from scipy.ndimage import gaussian_filter
import scipy.io as sio
import networkx as nx
from matplotlib import pyplot as plt
from gpp_in_cpp.ImgMapUtils import ImgMapUtil as imu
from gpp_in_cpp.ImgMap import ImgMap as im
import gpplib
from gpplib.Utils import GppConfig
from gpplib.MapTools import *
import pylab

def SaveFigureAsImage(fileName,fig=None,**kwargs):
    ''' Save a Matplotlib figure as an image without borders or frames.
       Args:
            fileName (str): String that ends in .png etc.

            fig (Matplotlib figure instance): figure you want to save as the image
        Keyword Args:
            orig_size (tuple): width, height of the original image used to maintain 
            aspect ratio.
    '''
    fig.patch.set_alpha(0)
    if kwargs.has_key('orig_size'): # Aspect ratio scaling if required
        w,h = kwargs['orig_size']
        fig_size = fig.get_size_inches()
        w2,h2 = fig_size[0],fig_size[1]
        fig.set_size_inches([(w2/w)*w,(w2/w)*h])
        fig.set_dpi((w2/w)*fig.get_dpi())
        plt.xlim(0,h); plt.ylim(w,0)
    a=fig.gca()
    a.set_frame_on(False)
    a.set_xticks([]); a.set_yticks([])
    plt.axis('off')
    fig.savefig(fileName, transparent=True, bbox_inches='tight', \
        pad_inches=0)


figSaveDir = 'pngs'
riskMapName = 'RiskMap7.shelf'
riskPngName = 'SCB_Apr13.png'
try:
    os.mkdir(figSaveDir)
except:
    pass

maxRiskVal = 250.

conf = gpplib.Utils.GppConfig()
im1=im(conf.myDataDir+'riskMaps/SCB_risk_250.map')
im2=im(conf.myDataDir+'riskMaps/SCB_bathy_250.pgm')
imUtil = imu()
npImg = imUtil.ReflectImage(im1)
bathyImg = imUtil.ReflectImage(im2)
bathyArray = (1-bathyImg/255.)

newArray = np.where(npImg>maxRiskVal,maxRiskVal,npImg)
newArray = newArray/maxRiskVal
newArray = gaussian_filter(newArray,1)
newArray = (newArray + bathyArray)
newArray = np.where(newArray>0.65,1,newArray)
newArray+= 0.01 * np.ones(newArray.shape)
newArray = np.where(newArray>0.75,1,newArray)

plt.imshow(newArray, origin='upper')
fig = plt.figure(1)
SaveFigureAsImage('../RiskMaps/%s'%(riskPngName),fig)
n,s,e,w = 34.1333333, 33.25, -117.7, -118.8

# Now for the region we are interested in...
n2, s2, e2, w2 = 33.68, 33.56, -118.33, -118.64


#n,s,e,w = 33.6, 33.25, -118.236, -118.8
#n, s, e, w = 33.76, 33.43, -118.32, -118.64
map_res = 250.
height,width = newArray.shape

vertRatio = (n-s)/(n2-s2)
horzRatio = (e-w)/(e2-w2)
y2lat,x2lon = (n-s)/250., (e-w)/250.
#x0,y0 = (w-w2)/x2lon, (n-n2)/y2lat

x0,y0 = 0, (n-n2)/y2lat

numPts = 20
hDiff, wDiff = (n2-s2)/numPts, (e2-w2)/numPts
lat_pts = np.linspace(s2+hDiff/2,n2-hDiff/2,numPts)
lon_pts = np.linspace(w2+wDiff/2,e2-wDiff/2,numPts)
y_pts = (y0+((lat_pts-s2))*(np.ones((1,numPts))*((height/vertRatio)/(n2-s2))))[0]
x_pts = (x0+(lon_pts-w2)*(np.ones((1,numPts))*((width/horzRatio)/(e2-w2))))[0]
riskMap = np.zeros((numPts,numPts))
plt.colorbar()
mc = MapConversions(n,s,w,e,map_res)

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
    
    def GetRangeToLand(self,x,y,R,bBox):
        ''' Find out how far away the nearest land mass is.
        Args:
            x,y (float) : x, y co-ods in risk-map image co-od system.
            R (float) : maximum distance to look for land in around (x,y)
            bBox (4-tuple) : n, s, e, w (north, south, east and west) within which range search is done
            
        Returns:
            x1,y1,dist 
            x1,y1 (float): (x1,y1) - Location of neares land pixel
            dist (float): distance of (x1,y1) from (x,y)
        '''
        if self.riskMap[y,x]>0.9:
            return x,y,0.0
        
        n,s,e,w = bBox
        
        lat,lon=self.riskXYtoLatLon(x, y)
        if lat<=n and lat>=s and lon<=e and lon>=w:
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
        else:
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
        lat0deg,lon0deg,py2Deg,px2Deg = \
            self.convVals['lat0deg'],self.convVals['lon0deg'], \
            self.convVals['py2deg'],self.convVals['px2deg']
        return lat0deg+y*py2Deg, lon0deg+x*px2Deg
    
    def latLonToRiskXY(self,lat,lon):
        lat0deg, lon0deg, py2Deg, px2Deg = \
            self.convVals['lat0deg'],self.convVals['lon0deg'], \
            self.convVals['py2deg'],self.convVals['px2deg']
        return (lon-lon0deg)/px2Deg, (lat-lat0deg)/py2Deg
    
    
    def distInRiskPixToKm(self,riskDist):
        return (self.convVals['px2m'] * riskDist)/1000.
    
    def distInKmToRiskPix(self,kmDist):
        return (kmDist*1000.)/self.convVals['px2m']
    
    
    def FindAllNearestLocations(self,bBox):
        ''' Find all the nearest locations by computing the range 
        '''
        for j in range(0,len(self.y_pts)):
            for i in range(0,len(self.x_pts)):
                lat,lon = self.riskXYtoLatLon(self.x_pts[i], self.y_pts[j])
                dist = (self.GetRangeToLand(self.x_pts[i], self.y_pts[j],self.maxDist, bBox ), lat, lon)
                self.allNearests['(%d,%d)'%(i,j)] = dist
                if dist[0][2]!=None:
                    print '(%d,%d) = %d,%d,%f'%(i,j,i,j,self.allNearests['(%d,%d)'%(i,j)][0][2])
                else:
                    print 'ignored.'

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
                if self.allNearests.has_key('(%d,%d)'%(i,j)):
                    if (self.allNearests['(%d,%d)'%(i,j)][0][distIndx]) >= howFarInKm:
                        print '(%d,%d)'%(i,j)
                        self.g.add_node('(%d,%d)'%(i,j))
        return self.g
    
    def FilterXYusingLatLon(self,n,s,e,w):
        ''' Remove locations whose lat/lon does not fall within bounds 
        '''
        import re
        for node in self.g.nodes():
            m1=re.match('\(([0-9]+),([0-9]+)\)',node)
            if m1:
                i,j = int(m1.group(1)),int(m1.group(2))
                lat,lon = self.riskXYtoLatLon(self.x_pts[i],self.y_pts[j])
                print '(%d,%d) = (%.4f,%.4f)'%(i,j,lat,lon)    
                if( lat>n or lat<s or lon<w or lon>e ):
                        self.g.remove_node('(%d,%d)'%(i,j))
                        print 'Removed Node (%d,%d)'%(i,j)
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
                i,j = int(m1.group(1)),int(m1.group(2))
                plt.plot(self.x_pts[i],height-self.y_pts[j],'m^')
                #i2,j2 = self.loc2riskXY(j1, i1)
                #plt.plot(i2,j2,'m^')
        #plt.title('Risk Map and transition graph node. Min dist to land = %.2f km'%(self.howFarInKm))
                
#gfmrp = GraphFromMinRiskPatches(newArray,n,s,e,w,numPts)
#gfmrp.CreateGraphOfLowRiskPatches()

np.set_printoptions(suppress=True,precision=2)
for j in range(0,numPts):
    for i in range(0,numPts):
        if IsTooCloseToLand(x_pts[i],y_pts[j],6):
            riskMap[j,i] = 1.
        else:
            riskMap[j,i] = newArray[math.floor(y_pts[j]+0.5),math.floor(x_pts[i]+0.5)]
        plt.plot(math.floor(x_pts[i]),math.floor(y_pts[j]),'k+')
plt.axis([0,width,height,0])
plt.savefig('%s/Riskmap7Original.png'%(figSaveDir))

#import pdb; pdb.set_trace()
plt.figure()
plt.imshow(riskMap,origin='upper')
plt.colorbar()
plt.savefig('%s/Riskmap7ForPlanner.png'%(figSaveDir))

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
#n2, s2, e2, w2 = 33.76, 33.43, -118.32, -118.64

lp = LandProximity(newArray,riskMap,x_pts,y_pts,convVals)
lp.FindAllNearestLocations((n2,s2,e2,w2))
lp.CreateTransitionGraphOfLocsFarFromLand( howFarInKm )
lp.PlotOurGraph()
plt.savefig('%s/RiskMap7_ClosestLand_%.2fkm_a.png'%(figSaveDir,howFarInKm))
#lp.FilterXYusingLatLon(n2, s2, e2, w2)
lp.PlotOurGraph()
plt.savefig('%s/RiskMap7_ClosestLand_%.2fkm_b.png'%(figSaveDir,howFarInKm))
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

kmzImageName= 'SCB_Apr13.png'
kmlOverlay = GppKmlGroundOverlay()
SaveFigureAsImage('%s'%(kmzImageName),plt.gcf(),orig_size=newArray.shape)
kmlOverlay.CreateGroundOverlay('%s'%(kmzImageName),n,s,e,w)
kmlOverlay.SaveKmzFile('%s.kmz'%(kmzImageName))
