from gpplib import *
from gpplib.GenGliderModelUsingRoms import GliderModel
from matplotlib import pyplot as plt
import numpy as np
import math, random

yy,mm,dd,numDays = 2011,1,1,2

conf = GppConfig()
gm = GliderModel(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir)
u,v,time,depth,lat,lon = gm.GetRomsData(yy,mm,dd,numDays) 


from getTransitionModels import *

ptg = ProduceTransitionGraph(conf.riskMapDir+'RiskMap.shelf',conf.romsDataDir)
ptg.UseRomsNoise = True
transModel = ptg.CreateTransitionModelFromProxemicGraph(yy,mm,dd,numDays,1.5,0.01,0.1,True)
