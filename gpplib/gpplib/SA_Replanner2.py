import random
import datetime
import ftplib

from sets import Set
import gpplib
from gpplib.Utils import *
from gpplib.GliderFileTools import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.PseudoWayptGenerator import *
from gpplib.SA_Replanner import *
from gpplib.LatLonConversions import *


class SA_Replanner2( SA_Replanner ):
    ''' Sub-class of SA_Replanner dealing with the new type of Risk-map
    '''
    def __init__(self,shelfName='RiskMap3.shelf',sfcst_directory='./',dMax=1.5):
        super(SA_Replanner2,self).__init__(shelfName,sfcst_directory,dMax)
        
        
    def GetTransitionModelFromShelf(self,yy,mm,dd,numDays,posNoise=None,currentNoise=None,shelfDirectory='.'):
        """ Loads up Transition models from the shelf for a given number of days, starting from a particular day, and a given amount of noise in position and/or a given amount of noise in the current predictions. We assume these models have been created earlier using ProduceTransitionModels.
            
            Args:
                * yy (int): year
                * mm (int): month
                * dd (int): day
                * numDays (int): number of days the model is being built over
                * posNoise (float): Amount of std-deviation of the random noise used in picking the start location
                * currentNoise (float): Amount of prediction noise in the ocean model
                * shelfDirectory (str): Directory in which the Transition models are located.
        """
        self.posNoise = posNoise; self.currentNoise = currentNoise
        if posNoise==None and currentNoise==None:
            gmShelf = shelve.open('%s/gliderModel3_%04d%02d%02d_%d.shelf'%(shelfDirectory,yy,mm,dd,numDays), writeback=False )
        if posNoise!=None:
            if currentNoise!=None:
                gmShelf = shelve.open('%s/gliderModel3_%04d%02d%02d_%d_%.3f_RN_%.3f.shelf'%(shelfDirectory,yy,mm,dd,numDays,posNoise,currentNoise),writeback=False)
            else:
                gmShelf = shelve.open('%s/gliderModel3_%04d%02d%02d_%d_%.3f.shelf'%(shelfDirectory,yy,mm,dd,numDays,posNoise), writeback=False)
        if posNoise==None and currentNoise!=None:
            gmShelf=shelve.open('%s/gliderModel3_%04d%02d%02d_%d_RN_%.3f.shelf'%(shelfDirectory,yy,mm,dd,numDays,currentNoise), writeback=False) 
        
        self.gm.TransModel = gmShelf['TransModel']
        self.gm.FinalLocs = gmShelf['FinalLocs']
        self.gm.TracksInModel = gmShelf['TracksInModel']
        self.gModel = {}
        self.gModel['TransModel'] = gmShelf['TransModel']
        gmShelf.close()