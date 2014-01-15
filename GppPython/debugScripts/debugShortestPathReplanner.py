import sys
import gpplib
from gpplib.Replanner import *

conf = gpplib.Utils.GppConfig()
yy,mm,dd,numDays = 2011,2,1,2
rp = Replanner(conf.myDataDir+'RiskMap.shelf',conf.myDataDir+'roms/')
rp.GetTransitionModelFromShelf(yy,mm,dd,numDays,0.1,0.01,conf.myDataDir+'NoisyGliderModels2')
u,v,time1,depth,lat,lon = rp.GetRomsData(yy,mm,dd,numDays)
rp.CreateGraphUsingProximityGraph('ShortestPath') # Run a Min-Exp-Risk replanner
#rp.CreateMinRiskGraph() # Run a Min-Risk replanner

rp2 = Replanner(conf.myDataDir+'RiskMap.shelf',conf.myDataDir+'roms/')
rp2.GetTransitionModelFromShelf(yy,mm,dd,numDays,0.1,0.01,conf.myDataDir+'NoisyGliderModels2')
u,v,time1,depth,lat,lon = rp2.GetRomsData(yy,mm,dd,numDays)
rp2.CreateGraphUsingProximityGraph('MinExpRisk') # Run a Min-Exp-Risk replanner

start,goal = (0,6),(8,1)
sp_mst,dist = rp.GetShortestPathMST(goal)
rp.PlotMRpaths(goal)
plt.figure(); rp.gm.PlotNewRiskMapFig(); rp.gm.PlotCurrentField(1)

sp_mst2,dist2 = rp2.GetShortestPathMST(goal)
rp2.PlotMRpaths(goal)
plt.figure(); rp.gm.PlotNewRiskMapFig(); rp.gm.PlotCurrentField(1)

totRiskMER = 0
numFailsMER = 0
for i in range(5,10):
    tempRiskMER,landedMER=rp2.SimulateAndPlotMR_PolicyExecution(start,goal,sp_mst,i,False)
    tempRiskSP , landedSP = rp.SimulateAndPlotMR_PolicyExecution(start,goal,sp_mst,i,False,'g-')
    if landedMER != True:
        totRiskMER+=tempRiskMER
    else:
        numFailsMER+=1
