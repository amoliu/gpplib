''' Here, we are going to take a data file from  http://www.ngdc.noaa.gov/mgg/gdas/gd_designagrid.html

Specifically, the grid data that I am using here was created 
35 (north), 31 (south), -121 W (west), -117 W (east) at a 3 second resolution. (which is really high!).

In this file, we are going to create a raster map of this by re-projecting this back into an image.

This is a very good resource for simple formulae: http://williams.best.vwh.net/avform.htm#Dist


'''
import numpy as np
import scipy.io as sio
from scipy.ndimage import gaussian_filter
import math
import matplotlib.pyplot as plt
import csv
import gpplib
import Interp
import unittest
#from scipy import spatial


class EarthRadius(object):
    def __init__(self,lat):
        a = 6378e3    # Equitorial radius
        e = 0.081082  # Earth's eccentricity
        b = 6357e3    # Earth's polar radius
        
        e = math.sqrt( 1-b**2/a**2)
        den = (1-(e**2)*(math.sin(lat))**2)
        if lat<-90 or lat>90:
            raise ValueError
        self.lat = lat
        self.R = a*(1-e**2)/den
        self.N = a/math.sqrt(den)
        print 'The Earth\'s radius at %.4f degree latitude is %.8f m'%(lat,self.R)
        
class DistCalculator(object):
    ''' A simple distance calculator object.
    '''
    def __init__(self, R):
        #er = EarthRadius(lat)
        self.radius_m = R
        self.radius_km = R/1000.
    
    def GetDistBetweenLocsInRadians(self,lat1,lon1,lat2,lon2):
        ''' Here lat1,lon1, lat2, lon2 are in radians. 
            (Always convert degrees to rad before calling this)
        '''
        distance_radians = 2*np.arcsin(np.sqrt((np.sin((lat1-lat2)/2.)**2 + \
                    np.cos(lat1)*np.cos(lat2)*np.sin((lon1-lon2)/2.)**2)))
        return distance_radians
        
    def GetDistBetweenLocs(self,lat1,lon1, lat2, lon2):
        ''' GetDistBetweenLocs in meters
            Args:
                lat1, lon1, lat2, lon2 (all in degrees)
            d=2*asin(sqrt((sin((lat1-lat2)/2))^2 + 
                     cos(lat1)*cos(lat2)*(sin((lon1-lon2)/2))^2))
        '''
        lat1,lon1 = self.DegToRad(lat1),self.DegToRad(lon1)
        lat2,lon2 = self.DegToRad(lat2),self.DegToRad(lon2)
        
        distance_radians = self.GetDistBetweenLocsInRadians(lat1, lon1, lat2, lon2)
        distance_m = self.radius_m * distance_radians
        return distance_m
    
    def NpDegToRad(self,deg):
        return (np.pi*np.ones(deg.shape))/180.
    
    def NpRadToDeg(self,rad):
        return (180.*np.ones(rad.shape))/np.pi
    
    def DegToRad(self,deg):
        return (math.pi*deg)/180.
    
    def RadToDeg(self,rad):
        return (180.*rad)/math.pi
        
    def MeterToNauticalMile(self,m):
         return m/1852.
     
    def NauticalMileToMeter(nm):
        return nm*1852.
    
    def GetIntermediatePtOnGreatCircle(self,lat1,lon1,lat2,lon2,frac):
        ''' Gets an intermediate point between (lat1,lon1) and (lat2,lon2)
            a fraction f away from (lat1,lon1) f=0 is pt1. f=1 is pt2.
        '''
        lat1,lon1 = self.DegToRad(lat1),self.DegToRad(lon1)
        lat2,lon2 = self.DegToRad(lat2),self.DegToRad(lon2)
        
        d = 2*math.asin(math.sqrt(math.sin((lat1-lat2)/2.)**2 + \
                        math.cos(lat1)**2.  \
                        *math.sin((lon1-lon2)/2.)**2))
        A=math.sin((1-frac)*d)/math.sin(d)
        B=math.sin(frac*d)/math.sin(d)
        x = A*math.cos(lat1)*math.cos(lon1) + B*math.cos(lat2)*math.cos(lon2)
        y = A*math.cos(lat1)*math.sin(lon1) + B*math.cos(lat2)*math.sin(lon2)
        z = A*math.sin(lat1) +B*math.sin(lat2)
        
        lat = math.atan2(z,math.sqrt(x**2+y**2))
        lon = math.atan2(y,x)
        
        return lat,lon
        
        

class MapConversions(object):
    def __init__(self,latN=33.25,latS=32.00,lonW=-119.0,lonE=-117.7, map_res=100.):
        self.latN, self.latS, self.lonW, self.lonE = latN, latS, lonW, lonE
        self.map_res = map_res
        self.er = EarthRadius((latN+latS)/2.)
        self.dc = DistCalculator(self.er.R)
        #Test_DistanceCalculator()
        midLat = (latN+latS)/2.
        midLon = (lonE+lonW)/2.
        horzDist = self.dc.GetDistBetweenLocs(midLat,lonW,midLat,lonE)
        vertDist = self.dc.GetDistBetweenLocs(latN,midLon,latS,midLon)
        
        # Compute number of pixels to get a resolution of map_res horizontally
        self.pxWidth = math.floor(horzDist/map_res+0.5)
        self.pxHeight = math.floor(vertDist/map_res+0.5)
        
        self.lon0, self.lat0 = lonW, latN
        self.px2lat = math.fabs((self.latN-self.latS)/(vertDist/map_res))
        self.px2lon = math.fabs((self.lonW-self.lonE)/(horzDist/map_res))
        self.lat2px = 1./self.px2lat
        self.lon2px = 1./self.px2lon
        
                
    def getLatLonFromPxPy(self,x,y):
        lon = (x-0.5)*self.px2lon + self.lon0
        lat = self.lat0-y*self.px2lat
        return lat,lon

    def getPxPyFromLatLon(self,lat,lon):
        px = (lon-self.lon0)*self.lon2px# - 0.5
        py = (self.lat0-lat)*self.lat2px# - 0.5
        return px,py
    
class NewImageMap(object):
    ''' New image map class which stores data into .mat format
    '''
    def __init__(self,ImgDict={}): # ,imgArray,latN,latS,lonW,lonE,map_res
        self.ImgDict = ImgDict
        #self.InitWithImage(imgArray, latN, latS, lonW,lonE, map_res)
    
    ''' Use @classmethod decorator to support multiple initializations.
    '''
    @classmethod
    def InitWithImage(cls,imgArray,latN,latS,lonW,lonE,map_res):
        ''' InitWithImage is a class method which returns an instance
            of the class which has been initialized with the data.
        '''
        mc = MapConversions(latN,latS,lonW,lonE,map_res)
        er = EarthRadius((latN+latS)/2.)
        dc = DistCalculator(er.R)
        
        pxWidth,pxHeight = mc.pxWidth, mc.pxHeight
        ImgDict={}
        ImgDict['ImgArray'] = imgArray
        ImgDict['Width'] = pxWidth
        ImgDict['Height'] = pxHeight
        ImgDict['lat0deg'] = latN
        ImgDict['lon0deg'] = lonW
        ImgDict['latDiffDeg'] = latN-latS
        ImgDict['lonDiffDeg'] = lonW-lonE
        ImgDict['px2m'] = map_res
        ImgDict['py2m'] = map_res
        
        return cls(ImgDict)
        
    def SaveImageToMat(self,matFileName=None):
        if matFileName!=None:
            sio.savemat(matFileName,self.ImgDict)
            
    def LoadImageFromMat(self,matFileName=None):
        if matFileName!=None:
            self.ImgDict = sio.loadmat(matFileName)
            
    def GetImageInfo(self):
        #latN=33.25,latS=32.00,lonW=-119.0,lonE=-117.7, map_res=100
        latN = self.ImgDict['lat0deg']; latS = latN-self.ImgDict['latDiffDeg']
        lonW = self.ImgDict['lon0deg']; lonE = lonW-self.ImgDict['lonDiffDeg']
        map_res = self.ImgDict['px2m']
        return latN,latS,lonW,lonE,map_res