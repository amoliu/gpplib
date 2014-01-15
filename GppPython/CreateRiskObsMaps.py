''' @author: Arvind A de Menezes Pereira
    @summary: Create Risk and Obstacle Maps from AIS and Bathymetric data.
    
    New additions : We're going to be using Kd-trees from FLANN to do super fast nearest-neighbor lookups.
'''
import math
import shelve
import gpplib
import os
import numpy as np
import networkx as nx
import scipy.io as sio
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

from gpp_in_cpp import ImgMap
from gpp_in_cpp import ImgMapUtils

''' Load Maps '''
class LoadRiskMaps(object):
    def __init__(self,rMapFN,bMapFN, saveFig = False):
        self.rMapFN,self.bMapFN = rMapFN, bMapFN
        
        #! Load these maps.
        self.rMap = ImgMap.ImgMap(rMapFN)
        self.bMap = ImgMap.ImgMap(bMapFN)

        # Load these maps into Python so we can shelve them later.
        self.rMapUtil = ImgMapUtils.ImgMapUtil()
        options={}
        options['ReflectImage']=True
        self.rMapUtil.ConvImgMapToDict(rMap,options)
        self.bMapUtil = ImgMapUtils.ImgMapUtil()
        self.bMapUtil.ConvImgMapToDict(bMap,options)
        self.bMapArray = bMapUtil.GetImage(bMap).transpose()
        
        if saveFig:
            plt.figure()
            plt.imshow(bMapArray)
            try:
                os.mkdir('pngs')
            except:
                pass
            plt.savefig('pngs/ObsmapOriginal.png')


    def ScaleMapAndSpreadRisk(self,ScaleVal = 250.):
        ''' Scale Map by some amount, then apply gaussian blur to spread risk.
        '''
        self.sMap = ImgMap.ImgMap()
        self.rMap.ScaleToPgm(sMap,0,ScaleVal)
        self.sMapUtil = ImgMapUtils.ImgMapUtil()
        self.sMapUtil.ConvImgMapToDict(self.sMap)
        self.sMapArray = rMapUtil.GetImage(sMap).transpose()/ScaleVal
        self.combMapArray = gaussian_filter((1-(self.bMapArray/255)) + \
            self.sMapArray,5) +(1-(self.bMapArray/255)) + 0.1*np.ones(self.bMapArray.shape)
        self.newArray = np.where(self.combMapArray>.9,1,self.combMapArray)
        #gBlurArray = gaussian_filter(newArray,20)
        
        if saveFig:
            plt.imshow(newArray,origin='upper')
        numPts = 10
        n,s,e,w = rMap.GetOyDeg()+rMap.GetLatDiff(), rMap.GetOyDeg(), rMap.GetOxDeg(), rMap.GetOxDeg()+rMap.GetLonDiff()
        hDiff,wDiff = rMap.GetLatDiff()/(numPts), rMap.GetLonDiff()/(numPts)
        lat_pts = np.linspace( rMap.GetOyDeg()+hDiff/2, rMap.GetOyDeg()+rMap.GetLatDiff()-hDiff/4, numPts )
        lon_pts = np.linspace( rMap.GetOxDeg()+wDiff/2, rMap.GetOxDeg()+rMap.GetLonDiff()-wDiff/2, numPts )
        y_pts = (lat_pts - rMap.GetOyDeg())*(np.ones((1,numPts))*(rMap.GetHeight()/rMap.GetLatDiff()))[0]
        x_pts = (lon_pts - rMap.GetOxDeg())*(np.ones((1,numPts))*(rMap.GetWidth()/rMap.GetLonDiff()))[0]
        riskMap = np.zeros((numPts,numPts))
        plt.colorbar()
        
        