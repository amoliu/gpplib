from gpplib import *
from gpplib.StateMDP import *


yy,mm,dd,numDays = 2011,2,1,2
posNoise = 0.1
curNoise = 0.01
start,goal = (0,6),(8,1)
print 'debugS_MDP!'
import gpplib.Utils
conf = gpplib.Utils.GppConfig()
sMdp = MDP(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir)
sMdp.GetTransitionModelFromShelf(yy, mm, dd, numDays, posNoise, curNoise, conf.myDataDir+'NoisyGliderModels2' )
sMdp.SetGoalAndInitTerminalStates(goal, 10.)
sMdp.doValueIteration(0.0001,50)
sMdp.DisplayPolicy()
plt.title('State-MDP Policy with goal (%d,%d)'%(goal[0],goal[1]))
plt.savefig('State_mdp_Jan.png')
sMdp.GetRomsData(yy, mm, dd, numDays, True)
plt.figure()
sMdp.gm.PlotNewRiskMapFig()
sMdp.gm.PlotCurrentField(1)
sMdp.SimulateAndPlotMDP_PolicyExecution(start, goal, 0, False, 'r-')
plt.savefig('State_mdp_execution_Jan.png')
