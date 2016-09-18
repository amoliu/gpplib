''' **debugMDP.py** - a sample program to run an MDP
Author: Arvind A de Menezes Pereira

'''
import sys
import gpplib
from gpplib.MDP_class import *

''' We are going to create two MDPs here - one having no Noise in its transition predictions,
while the other has noise in them. The steps involved for both of these planners are roughly the 
same.
'''
conf = gpplib.Utils.GppConfig()
#! First choose a day for the simulation to start
yy,mm,dd,numDays = 2011,2,1,2
#! Set some Noise values
posNoise, currentNoise = 0.1, 0.01
''' Create two MDP instances
'''
#mdp = MDP(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir); 
mdp2 = MDP(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir);
''' Load up the transition models for the noiseless MDP
'''
#mdp.GetTransitionModelFromShelf(yy,mm,dd,numDays,None,None,conf.myDataDir+'NoisyGliderModels2')
#u,v,time1,depth,lat,lon = mdp.GetRomsData(yy,mm,dd,numDays)
''' Load up the transition models for the noisy MDP
'''
mdp2.GetTransitionModelFromShelf(yy,mm,dd,numDays, posNoise, currentNoise,conf.myDataDir+'NoisyGliderModels2')
u,v,time1,depth,lat,lon = mdp2.GetRomsData(yy,mm,dd,numDays)

''' Set a start and a goal
'''
start,goal=(0,0),(5,1)
#mdp.SetGoalAndInitTerminalStates(goal)
mdp2.SetGoalAndInitTerminalStates(goal)

''' Start doing Value iteration and display the policy found.'''
#print 'Doing Value Iteration without Noise'
mdp2.doValueIteration(0,50)
Xpolicy,Ypolicy = mdp2.DisplayPolicy()
plt.title('MDP Policy with goal (%d,%d)'%(goal[0],goal[1]))
plt.savefig('MDP_policy_Feb.png')
plt.figure()
mdp2.gm.PlotNewRiskMapFig()
mdp2.gm.PlotCurrentField(1)
''' Simulate and plot the MDP policy execution '''
mdp2.SimulateAndPlotMDP_PolicyExecution(start,goal,0,False,'r-')
plt.savefig('MDP_simulation_Feb.png')
#mdp2.InitMDP_Simulation(start,goal,0,'-r',False)
#while (not (mdp2.isSuccess or mdp2.possibleCollision==True)):
#    mdp2.SimulateAndPlotMDP_PolicyExecution_R()
