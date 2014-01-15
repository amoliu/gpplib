import UseAgg
import os
import gpplib
import sys
from gpplib.SA_Replanner import *
from gpplib.StateActionMDP import *
from gpplib.RuleBasedRePlanner import *


''' Debug RBRP '''
conf = GppConfig()
rbrp = RuleBasedReplanner(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir)
yy,mm,dd,numDays,posNoise,romsNoise = 2011,5,1,2,0.1,0.01
rbrp.GetRomsData(yy, mm, dd, numDays)
rbrp.GetTransitionModelFromShelf(yy,mm,dd,numDays,posNoise,romsNoise,conf.myDataDir+'NoisyGliderModels2')
rbrp.GetMeanAndVariance(0, 48)
start,goal = (0,6),(8,1)
simStartTime = 0

rbrp.SimulateAndPlotRBRP_PolicyExecution(start,goal,simStartTime,True,'r-')
