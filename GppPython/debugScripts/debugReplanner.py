import sys
import gpplib
from gpplib.Replanner import *

conf = gpplib.Utils.GppConfig()
yy,mm,dd,numDays = 2012,7,18,2
rp = Replanner(conf.myDataDir+'RiskMap7.shelf',conf.myDataDir+'roms/',1.5)

#rp.gm.ReverseY = True

#rp.GetTransitionModelFromShelf(yy,mm,dd,numDays,0.1,0.01,conf.myDataDir+'NoisyGliderModels2')
u,v,time1,depth,lat,lon = rp.GetRomsData(yy,mm,dd,numDays,True,True)
rp.CreateGraphUsingProximityGraph('MinRisk') # Run a Min-Exp-Risk replanner
#rp.CreateGraphUsingProximityGraph('ShortestPath') # Run a Min-Exp-Risk replanner

#rp.CreateMinRiskGraph() # Run a Min-Risk replanner
#start,goal = (0,6),(8,1)
#start,goal = (3.78802622,1.48330278), (1,0)
start,goal=(3,12),(22,7)
sp_mst,dist = rp.GetShortestPathMST(goal)
rp.PlotMRpaths(goal)
plt.figure(); rp.gm.PlotNewRiskMapFig(); rp.gm.PlotCurrentField(1);

totRiskMER = 0
numFailsMER = 0
for i in range(5,10):
    tempRiskMER,landedMER=rp.SimulateAndPlotMR_PolicyExecution(start,goal,sp_mst,i,newFig=False)
    if landedMER != True:
        totRiskMER+=tempRiskMER
    else:
        numFailsMER+=1
