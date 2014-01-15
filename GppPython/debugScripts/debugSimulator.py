from gpplib import Utils
from gpplib.Simulate import *
from gpplib.StateActionMDP import SA_MDP
from matplotlib import pyplot as plt

posNoise = 0.1
curNoise = 0.01
start,goal = (0,6),(8,1)
conf = Utils.GppConfig()
yy,mm,dd,numDays = 2011,2,1,2

FullSimulation,HoldValsOffMap=False,True
simStartTime=0
maxDepth = 80.

samdp = SA_MDP(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir)
samdp.GetTransitionModelFromShelf(yy, mm, dd, numDays, posNoise, curNoise, conf.myDataDir+'NoisyGliderModels2' )
samdp.SetGoalAndInitTerminalStates(goal, 10.)
samdp.doValueIteration(0.0001,50)
samdp.DisplayPolicy()
plt.title('MDP Policy with goal (%d,%d)'%(goal[0],goal[1]))
plt.savefig('SAmdp_Jan.png')
samdp.GetRomsData(yy, mm, dd, numDays, True)

'''
gs = GliderSimulator_R(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir)
u,v,time,depth,lat,lon = gs.gm.GetRomsData(yy,mm,dd,numDays)
gs.Start_Simulation(start,goal,simStartTime,80,'r-',FullSimulation)
gs.SetupCallbacks(samdp.GetPolicyAtCurrentNode)
for i in range(50):
    totalRisk, crashState =gs.SimulateAndPlot_PolicyExecution_R(-1)
'''

gs2 = GliderSimulator(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir)
u,v,time,depth,lat,lon = gs2.gm.GetRomsData(yy,mm,dd,numDays)
gs2.SimulateAndPlot_PolicyExecution(start,goal,simStartTime,maxDepth,samdp.GetPolicyAtCurrentNode)