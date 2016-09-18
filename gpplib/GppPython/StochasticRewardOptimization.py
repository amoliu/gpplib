''' This is a new type of stochastic reward optimization algorithm, which tries to calculate the best reward function
to use based upon simulation results.
'''
import UseAgg
import os
import gpplib
import sys
import random
from gpplib.Replanner import *
from gpplib.StateMDP import *
from gpplib.SA_Replanner import *
from gpplib.StateActionMDP import *
from gpplib.Utils import *
from sets import Set

class MDP_Reward_Optimizer(object):
    ''' A class that repeatedly tries to optimize the reward function using gradient-descent
    on a parameter vector.
    '''
    def __init__(self,riskMapShelf='RiskMap.shelf',romsDataDirectory='/Users/arvind/data/roms/',dataDir='./'):
        self.pngDir = 'pngs_reward_optimizer'
        self.lastGoal = (-1,-1)
        self.numRuns = 10
        try:
            os.mkdir(self.pngDir)
        except OSError as (errno,strerror):
            pass
        self.samdp = SA_MDP(riskMapShelf,romsDataDirectory)
        self.NodeList = []
        self.StartGoalIncomplete = {}
        self.StartGoalSuccess = {}
        self.StartGoalCrash = {}
        self.lastGoal = None
        w_g, w_c, w_r = 1., -1., -1.
        self.theta = { 'w_g':w_g, 'w_r':w_r, 'w_c':w_c }
        self.lastTheta = self.theta.copy()
        self.deltaTheta = {'w_g':0., 'w_r':0., 'w_c':0.}
        self.NodeList = self.GetListOfNodesInGraph()
        self.goal = random.choice(self.NodeList)
        self.dateList = DateRange(2011,2,1,2011,2,1).DateList
        self.lastNumCrashes = 0; 
        self.lastNumIncompletes = 0;
        self.lastDistToGoal = 0.6;
        self.numDays = 2
        self.simTime = np.arange(0,24)
        self.posNoise, self.romsNoise = 0.1, 0.01
        self.updatedTheta=False
        self.JerrHist = {}
        self.thetaHist = {}
        self.lastJerr = 0.
        self.iter = 0
        self.alpha = 0.2 # Learning rate parameter.
        self.myDataDir = dataDir
        self.startLocs = self.GetRandomLocs(self.numRuns)

        
    def GetRandomDayAndLoadCurrentsAndTransitionModels(self):
        self.yy,self.mm,self.dd = random.choice(self.dateList)
        print 'Using %04d-%02d-%02d as date for simulations.'%(self.yy,self.mm,self.dd)
        self.samdp.GetRomsData(self.yy,self.mm,self.dd,self.numDays)
        self.samdp.GetTransitionModelFromShelf(self.yy,self.mm,self.dd,self.numDays,self.posNoise,self.romsNoise,self.myDataDir+'NoisyGliderModels2')
        
        
    def GetListOfNodesInGraph(self):
        self.NodeList = []
        for a in self.samdp.g.nodes():
                i,j = self.samdp.GetXYfromNodeStr(a)
                self.NodeList.append( (i,j) )
        return self.NodeList
    
    def GetRandomLocs(self,numLocs,avoidLocation=None,allUnique=True):
        self.NodeList = self.GetListOfNodesInGraph()
        print self.NodeList
        if numLocs<=0 or len(self.NodeList)==0:
            return None
        # Select some random start locations...
        if allUnique:
            if numLocs>=len(self.NodeList): # Not enough unique items in the first place!
                return None
            else:
                if avoidLocation!=None:
                    randomLocsSet = Set([avoidLocation])
                else:
                    randomLocsSet = Set()
                while len(randomLocsSet)<numLocs:
                    randomLocsSet.add(random.choice(self.NodeList))
                randomLocs = list(randomLocsSet)
        else:
            randomLocs = []
            for i in range(0,numLocs):
                randomLocs.append(random.choice(self.NodeList))
        return randomLocs
    
    def EstimateGradient(self,numCrashes,numIncompletes,distToGoal):
        print 'Estimating Gradient. NumCrashes=%d, NumIncompletes=%d'%(numCrashes,numIncompletes)
        self.DeltaJerr = (math.sqrt((numCrashes)**2+(numIncompletes)**2+distToGoal**2)-self.lastJerr)/2
        self.lastJerr  = math.sqrt((numCrashes)**2+(numIncompletes)**2+distToGoal**2)
        self.JerrHist['%d'%(self.iter)]= self.lastJerr
        print 'Jerr =',self.lastJerr
        
        print 'numCrashes=%f, numIncompletes=%f, distToGoal=%f'%(numCrashes,numIncompletes,distToGoal)
        grad = {}
        #for weightKey, weightVal in self.deltaTheta.items():
        #self.deltaTheta[weightKey] = self.theta[weightKey] - self.lastTheta[weightKey]
        if distToGoal > 1: # we're not closer to the goal
            self.theta['w_g'] += self.alpha * distToGoal/50.
            self.theta['w_r'] += self.alpha
            if (self.theta['w_r']>=-0.1): 
                self.theta['w_r']=-0.1
            self.updatedTheta = True
        if numCrashes >0:
            self.theta['w_r']=self.theta['w_r'] - self.alpha * numCrashes
            self.theta['w_g']=self.theta['w_g'] - self.alpha * numCrashes
            self.updatedTheta = True
        if numIncompletes >0:
            self.theta['w_g']+=self.alpha * numIncompletes
            self.theta['w_r']= self.theta['w_r'] + self.alpha            
            if (self.theta['w_r']>=-0.1): 
                self.theta['w_r']=-0.1 
            self.updatedTheta = True
            #if self.deltaTheta[weightKey]!=0.:
            #    grad[weightKey] = self.DeltaJerr/self.deltaTheta[weightKey]
            #else:
            #    grad[weightKey] = self.DeltaJerr/1.
        print '------------------------ Theta = ',self.theta
        #theta = self.UpdateTheta(grad)
        self.thetaHist['%d'%(self.iter)] = self.theta
        self.iter+=1
        self.lastNumCrashes = numCrashes; self.lastNumIncompletes = numIncompletes;
        self.lastDistToGoal = distToGoal;
        
        return grad
        
    def DoSimulationsForGoal(self,goal):
        saMdpResult = {}
        
        if goal!= self.lastGoal or self.updatedTheta:
            self.samdp.SetGoalAndRewardsAndInitTerminalStates(goal,self.theta)
            
            print 'Doing Value iteration for State-Action MDP'
            self.samdp.doValueIteration(0.0001,50)
            self.Xpolicy,self.Ypolicy = self.samdp.DisplayPolicy()
            plt.title('SA-MDP Policy with goal (%d,%d)'%(goal[0],goal[1]))
            plt.text(1.5,10,'Theta[w_r]=%.3f, Theta[w_g]=%.3f'%(self.theta['w_r'],self.theta['w_g']))
            plt.savefig('%s/SA_MDP_Policy_Goal_%04d%02d%02d_%d_%d_%d.png'%(self.pngDir,self.yy,self.mm,self.dd,goal[0],goal[1],self.iter))
            plt.close()
            
            self.lastGoal = goal
        
        plt.figure()
        startT = self.simTime[0] #random.choice(self.simTime)
        self.samdp.gm.PlotNewRiskMapFig(startT)
        saMdpResult['Risk'], saMdpResult['pathLength'], saMdpResult['Time'] = [], [], []
        saMdpResult['numHops'], saMdpResult['distFromGoal'], saMdpResult['CollisionReason'] = [], [], []
        saMdpResult['isSuccess']= []; saMdpResult['startTime'] = []
        saMdpResult['finalLoc'] = []
        sa_totRiskMDP, sa_totHopsMDP, sa_totSuccessMDP, sa_totCrashesMDP, sa_totFalseStartsMDP, sa_totTimeMDP, sa_totDistMDP = 0.,0.,0.,0.,0.,0.,0.
        sa_totNoPolicyMDP, sa_totNanMDP, sa_totNonStartsMDP = 0, 0, 0
        for i in range(self.numRuns):
            start = self.startLocs[i]
            tempRiskMDP, landedMDP = self.samdp.SimulateAndPlotMDP_PolicyExecution(start,goal,startT+i, False )
            saMdpResult['Risk'].append(self.samdp.gs.totalRisk); saMdpResult['pathLength'].append(self.samdp.gs.totalPathLength/1000.)
            saMdpResult['Time'].append(self.samdp.gs.totalTime/3600.); saMdpResult['numHops'].append(self.samdp.gs.numHops)
            saMdpResult['CollisionReason'].append(self.samdp.gs.CollisionReason); saMdpResult['isSuccess'].append(self.samdp.gs.isSuccess)
            saMdpResult['distFromGoal'].append(self.samdp.gs.distFromGoal); saMdpResult['startTime'].append(startT+i)
            saMdpResult['finalLoc'].append((self.samdp.gs.finX,self.samdp.gs.finY))
            sa_totRiskMDP+=self.samdp.gs.totalRisk; sa_totHopsMDP+=self.samdp.gs.numHops; sa_totTimeMDP+=self.samdp.gs.totalTime/3600.; sa_totDistMDP+=self.samdp.gs.totalPathLength/1000.
            if self.samdp.gs.isSuccess==True:
                sa_totSuccessMDP+=1
            
            if self.samdp.gs.CollisionReason!=None:
                if self.samdp.gs.CollisionReason=='Obstacle':
                    sa_totCrashesMDP+=1
                else:
                    if self.samdp.gs.CollisionReason=='RomsNansAtStart':
                        sa_totNonStartsMDP+=1
                    else:
                        if self.samdp.gs.CollisionReason == 'RomsNanLater':
                            sa_totNanMDP +=1
                        elif self.samdp.gs.CollisionReason == 'DidNotFindPolicy':
                            sa_totNoPolicyMDP +=1
        self.samdp.gm.PlotCurrentField(startT);
        plt.text(1.5,10,'Theta[w_r]=%.3f, Theta[w_g]=%.3f'%(self.theta['w_r'],self.theta['w_g']))
        plt.savefig('%s/Ensembles_%04d%02d%02d_%d_%d_%d_%d_%d.png'%(self.pngDir,self.yy,self.mm,self.dd,start[0],start[1],goal[0],goal[1],self.iter))                   
        
        # Now, we have the results of this run.
        grad = self.EstimateGradient(sa_totCrashesMDP, (self.numRuns-sa_totSuccessMDP-sa_totCrashesMDP), sa_totDistMDP )
        print grad
        return saMdpResult
        
    
conf = GppConfig()
mro = MDP_Reward_Optimizer(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir,conf.myDataDir)
mro.GetRandomDayAndLoadCurrentsAndTransitionModels()
# Armed with these nodes in the graph, let us try to run a few simulations.
result = {}
GoalLocs=mro.GetRandomLocs(10)
print 'Goals chosen are:',GoalLocs
#for goal in GoalLocs:
lastXpol, lastYpol, lastGoal = None, None, None
for j in range(0,10):
    goal = GoalLocs[j]
    for i in range(0,2):
            result['(%d,%d)'%(goal[0],goal[1])] = mro.DoSimulationsForGoal(goal)
            xpol,ypol = mro.Xpolicy,mro.Ypolicy
            if lastXpol!=None and lastYpol!=None:
                if xpol.all()==lastXpol.all() and ypol.all()==lastYpol.all() and goal==lastGoal:
                    print 'Final Values for Theta are',mro.theta
                    print 'Theta History ',mro.thetaHist
                    print 'Jerr History',mro.JerrHist
                    break
            lastXpol,lastYpol = xpol, ypol
        

        
        