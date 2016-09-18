''' Simulation of communication goodness
'''
import os
import scipy.io as sio
import matplotlib.pyplot as plt
import numpy as np
import math
import shelve
import gpplib
from gpp_in_cpp import ImgMap
from gpp_in_cpp import ImgMapUtils

from MapTools import *
from LatLonZ import *






class BaseStationLineOfSightTester(object):
    ''' A class that has methods to test for line-of-sight between two antennae assuming a spherical model of
    the world.
    '''
    def __init__(self,bs_lat,bs_lon,):
        # Load up the llz file
        result = np.load('SCB_CST.npy')
        lon, lat, Z = result[:, 0], result[:, 1], result[:, 2]
        self.llz = LatLonZ(lat,lon,Z)
        lat, lon, Z = self.llz.FilterLatLonZ_ValuesBetweenLatLonValues()
        
        self.bs_lat, self.bs_lon  = bs_lat, bs_lon
        self.nim = NewImageMap()
        self.nim.LoadImageFromMat('scb_bin_bathy_500.mat')
        plt.figure()
        plt.imshow(self.nim.ImgDict['ImgArray'])
        latN,latS,lonW,lonE,map_res = self.nim.GetImageInfo()
        self.mc = MapConversions(latN,latS,lonW,lonE,map_res)
        self.bs_x,self.bs_y = self.mc.getPxPyFromLatLon(self.bs_lat,self.bs_lon)
        plt.plot(self.bs_x,self.bs_y,'k.')
        self.bs_ha = self.llz.getNearestZforLatLon(self.bs_lat,self.bs_lon)
        print 'Height of Nearest location in LLZ map to Catalina base station is :%f'%(self.bs_ha)
        
        self.bs_ha2 = self.llz.getLinInterpZforLatLon(self.bs_lat,self.bs_lon)
        print 'Height of Lin-Interpolated location in LLZ map to Catalina base station is: %f'%(self.bs_ha2)
        
    
    
    def GetHeightProfileBetweenGliderAndBaseStation(self,gl_Lat,gl_Lon):
        ''' Get the height profile along the great-circle joining the glider and the base-station.
        '''
        numPts = 100
        htVals = np.zeros((numPts,1))
        intPts = np.linspace(0,1,numPts)
        for i,iPt in enumerate(intPts):
            iLat,iLon = self.mc.dc.GetIntermediatePtOnGreatCircle(self.bs_lat,self.bs_lon,gl_Lat,gl_Lon,iPt)
            iLat,iLon = self.mc.dc.RadToDeg(iLat),self.mc.dc.RadToDeg(iLon)
            print iLat,iLon
            htVals[i] = self.llz.getLinInterpZforLatLon(iLat,iLon)

        plt.figure()
        plt.plot(intPts,htVals)
        
        
    
    

    
        
        
bslst = BaseStationLineOfSightTester(33.445,-118.4777)
#BaseStationLineOfSightTester(33.447277,-118.477860)

bslst.GetHeightProfileBetweenGliderAndBaseStation(33.36, -118.5979)

dummySt = BaseStationLineOfSightTester( 33.471811, -118.596854 )
gl_Lat,gl_Lon = ( 33.264350, -118.271724 )
dummySt.GetHeightProfileBetweenGliderAndBaseStation(gl_Lat, gl_Lon)
        
        






