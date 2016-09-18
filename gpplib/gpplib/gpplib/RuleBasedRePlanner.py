''' @Summary: This program implements a Rule-based planner which switches plans depending upon the correlation
state of the node it is currently at. The motivation behind this is what we noticed about our planners, where the
SA-MDP is able to make safer choices when starting/ending at a poorly correlated node, while the SA-MRP does better
when starting/ending at well co-related nodes especially when the ocean currents are slower than those of the glider.

So here is the rule based planner we are going to use:
1. Compute the mean and variance of the depth-averaged currents around the nodes being considered for planning.
2.  If \mu+\sigma > nominal_glider_vel 
        use mdp_policy
    else:
        If isWellCorrelated(curNode):
            use SA_Replanner
        else:
            use SA_mdp_policy
'''
#import UseAgg
import os
import gpplib
import sys
from gpplib.Replanner import *
from gpplib.StateMDP import *
from gpplib.SA_Replanner import *
from gpplib.StateActionMDP import *
from gpplib.Utils import *
from gpplib.Simulate import *

class RuleBasedReplanner(object):
    ''' Rule based Replanner. '''
    def __init__(self,riskMapShelf='RiskMap.shelf',romsDataDirectory='/Users/arvind/data/roms/',myDataDir='/Users/arvind/data/'):
        self.pngDir = 'pngs_sa_mr_mer_mdp_rrp'
        self.lastGoal = (-1,-1)
        self.numRuns = 10
        try:
            os.mkdir(self.pngDir)
        except OSError as (errno,strerror):
            pass
        self.rp = SA_Replanner(riskMapShelf,romsDataDirectory)
        self.samdp = SA_MDP(riskMapShelf,romsDataDirectory)
        self.gm = GliderModel(riskMapShelf,romsDataDirectory)
        self.gs = GliderSimulator(riskMapShelf,romsDataDirectory)
        self.maxDepth = 80.0
        self.currentsLoaded = None
        self.transModelLoaded = None
        self.MeanVariance = {}
        self.lookAhead = 24.0
        self.myDataDir = myDataDir
        GoodCorrLocsU,BadCorrLocsU,GoodCorrLocsV,BadCorrLocsV, \
            self.GoodCorrLocs, self.BadCorrLocs = self.GetGoodBadCorrLocs(0.5, 48,self.myDataDir)
        
        
    def GetCorrLocLists(self,BinCorrMat):
        GoodCorrLocs,BadCorrLocs={},{}
        sX,sY = BinCorrMat.shape
        for y in range(sY):
            for x in range(sX):
                if BinCorrMat[x,y]==1.0:
                    GoodCorrLocs['%d,%d'%(x,y)]= (x,y)
                if BinCorrMat[x,y]==0.0:
                    BadCorrLocs['%d,%d'%(x,y)] = (x,y)
        return GoodCorrLocs, BadCorrLocs
    
    def GetGoodBadCorrLocs(self,Thresh=0.5,TimeScale=48,dataDir='.'):
        CorrShelf = shelve.open('%s/CorrModel_%.2f_%d.shelf'%(dataDir,Thresh,TimeScale),writeback=False)
        BinCorrMatU,BinCorrMatV,BinCorrMatS = CorrShelf['BinCorrMatU'],CorrShelf['BinCorrMatV'],CorrShelf['BinCorrMatS']
        CorrShelf.close()
        GoodCorrLocsU,BadCorrLocsU = self.GetCorrLocLists(BinCorrMatU)
        GoodCorrLocsV,BadCorrLocsV = self.GetCorrLocLists(BinCorrMatV)
        GoodCorrLocsS,BadCorrLocsS = self.GetCorrLocLists(BinCorrMatS)
        sX,sY = BinCorrMatS.shape
        
        return GoodCorrLocsU,BadCorrLocsU,GoodCorrLocsV,BadCorrLocsV,GoodCorrLocsS,BadCorrLocsS
    
    def GetRomsData(self,yy,mm,dd,numDays,UpdateSelf=True):
        if self.currentsLoaded != '%04d%02d%02d_%d'%(yy,mm,dd,numDays):
            self.u,self.v,self.time1,self.depth,self.lat,self.lon = self.rp.GetRomsData(yy,mm,dd,numDays)
            self.u,self.v,self.time1,self.depth,self.lat,self.lon = self.samdp.GetRomsData(yy,mm,dd,numDays)
            self.gs.gm.GetRomsData(yy,mm,dd,numDays)
            self.gm.GetRomsData(yy,mm,dd,numDays)
            self.u2, self.v2 = self.u[:,0:self.maxDepth,:,:],self.v[:,0:self.maxDepth,:,:]
            self.currentsLoaded = '%04d%02d%02d_%d'%(yy,mm,dd,numDays)
            if UpdateSelf:
                self.yy,self.mm,self.dd = yy,mm,dd
                self.numDays = numDays
                self.gm.numDays = numDays
                
    def GetTransitionModelFromShelf(self,yy,mm,dd,numDays,posNoise,romsNoise,romsDataDir):
        if self.transModelLoaded != '%04d%02d%02d_%d'%(yy,mm,dd,numDays):
            self.samdp.GetTransitionModelFromShelf(yy,mm,dd,numDays,posNoise,romsNoise,romsDataDir)
            self.rp.GetTransitionModelFromShelf(yy,mm,dd,numDays,posNoise,romsNoise,romsDataDir)
            self.rp.CreateExpRiskGraph()
        
    def GetMeanAndVariance(self,t1,t2):
        ''' Compute the mean and variance of the currents between times t1 and t2,
        for all locations in the map. We use this to determine which policy to use
        at the given location at that time.
        '''
        #u_mu, v_mu = self.u2[t1:t2].mean(axis=1).mean(axis=1), self.v2[t1:t2].mean(axis=1).mean(axis=1)
        #print u_mu,v_mu
        meanVarStr = '%d,%d'%(t1,t2)
        if self.MeanVariance.has_key(meanVarStr):
            return self.MeanVariance[meanVarStr]
        #import pdb; pdb.set_trace()
        self.s = np.sqrt(self.u[t1:t2,0:self.maxDepth,:,:]**2 + self.v[t1:t2,0:self.maxDepth,:,:]**2)
        self.ma_s = np.ma.masked_array(self.s,np.isnan(self.s))
        self.mean_s = self.ma_s.mean(axis=1).mean(axis=1).mean(axis=1).mean(axis=0)
        self.var_s = self.ma_s.mean(axis=1).mean(axis=1).mean(axis=1).var(axis=0)
        self.sigma_s = np.sqrt(self.var_s)
        self.MeanVariance[meanVarStr] = (self.mean_s,self.var_s,self.sigma_s)
        #self.ma_u = np.ma.masked_array(self.u[t1:t2,0:self.maxDepth],np.isnan(self.u[t1:t2,0:self.maxDepth]))
        #self.ma_v = np.ma.masked_array(self.v[t1:t2,0:self.maxDepth],np.isnan(self.v[t1:t2,0:self.maxDepth]))
        #self.u_mean = np.mean(self.ma_u,axis=0)
        #self.v_mean = np.mean(self.ma_v,axis=0)
        return self.MeanVariance[meanVarStr]

    
    def GetPolicyAtCurrentNode(self,curNode,goal):
        if curNode == goal:
            return self.goal[0], self.goal[1]
        
        # First decide whether the currents are too strong for us...
        mu,var,sigma =  self.GetMeanAndVariance(int(self.totalTime), int(self.totalTime+self.lookAhead))
        print mu,var,sigma
        #if self.gm.gVel<=(mu-sigma) or self.BadCorrLocs.has_key('%d,%d'%(curNode[0],curNode[1])):
        if self.gm.gVel<=(mu-sigma) or self.BadCorrLocs.has_key('%d,%d'%(curNode[0],curNode[1])):
            print 'at: (%d,%d). Using SA-MDP'%(curNode[0],curNode[1])
            return self.samdp.GetPolicyAtCurrentNode(curNode,goal)
        else:
            print 'at: (%d,%d). Using SA-Replanner'%(curNode[0],curNode[1])
            return self.rp.GetPolicyAtCurrentNode(curNode,goal)
        
        
    
    def SimulateAndPlotRBRP_PolicyExecution(self,start,goal,simStartTime,newFig=True,lineType='r-',NoPlot='False'):
        ''' Simulate and Plot the MDP policy execution.
        
        Args:
            start (x,y) : tuple containing the start vertex on the graph
            goal (x,y) : tuple containing the goal vertex on the graph
            k (int) :  time in hours for the simulation to start from
            newFig (bool) : default=True, creates a new figure if set to true. If multiple simulations need overlaying, this is set to false.
            lineType (string): matplotlib line type. defaults to 'r-'
            NoPlot (bool) : default = False. Indicates that we do not want this plotted. (FIXME: Needs implementation).
        
        Returns:
            totalRisk (float): total risk associated with the path
            collisionState (bool): True if collided with land. False if no collision detected. 
        
        '''
        if newFig:
            plt.figure()
            plt.title('Plotting Min-Exp Risk Ensemble')
            self.gm.PlotNewRiskMapFig()
        self.totalRisk = 0
        self.distFromGoal = float('inf')
        self.totalPathLength = 0.
        self.totalTime = 0
        self.goal = goal
        self.start = start
        self.numHops = 0
        self.isSuccess = False
        
        if goal!= self.lastGoal:
            self.samdp.SetGoalAndInitTerminalStates(goal,10.)
            print 'Doing Value Iteration for State-Action MDP'
            self.samdp.doValueIteration(0.0001,50)
            Xpolicy,Ypolicy = self.samdp.DisplayPolicy()
            plt.title('SA-MDP Policy with goal (%d,%d)'%(goal[0],goal[1]))
            plt.savefig('%s/SA_MDP_Policy_Goal_%04d%02d%02d_%d_%d.png'%(self.pngDir,self.yy,self.mm,self.dd,goal[0],goal[1]))
            plt.close()
            # Find the shortest path according to the replanner.
            self.sp_mst, self.dist = self.rp.GetShortestPathMST(goal)
            self.rp.goal = goal
        
        return self.gs.SimulateAndPlot_PolicyExecution(start,goal,simStartTime,self.maxDepth,self.GetPolicyAtCurrentNode,lineType,newFig)
            

''' Debug
conf = GppConfig('../../config.shelf')
rbrp = RuleBasedReplanner(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir)
yy,mm,dd,numDays,posNoise,romsNoise = 2011,2,1,2,0.1,0.01
rbrp.GetRomsData(yy, mm, dd, numDays)
rbrp.GetTransitionModelFromShelf(yy,mm,dd,numDays,posNoise,romsNoise,conf.myDataDir+'NoisyGliderModels2')
rbrp.GetMeanAndVariance(0, 48)
start,goal = (0,6),(8,1)
simStartTime = 0

rbrp.SimulateAndPlotRBRP_PolicyExecution(start,goal,simStartTime,True,'r-')
'''
