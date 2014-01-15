import sys
import gpplib
from gpplib.SA_Replanner import *
from gpplib.LatLonConversions import *
from gpplib.Utils import *

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
        

conf = gpplib.Utils.GppConfig()
yy,mm,dd,numDays = 2012,7,29,0
sarp = SA_Replanner2(conf.myDataDir+'RiskMap3.shelf',conf.myDataDir+'roms/')
sarp.GetTransitionModelFromShelf(yy,mm,dd,numDays,0.01,0.01,conf.myDataDir+'NoisyGliderModels4')
u,v,time1,depth,lat,lon = sarp.GetRomsData(yy,mm,dd,numDays,True,True)
sarp.gm.GetRomsData(yy,mm,dd,numDays,True,True)
sarp.CreateExpRiskGraph() # Run a Min-Exp-Risk replanner
#rp.CreateMinRiskGraph() # Run a Min-Risk replanner

util = LLConvert()
goal_wLat, goal_wLon = 3329.485, -11819.777
goalLat, goalLon = util.WebbToDecimalDeg(goal_wLat,goal_wLon)
goalX,goalY = sarp.gm.GetXYfromLatLon(goalLat,goalLon)

start_wLat, start_wLon = 3331.5620, -11844.1030
startLat,startLon = util.WebbToDecimalDeg(start_wLat, start_wLon)
startX, startY = sarp.gm.GetXYfromLatLon(startLat,startLon)

start = (startX,startY); goal=(goalX,goalY)

#start,goal=(1,15),(14,12) #start,goal=(0,6),(8,1)
sp_mst,dist = sarp.GetShortestPathMST(goal)
sarp.PlotMRpaths(goal)
plt.figure(); sarp.gm.PlotNewRiskMapFig(); sarp.gm.PlotCurrentField(1)

totRiskMER = 0
numFailsMER = 0
for i in range(0,5):
    tempRiskMER,landedMER=sarp.SimulateAndPlotMR_PolicyExecution(start,goal,sp_mst,i,newFig=False)
    if landedMER != True:
        totRiskMER+=tempRiskMER
    else:
        numFailsMER+=1



