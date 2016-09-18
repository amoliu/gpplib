''' *StateActionMDP** - A modified MDP which has a Reward function that depends upon 
state-action pairs instead of just the reward for getting to a particular state.

This makes sense because when our MDP is being run on a smaller graph, it becomes
very important that we should be able to weight the costs of hitting land very high.
In the simpler method, we will end up ignoring reaching land because these states
do not exist in our planning graph. This is the optimal thing to do in the simple 
graph, but isn't going to help us determine (in an accurate way), what we should be 
avoiding.

We expect that using the state-action pairs will allow us to incorporate the values
of the varying rewards due to performing a particular action, since in reality
there are costs associated with each action being performed. Maximizing over this
quantity is the right thing to do!
'''
import gpplib
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import math
import re
import shelve
import networkx as nx
from InterpRoms import *
from GenGliderModelUsingRoms import GliderModel
from Simulate import *


class NewSA_MDP(object):
    ''' Main State-Action MDP class
    '''
    
    def __init__(self,shelfName='RiskMap.shelf',sfcst_directory='./',dMax=1.5):
        '''
        Args:
            * shelfName (str): Name of shelf-file that contains obstacle and risk maps
            * sfcst_directory (str): Directory in which ROMS small-forecast files have been stored.
        '''
        self.gm = GliderModel(shelfName,sfcst_directory)
        self.gs = GliderSimulator(shelfName,sfcst_directory)
        self.gsR = GliderSimulator_R(shelfName,sfcst_directory)
        self.Dmax = dMax
        self.maxLengths = 50
        self.acceptR = 0.6
        #! Load the graph
        self.g = self.gm.lpGraph.copy()
        for a in self.g.nodes():
            i,j = self.GetXYfromNodeStr(a)
        
        np.set_printoptions(precision=2)
        self.possibleCollision=False
        self.Rwd = {}
        self.mdp = {}
        self.ReInitializeMDP()
        self.gamma = 1.0
        self.maxDepth = 80.
        self.w_r = -1.
        self.w_g = 10.
        self.theta = {}
        self.theta['w_r'], self.theta['w_g'] = self.w_r, self.w_g
        self.RewardsHaveChanged = False
        
    def GetXYfromNodeStr(self,nodeStr):
        ''' Convert from the name of the node string to the locations.
        Args:
            nodeStr (string): A string in the form of '(x,y)'.
        
        Returns:
            x,y if the string is in the form expected.
            None,None if a mal-formed string.
        '''
        m = re.match('\(([0-9\.]+),([0-9\.]+)\)',nodeStr)
        if m:
            return int(m.group(1)),int(m.group(2))
        else:
            return None, None
        
    def GetNodesFromEdgeStr(self,edgeStr):
        ''' Convert from a transition model edge string to the
        respective edges on the graph
        
        Args:
            * edgeStr (str): string in the format '(x1,y1),(x2,y2)'
            
        Returns:
            * x1, y1, x2, y2 values above, or None, None, None, None if string did not match.
        '''
        m = re.match('([0-9]+),([0-9]+),([0-9]+),([0-9]+)',edgeStr)
        x1,y1,x2,y2 = None,None,None,None
        if m:
            x1,y1,x2,y2 = int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4))
        return x1,y1,x2,y2
    
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
            
            Updates:
                * self.gm.FinalLocs: Stores the final locations 
        """
        self.posNoise = posNoise; 
        self.currentNoise = currentNoise 
        #import pdb; pdb.set_trace()
        if posNoise==None and currentNoise==None:
            gmShelf = shelve.open('%s/gliderModel_%04d%02d%02d_%d.shelf'%(shelfDirectory,yy,mm,dd,numDays), writeback=False )
        if posNoise!=None:
            if currentNoise!=None:
                gmShelf = shelve.open('%s/gliderModel_%04d%02d%02d_%d_%.3f_RN_%.3f.shelf'%(shelfDirectory,yy,mm,dd,numDays,posNoise,currentNoise),writeback=False)
            else:
                gmShelf = shelve.open('%s/gliderModel_%04d%02d%02d_%d_%.3f.shelf'%(shelfDirectory,yy,mm,dd,numDays,posNoise), writeback=False)
        if posNoise==None and currentNoise!=None:
            gmShelf=shelve.open('%s/gliderModel_%04d%02d%02d_%d_RN_%.3f.shelf'%(shelfDirectory,yy,mm,dd,numDays,currentNoise), writeback=False)     
        self.gm.TransModel = gmShelf['TransModel']
        #if gmShelf.has_key('FinalLocs'):
        self.gm.FinalLocs = gmShelf['FinalLocs']
        #if gmShelf.has_key('TracksInModel'):
        self.gm.TracksInModel = gmShelf['TracksInModel']
        gmShelf.close()
        # Now that we have loaded the new transition model, we better update our graph.
        self.ReInitializeMDP()
        
        
    def BuildTransitionGraph(self):
        ''' Computes the transition graph from all the available edges in the transition model.
        '''
        for a in self.g.nodes():
            for b in self.g.nodes():
                if a!=b:
                    i,j = self.GetXYfromNodeStr(a); x,y = self.GetXYfromNodeStr(b)
                    edge_str = '%d,%d,%d,%d'%(i,j,x,y)
                    if self.gm.TransModel.has_key(edge_str):
                        rwd = self.GetRewardForStateAction('%d,%d'%(i,j), edge_str)
                        self.g.add_edge('(%d,%d)'%(i,j),'(%d,%d)'%(x,y),weight=rwd,trapped=False)
        # Store a copy of g, so that we can re-run the MDP when needed
        # This is because, we will end up adding 
        self.g_copy = self.g.copy()

        
    def GetRomsData(self,yy,mm,dd,numDays,UpdateSelf=True,usePredictionData=False):
        ''' Loads up ROMs data from a particular day, for a certain number of days and supports self-update
            
        Args:
            yy (int): year
            mm (int): month
            dd (int): day
            numDays (int): number of days the model is being built over
            UpdateSelf (bool): Should the MDP update itself with the ROMS data being loaded? 
        '''
        useNewFormat = True
        u,v,time1,depth,lat,lon = self.gm.GetRomsData(yy,mm,dd,numDays,useNewFormat,usePredictionData)
        u,v,time1,depth,lat,lon = self.gs.gm.GetRomsData(yy,mm,dd,numDays,useNewFormat,usePredictionData)
        u,v,time1,depth,lat,lon = self.gsR.gm.GetRomsData(yy,mm,dd,numDays,useNewFormat,usePredictionData)
        if UpdateSelf:
            self.u,self.v,self.time1,self.depth,self.lat,self.lon = u,v,time1,depth,lat,lon
            self.yy,self.mm,self.dd = yy,mm,dd
        self.numDays = numDays
        self.gm.numDays = numDays
        return u,v,time1,depth,lat,lon
    
    def isOnMap(self,s):
        ''' Test whether the state being tested is within the map.
        Args:
            s (dict {'x','y'}) : dictionary with 'x' and 'y' values
        '''
        x,y = s
        if x<0 or x>=self.gm.Width:
            return False
        if y<0 or y>=self.gm.Height:
            return False
        return True
    
    def GetRewardForStateAction(self,state_str,action_str):
        ''' Get the reward for a state-action pair. We use a dictionary here
        to perform a lookup if we have already computed this earlier.
        
        Args:
            state (node_str) : node we are currently evaluating
            action (edge_str): action (or edge) we are currently computing the reward for.
                            
        
        Updates:
            self.Rwd[state-action-pair-str] with computed reward.
        
        Returns:
            self.Rwd[state-action-pair-str] if previously computed, else computes it and returns that result.
        '''
        OffMapNotObs = False # Treat locations off the map as high-risk locations
        state_action_str = '%s_%s'%(state_str,action_str)
        if self.Rwd.has_key(state_action_str) and not self.RewardsHaveChanged:
            return self.Rwd[state_action_str]
        else:
            X = self.gm.FinalLocs[action_str][0]; Y = self.gm.FinalLocs[action_str][1]
            tot_rwd = 0
            totNum = len(np.nonzero(self.gm.FinalLocs[action_str][0])[0])
            for i in range(0,totNum):
                lat,lon = self.gm.GetLatLonfromXY(X[i],Y[i])
                riskVal = self.gm.GetRisk(lat,lon,OffMapNotObs) * self.w_r
                #if riskVal>1:
                #    riskVal = 1
                tot_rwd += riskVal
            #import pdb; pdb.set_trace()
            if totNum>0:
                self.Rwd[state_action_str] = (tot_rwd/totNum) # Use the average.
            else:
                self.Rwd[state_action_str] = tot_rwd
            self.RewardsHaveChanged = False
                
            return self.Rwd[state_action_str]
    
    
    def GetUtilityForStateTransition(self,state,state_prime):
        ''' Compute the Utility for performing the state transition of going 
        from state to state_prime.
        
        Args:
            state (tuple of (int,int)): state x,y in planning graph coods.
            state_prime (tuple of (int,int)): state_prime x,y in P.graph coods.
            
        Returns:
            Utility (float) : utility for this state transition.
        '''
        x,y = state
        xp,yp= state_prime
        width,height=self.gm.Width, self.gm.Height
        Util = 0.
        totalProb = 0
        transProb = 0
        
        if state_prime == self.goal:
            return self.mdp['U'][y][x]
        
        stateTrans = '%d,%d,%d,%d'%(x,y,xp,yp)
        if self.gm.TransModel.has_key(stateTrans):
            transProbs = self.gm.TransModel[stateTrans][2]
            tPSize = self.gm.TransModel[stateTrans][1]
            zeroLoc = self.gm.TransModel[stateTrans][0]
            
            # Iterate over all possible actions
            for j in range(0,int(tPSize)):
                for i in range(0,int(tPSize)):
                    state_action = (x+i-zeroLoc, y+j-zeroLoc)
                    if i!=j:
                        if self.isOnMap(state_prime) and self.isOnMap(state_action):
                            if not self.gm.ObsDetLatLon(self.gm.lat_pts[yp],self.gm.lon_pts[xp], \
                                                            self.gm.lat_pts[y],self.gm.lon_pts[x]):
                                transProb = transProbs[j][i]
                                totalProb += transProb
                                # This looks like a bug to me...
                                Util += transProb * self.mdp['U'][y+j-zeroLoc][x+i-zeroLoc]
                                #Util += transProb * self.mdp['U'][y+j-zeroLoc][x+i-zeroLoc]
        if totalProb !=1:
            transProb = 1-totalProb
            Util+=transProb * self.mdp['U'][y][x]
        #print Util
        return Util
    
    def CalculateTransUtilities(self,state):
        ''' Get all the transition utilities based upon all the actions we can take
        from this state.
        
        Args:
            state (x,y) : tuple containing x and y locations in graph-coordinates
        '''
        x,y = state
        # Transition graph should have all the out-going edges from this place via
        # neighbors of this node.
        # (To see weights in graph, we can do self.g['(i,j)']['(k,l)']['weight'] ).
        UtilVec = {}
        for u,v,d in self.g.out_edges('(%d,%d)'%(x,y),data=True):
            #print u,v,d['weight']
            sa_rwd = d['weight']
            ''' Goals, are trapping terminal states.
            '''
            if d.has_key('goal_edge'):
                if self.goalReached:
                    sa_rwd = 0.
                else:
                    self.goalReached = True
                    # Now, set the weight of this edge to zero.
                    d['weight'] = 0.
                    d['trapped'] = True
                
            x1,y1 = self.GetXYfromNodeStr(u); x2,y2 = self.GetXYfromNodeStr(v)
            stateTrans = '%d,%d,%d,%d'%(x1,y1,x2,y2)
            UtilVec[stateTrans] = sa_rwd + self.gamma * self.GetUtilityForStateTransition((x1,y1), (x2,y2))
        
        return UtilVec

    def ReInitializeMDP(self):
        self.mdp['U'] = np.zeros((self.gm.Height,self.gm.Width))
        self.mdp['Uprime'] = np.zeros((self.gm.Height,self.gm.Width))
        self.g = self.gm.lpGraph.copy()
        self.BuildTransitionGraph()
        
    
    def SetGoalAndInitTerminalStates(self,goal,rewardVal=10):
        ''' Set the goal location, and initialize everything including 
        terminal states.
        
        Args:
            goal (x,y) : tuple with (x,y) given in graph coordinates.
            rewardVal (float): Reward value for getting to the goal. Defaults to 10.
        '''
        self.ReInitializeMDP()
        self.mdp['U'][goal[1],goal[0]] = rewardVal
        self.mdp['Uprime']= self.mdp['U'].copy()
        self.goal = goal
        self.goalReached = False
        ''' The goal is a trapping state, so we 
        We remove all the out-going edges from the goal, and add a self-edge with weight zero.
        '''
        for u,v,d in self.g.in_edges('(%d,%d)'%(goal[0],goal[1]),data=True):
            d['weight'] = rewardVal
            d['trapped']= False
            d['goal_edge'] = True
        
        for u,v,d in self.g.out_edges('(%d,%d)'%(goal[0],goal[1]),data=True):
             self.g.remove_edge(u,v)
        self.g.add_edge('(%d,%d)'%(goal[0],goal[1]),'(%d,%d)'%(goal[0],goal[1]),weight=0.)
        
    def SetGoalAndRewardsAndInitTerminalStates(self,goal,theta):
        ''' 
        '''
        print 'Using new theta:',theta
        self.w_r = theta['w_r']
        self.w_g = theta['w_g']
        self.theta = theta
        self.RewardsHaveChanged = True

        self.ReInitializeMDP()
        self.mdp['U'][goal[1],goal[0]] = self.w_g
        self.mdp['Uprime']= self.mdp['U'].copy()
        self.goal = goal
        self.goalReached = False
        ''' The goal is a trapping state, so we 
        We remove all the out-going edges from the goal, and add a self-edge with weight zero.
        '''
        for u,v,d in self.g.in_edges('(%d,%d)'%(goal[0],goal[1]),data=True):
            d['weight'] = self.w_g
            d['goal_edge'] = True

        for u,v,d in self.g.out_edges('(%d,%d)'%(goal[0],goal[1]),data=True):
             self.g.remove_edge(u,v)
        self.g.add_edge('(%d,%d)'%(goal[0],goal[1]),'(%d,%d)'%(goal[0],goal[1]),weight=0.)
    

    def doValueIteration(self, eps=0.00001, MaxRuns = 50):
        ''' Perform Value Iteration.
        
        Args:
            eps (float) : epsilon -> a small value which indicates the maximum change in utilities over an iteration we are interested in.
            MaxRuns (int) : maximum number of runs to do value iteration for. If negative, we will quit when the epsilon criterion is reached.
            
        Note:
            set the value of gamma if you want discounted rewards. By default gamma is 1.
        '''
        for i in range(0,MaxRuns):
            self.mdp['U'] = self.mdp['Uprime'].copy()
            self.delta = 0.
            for nodeStr in self.g.nodes():
                x,y = self.GetXYfromNodeStr(nodeStr)
                Utils = self.CalculateTransUtilities((x,y))
                ExpUtilVec = Utils.values()
                maxExpectedUtility = max(ExpUtilVec)
                #print x,y,maxExpectedUtility
                self.mdp['Uprime'][y,x] = maxExpectedUtility
                
                absDiff = abs(self.mdp['Uprime'][y,x]-self.mdp['U'][y,x])
                if(absDiff>self.delta):
                    self.delta = absDiff
            print 'delta=%f'%(self.delta)
            print 'U',self.mdp['U']
            if (self.delta<=eps*(1-self.gamma)/self.gamma):
                print 'delta is smaller than eps %f. Terminating.'%(self.delta)
                break
        # Get Policy tree.
        self.GetPolicyTreeForMDP()
        
        
    ''' -------------------------------------------------------------------------------------------
    ---------------------------------- Code to create the policy tree -----------------------------   
    --------------------------------------------------------------------------------------------'''
    def DisplayPolicy(self,FigHandle = None):
        ''' Display MDP policy
        
        Args:
            FigHandle -> Pyplot.Figure handle if we want to draw the policy on the
            previous figure. If this is not passed, a new figure will be created.
        '''
        width,height = self.gm.Width,self.gm.Height
        Xpolicy = np.zeros((width,height))
        Ypolicy = np.zeros((width,height))
        Xloc,Yloc = np.zeros((width,height)), np.zeros((width,height))
        Uprime = self.mdp['U']
        if FigHandle==None:
            plt.figure()
        self.gm.PlotNewRiskMapFig()
        
        for a in self.g.nodes():
            x,y = self.GetXYfromNodeStr(a) 
            Xloc[x][y],Yloc[x][y] = x,y
            UtilVec = np.zeros(10)
            maxUtil = -float('inf')
            k,maxU,maxV= 0,0,0
            for u,v,d in self.g.out_edges(a,data=True):
                i,j = self.GetXYfromNodeStr(v)
                UtilVec[k] = Uprime[j][i]
                if maxUtil<=UtilVec[k]:
                    maxUtil = UtilVec[k]
                    maxU,maxV = i-x,j-y
                    k=k+1
                Xpolicy[x][y],Ypolicy[x][y] = 0.5*maxU, 0.5*maxV
        plt.quiver(Xloc,Yloc,Xpolicy,Ypolicy)
        plt.title('MDP Policy')
        return Xpolicy,Ypolicy
        
    def GetPolicyTreeForMDP(self):
        ''' Get the policy tree for the MDP. This is required in order for us to be able to
        simulate.
        '''
        width, height = self.gm.Width, self.gm.Height
        
        Uprime = self.mdp['Uprime']
        self.gm2 = nx.DiGraph()
        
        for a in self.g.nodes():
            x,y = self.GetXYfromNodeStr(a)
            UtilVec = np.zeros(10)
            maxUtil = -float('inf')
            k,maxU,maxV = 0,0,0
            for u,v,d in self.g.out_edges(a,data=True):
                i,j = self.GetXYfromNodeStr(v)
                UtilVec[k] = Uprime[j][i]
                if maxUtil<=UtilVec[k]:
                    maxUtil = UtilVec[k]
                    maxU,maxV = i-x,j-y
                    bestNode = v
                    k=k+1
            if not(maxU==0 and maxV==0):
                self.gm2.add_edge(a,bestNode,weight=maxUtil)
        '''
        if self.UseNetworkX == False:
            dot = write(self.gm2)
            G = gv.AGraph(dot)
            G.layout(prog = 'dot')
            G.draw('SCB_MDP_MSG.png')
        '''
        return self.gm2
    
    def GetPolicyAtCurrentNode(self,curNode,goal,forceGoal=False):
        if curNode==goal:
            return self.goal[0], self.goal[1]
        
        try:
            neighborNode = self.gm2.neighbors('(%d,%d)'%(int(curNode[0]),int(curNode[1])))
            if len(neighborNode)>0:
                nextNode = neighborNode[0]
            else:
                nextNode = None
        except nx.NetworkXError:
            nextNode = None
        
        if nextNode!=None:
            m = re.match('\(([0-9]+),([0-9]+)\)', nextNode) # Changed this!!!
            #m2 =re.match('\(([0-9]+),([0-9]+)\)',goal)
            if m:
                return int(m.group(1)),int(m.group(2))
            
        return self.FindNearestNodeOnGraph(curNode)
    
    '''    
    def GetPolicyAtCurrentNode(self,curNode,goal,forceGoal=False):
        if curNode == goal:
            return self.goal[0],self.goal[1]
        
        self.UseNetworkX = True
        import networkx as nx
        try:
            if self.UseNetworkX:
                neighborNode = self.gm2.neighbors(curNode)
                if len(neighborNode)>0:
                    nextNode = neighborNode[0]
                else:
                    nextNode = None
            else:
                nextNode = self.pol_tree.node_neighbors[curNode]
        except KeyError:
            nextNode=None
        except nx.NetworkXError:
            nextNode = None
            
        if nextNode!=None:
            m = re.match('\(([0-9]+),([0-9]+)\)', nextNode) # Changed this!!!
            m2 =re.match('\(([0-9]+),([0-9]+)\)',goal)
            if m:
                return int(m.group(1)),int(m.group(2))
            if m2:
                return int(m2.group(1)),int(m2.group(2))
            
        return self.FindNearestNodeOnGraph(curNode)
    '''
        
    def FindNearestNodeOnGraph(self,curNode):
        nearest_dist = float('inf')
        best_utility = -float('inf')
        nearest_node = (None,None)
        for a in self.g.nodes():
            i,j = curNode
            x,y = self.GetXYfromNodeStr(a)
            dist = math.sqrt((i-x)**2+(j-y)**2)
            if not self.gm.ObsDetLatLon(self.gm.lat_pts[j],self.gm.lon_pts[i], \
                                                            self.gm.lat_pts[y],self.gm.lon_pts[x]):
                    if self.mdp['U'][y][x] > best_utility and dist<self.Dmax:
                        best_utility = self.mdp['U'][y][x]
                        nearest_node =  (x,y)
        return nearest_node
        
    ''' -------------------------------------------------------------------------------------------
    ---------------------------------- Code for Performing Simulations ----------------------------   
    --------------------------------------------------------------------------------------------'''
    def GetRiskFromXY(self,x,y):
        '''  Looks up the risk value for x,y from the risk-map
        
        Args:
            x,y (float,float) : x and y in graph coordinates.
        '''
        lat,lon = self.gm.GetLatLonfromXY(x,y)
        return self.gm.GetRisk(lat,lon)
    
    def SimulateAndPlotMDP_PolicyExecution(self,start,goal,simStartTime,newFig=True,lineType='r-',NoPlot='False'):
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
        
        return self.gs.SimulateAndPlot_PolicyExecution(start,goal,simStartTime,self.maxDepth,self.GetPolicyAtCurrentNode,lineType,newFig)
        
        self.a= start
        done = False
        i=0
        #x_sims,y_sims = np.zeros((24*gm.numDays,1)),np.zeros((24*gm.numDays,1))
        if simStartTime>=(24*self.gm.numDays):
           simStartTime = 24*self.gm.numDays-1
        x_sims,y_sims = 0,0
        self.finX,self.finY = start[0],start[1]
        #import pdb; pdb.set_trace()
        while (not done):
            self.numHops+=1
            #print self.a[0],self.a[1]
            try:
                bx,by = self.GetPolicyAtCurrentNode((int(self.a[0]+0.5),int(self.a[1]+0.5)),(goal[0],goal[1]))
                #bx,by = self.GetPolicyAtCurrentNode('(%d,%d)'%(int(self.a[0]+0.5),int(self.a[1]+0.5)),'(%d,%d)'%(goal[0],goal[1]))
            except TypeError:
                bx,by = None, None
            #if bx==None and by==None:
            #    import pdb; pdb.set_trace()
            if bx!=None and by!=None:
                b = (bx,by)
                #tempRisk = self.GetRiskFromXY(bx,by)
                #totalRisk+=tempRisk
                self.distFromGoal = math.sqrt((self.a[0]-goal[0])**2+(self.a[1]-goal[1])**2)
                if self.distFromGoal<=self.acceptR:
                    self.isSuccess = True
                    done = True
                sLat,sLon = self.gm.GetLatLonfromXY(self.a[0],self.a[1])
                gLat,gLon = self.gm.GetLatLonfromXY(b[0],b[1])
                tStart = simStartTime + self.totalTime/3600.
                if tStart>=24*self.gm.numDays:
                    tStart = 24*self.gm.numDays-1
                xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist = \
                    self.gm.SimulateDive(sLat,sLon,gLat,gLon, self.gm.maxDepth, self.u, self.v, self.lat, self.lon, self.depth, tStart, False )
                    #gm.SimulateDive(gm.lat_pts[a[1]], gm.lon_pts[a[0]], gm.lat_pts[b[1]], gm.lon_pts[b[0]], gm.maxDepth, u, v, lat, lon, depth, k)    
                self.xFin,self.yFin,self.latFin,self.lonFin,self.latArray,self.lonArray,self.depthArray,self.tArray,self.possibleCollision = \
                    xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision
                self.totalPathLength += totalDist
                self.CollisionReason = CollisionReason
                
                if len(tArray>0):
                    self.totalTime+=tArray[-1]
                
                if possibleCollision == False:
                    
                    tempX,tempY = self.gm.GetXYfromLatLon(np.array(latArray),np.array(lonArray))
                    x_sims,y_sims = tempX[-1:][0],tempY[-1:][0] # TODO: This might be wrong!
                    plt.plot(tempX,tempY,lineType)
                    if x_sims!=[] and y_sims!=[]:
                        tempRisk = self.GetRiskFromXY(x_sims,y_sims)
                        self.finX, self.finY = x_sims, y_sims
                        self.totalRisk+=tempRisk
                    else:
                        self.totalRisk+= self.gm.GetRisk(sLat,sLon)
                else:
                    if self.CollisionReason == 'RomsNanAtStart':
                        self.totalRisk+= self.gm.GetRisk(sLat, sLon)
                    
                    tempX,tempY = self.gm.GetXYfromLatLon(np.array(latArray),np.array(lonArray))
                    if len(tempX)>0 and len(tempY)>0:
                        if self.CollisionReason =='Obstacle' or self.CollisionReason=='RomsNanLater':
                            self.totalRisk+= self.GetRiskFromXY(tempX[-1:], tempY[-1:])
                            self.finX,self.finY = tempX[-1], tempY[-1]
                        plt.plot(tempX,tempY,lineType)
                    x_sims,y_sims = 0,0
                    done=True
                    return self.totalRisk,True # Landed on beach!
                #plt.plot([a[0],x_sims[0]],[a[1],y_sims[0]],lineType)
                try:
                    self.a = (x_sims[0],y_sims[0])
                    self.finX,self.finY = self.a
                except IndexError:
                    done = True
                    return self.totalRisk, True # Landed on beach
                    #import pdb; pdb.set_trace()
                i=i+1
                if i>self.maxLengths:
                    done = True
            else: # We did not get a policy here.
                self.CollisionReason = 'DidNotFindPolicy'
                done = True
        return self.totalRisk, False
    
    
    
    def InitMDP_Simulation(self,start,goal,startT,lineType='r',newFig = False):
        ''' Initialize Simulation of the MDP policy execution.
        
        Args:
            start (x,y) : tuple containing the start vertex on the graph
            goal (x,y) : tuple containing the goal vertex on the graph
            startT (int) :  time in hours for the simulation to start from
            lineType (string): matplotlib line type. defaults to 'r-'
            newFig (bool) : default=True, creates a new figure if set to true. If multiple simulations need overlaying, this is set to false.
        '''
        self.DoFullSim = False
        self.HoldValsOffMap = True
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
        self.a= self.start
        self.done = False
        self.Indx = 0
        self.lineType = lineType
        self.possibleCollision = False
        #x_sims,y_sims = np.zeros((24*gm.numDays,1)),np.zeros((24*gm.numDays,1))
        #if startT>=(24*self.gm.numDays):
        #   startT = 24*self.gm.numDays-1
        self.startT = startT
        self.x_sims,self.y_sims = 0,0
        self.finX,self.finY = start[0],start[1]
        self.sLat,self.sLon = self.gm.GetLatLonfromXY(self.start[0],self.start[1])
        self.gLat,self.gLon = self.gm.GetLatLonfromXY(self.goal[0],self.goal[1])
        self.latArray, self.lonArray = [], []
        #self.gm.InitSim(self.sLat,self.sLon,self.gLat,self.gLon,self.gm.MaxDepth,startT,self.DoFullSim,self.HoldValsOffMap)
        #import pdb; pdb.set_trace()
        self.lastLegComplete = True
        self.bx,self.by = None, None
        self.lastTransition = None
    

    def SimulateAndPlotMDP_PolicyExecution_R(self,simulTime=-1,PostDeltaSimCallback=None,PostSurfaceCallbackFn=None):
        ''' Simulate and plot the MDP policy execution in a re-entrant manner. This simulation is very useful
        when we want to create a movie of how things are progressing. It can be called over and over again
        after a single call to InitMDP_Simulation_
        
        Args:
            simulTime (float) : indicates the maximum amount of time we want to simulate for in hours. Defaults to -1, which means that it will only exit after completing the simulation.
            
            PostDeltaSimCallback: default=None. This is a user-defined callback function which will be executed upon completion of the simulation.
            PostSurfaceCallbackFn: default=None. This is a user-defined callback function which will be executed when the glider surfaces. This might happen
            in between a surfacing.
            
            Returns:
                totalRisk (float): total risk associated with the path
                collisionState (bool): True if collided with land. False if no collision detected.
        '''
        i = self.Indx
        tStart = self.startT
        #self.lastLegComplete = self.gm.doneSimulating;
        if self.lastLegComplete == True:
                self.numHops += 1
                try:
                    self.lastTransition = [(int(self.a[0]+0.5),int(self.a[1]+0.5)),(self.bx,self.by)]
                    #self.bx, self.by = self.GetPolicyAtCurrentNode('(%d,%d)' % (int(self.a[0]), int(self.a[1])), '(%d,%d)' % (self.goal[0], self.goal[1]))
                    self.bx,self.by = self.GetPolicyAtCurrentNode((int(self.a[0]+0.5),int(self.a[1]+0.5)),(self.bx,self.by))
                    if PostSurfaceCallbackFn != None:
                        PostSurfaceCallbackFn(self.latArray,self.lonArray)
                    self.b = (self.bx, self.by)
                    self.sLat, self.sLon = self.gm.GetLatLonfromXY(self.a[0], self.a[1])
                    self.gLat, self.gLon = self.gm.GetLatLonfromXY(self.b[0], self.b[1])
                    self.gm.InitSim(self.sLat, self.sLon, self.gLat, self.gLon, self.gm.MaxDepth, tStart, self.DoFullSim, self.HoldValsOffMap)
                except TypeError: 
                    self.bx, self.by = None, None
        if self.bx != None and self.by != None:
                #self.b = (self.bx, self.by)
                #self.sLat, self.sLon = self.gm.GetLatLonfromXY(self.a[0], self.a[1])
                #self.gLat, self.gLon = self.gm.GetLatLonfromXY(self.b[0], self.b[1])
                
                xFin, yFin, latFin, lonFin, latArray, lonArray, depthArray, tArray, possibleCollision, CollisionReason, totalDist = \
                    self.gm.SimulateDive_R(simulTime) # If this is <1 it will have the same behavior as before.
                self.xFin, self.yFin, self.latFin, self.lonFin, self.latArray, self.lonArray, self.depthArray, self.tArray, self.possibleCollision = \
                    xFin, yFin, latFin, lonFin, latArray, lonArray, depthArray, tArray, possibleCollision
                self.totalPathLength += totalDist
                self.CollisionReason = CollisionReason
                self.lastLegComplete = self.gm.doneSimulating;
                if PostDeltaSimCallback!=None:
                    PostDeltaSimCallback(latArray,lonArray)
                
                self.distFromGoal = math.sqrt((self.a[0] - self.goal[0]) ** 2 + (self.a[1] - self.goal[1]) ** 2)
                if self.distFromGoal <= self.acceptR:
                    self.isSuccess = True
                    self.done = True
                
                if len(tArray > 0):
                    self.totalTime += tArray[-1]
                self.thisSimulTime = tArray[-1]
                tStart = self.startT + self.totalTime / 3600.
                if tStart >= 24 * self.gm.numDays:
                    tStart = 24 * self.gm.numDays - 1
                
                if possibleCollision == False:
                    tempX, tempY = self.gm.GetXYfromLatLon(np.array(latArray), np.array(lonArray))
                    self.x_sims, self.y_sims = tempX[-1:], tempY[-1:] 
                    plt.plot(tempX, tempY, self.lineType)
                    if self.x_sims != [] and self.y_sims != []:
                        if self.lastLegComplete:
                            tempRisk = self.GetRiskFromXY(self.x_sims, self.y_sims)
                            self.finX, self.finY = self.x_sims, self.y_sims
                            self.totalRisk += tempRisk
                    else:
                        if self.lastLegComplete:
                            self.totalRisk += self.gm.GetRisk(self.sLat, self.sLon)
                else:
                    if self.CollisionReason == 'RomsNanAtStart':
                        self.totalRisk += self.gm.GetRisk(self.sLat, self.sLon)
                    
                    tempX, tempY = self.gm.GetXYfromLatLon(np.array(latArray), np.array(lonArray))
                    if len(tempX) > 0 and len(tempY) > 0:
                        if self.CollisionReason == 'Obstacle' or self.CollisionReason == 'RomsNanLater':
                            self.totalRisk += self.GetRiskFromXY(tempX[-1:], tempY[-1:])
                            self.finX, self.finY = tempX[-1], tempY[-1]
                        plt.plot(tempX, tempY, self.lineType)
                    self.x_sims, self.y_sims = 0, 0
                    self.done = True
                    return self.totalRisk, True # Landed on beach!
                try:
                    self.a = (self.x_sims[0], self.y_sims[0])
                    self.finX,self.finY = self.a
                except IndexError:
                    self.done = True
                    return self.totalRisk, True # Landed on beach
                    #import pdb; pdb.set_trace()
                if self.lastLegComplete == True: # Finished simulating a leg.
                    i = i + 1
                    #if i > self.maxLengths:
                    #    self.CollisionReason = 'MaxHopsExceeded'
                    #    self.done = True
                else: # Since this is a re-entrant simulator... Get done here...
                    self.done = True
        else: # We did not get a policy here.
                self.CollisionReason = 'DidNotFindPolicy'
                self.done = True
        return self.totalRisk, False

        
''' Usage Example
yy,mm,dd,numDays = 2011,1,1,2
posNoise = 0.1
curNoise = 0.01
start,goal = (0,0),(6,2)
print 'Hello World!'
import gpplib.Utils
conf = gpplib.Utils.GppConfig('../../config.shelf.db')
saMdp = SA_MDP(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir)
saMdp.GetTransitionModelFromShelf(yy, mm, dd, numDays, posNoise, curNoise, '.')
saMdp.SetGoalAndInitTerminalStates(goal, 100.)
saMdp.doValueIteration(0.0001,25)
saMdp.DisplayPolicy()
plt.savefig('SAmdp.png')
saMdp.GetRomsData(yy, mm, dd, numDays, True)
saMdp.SimulateAndPlotMDP_PolicyExecution(start, goal, 0, True, 'r-')
'''