from gpplib.GliderFileTools import *
import random
from sets import Set
import gpplib
from gpplib.Utils import *
from gpplib.GenGliderModelUsingRoms import GliderModel
from gpplib.GenGliderModelUsingRoms import *
from gpplib.StateActionMDP import *
from gpplib.LatLonConversions import *
from gpplib.PseudoWayptGenerator import *
import datetime
import ftplib
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

class SA_NS_MDP( object ):
    def __init__(self,shelfName='RiskMap3.shelf',sfcst_directory='./',dMax=1.5):
        ''' Args:
            * shelfName (str) : Name of shelf-file that contains obstacle and risk maps.
            * sfcst_directory( str ): Directory in which ROMS small forecast files have been stored.
        '''
        self.gm = GliderModel(shelfName,sfcst_directory)
        self.gs = GliderSimulator(shelfName,sfcst_directory)
        self.gsR = GliderSimulator(shelfName,sfcst_directory)
        
        self.Dmax = dMax
        self.maxLengths = 50
        self.acceptR = 0.6
        
        self.locG =  self.gm.lpGraph.copy()
        for a in self.locG.nodes():
            print a
        np.set_printoptions(precision=2)
        self.possibleCollision = False
        self.Rwd = {}
        self.mdp = {}
        self.gamma = 1.0
        self.maxDepth = 80.
        self.w_r = -1.
        self.w_g = 10.
        self.theta = {}
        self.theta['w_r'], self.theta['w_g'] = self.w_r, self.w_g
        self.RewardsHaveChanged = False
        self.tMax = 48
        self.tExtra = 12
        #self.ReInitializeMDP()
        
    def GetTransitionModelFromShelf(self,yy,mm,dd,s_indx,e_indx,posNoise=None,currentNoise=None,shelfDirectory='.'):
        """ Loads up Transition models from the shelf for a given number of days, starting from a particular day, and a given amount of noise in position and/or a given amount of noise in the current predictions. We assume these models have been created earlier using ProduceTransitionModels.
            
            Args:
                * yy (int): year
                * mm (int): month
                * dd (int): day
                * s_indx (int): start index for the transition model
                * e_indx (int): end index for the transition model
                * posNoise (float): Amount of std-deviation of the random noise used in picking the start location
                * currentNoise (float): Amount of prediction noise in the ocean model
                * shelfDirectory (str): Directory in which the Transition models are located.
            
            Updates:
                * self.gm.FinalLocs: Stores the final locations 
        """
        print 'Loading Transition model from Shelf'
        self.posNoise = posNoise; 
        self.currentNoise = currentNoise 
        #import pdb; pdb.set_trace()
        if posNoise==None and currentNoise==None:
            gmShelf = shelve.open('%s/gliderModelNS_GP_%04d%02d%02d_%d_%d.shelf'%(shelfDirectory,yy,mm,dd,s_indx,e_indx), writeback=False )
        if posNoise!=None:
            if currentNoise!=None:
                gmShelf = shelve.open('%s/gliderModelNS_GP_%04d%02d%02d_%d_%d_%.3f_RN_%.3f.shelf'%(shelfDirectory,yy,mm,dd,s_indx,e_indx,posNoise,currentNoise),writeback=False)
            else:
                gmShelf = shelve.open('%s/gliderModelNS_GP_%04d%02d%02d_%d_%d_%.3f.shelf'%(shelfDirectory,yy,mm,dd,s_indx,e_indx,posNoise), writeback=False)
        if posNoise==None and currentNoise!=None:
            gmShelf=shelve.open('%s/gliderModelNS_GP_%04d%02d%02d_%d_%d_RN_%.3f.shelf'%(shelfDirectory,yy,mm,dd,s_indx,e_indx,currentNoise), writeback=False)     
        self.gm.TransModel = gmShelf['TransModel']
        #if gmShelf.has_key('FinalLocs'):
        self.gm.FinalLocs = gmShelf['FinalLocs']
        if gmShelf.has_key('TracksInModel'):
            self.gm.TracksInModel = gmShelf['TracksInModel']
        gmShelf.close()
        # Now that we have loaded the new transition model, we better update our graph.
        self.ReInitializeMDP()    
    
        
    def ReInitializeMDP(self):
        self.mdp['U'] = np.zeros((self.tMax+ self.tExtra, self.gm.Height, self.gm.Width,  ))
        self.mdp['Uprime'] = np.zeros((self.tMax + self.tExtra, self.gm.Height, self.gm.Width ))
        self.locG = self.gm.lpGraph.copy()
        self.BuildTransitionGraph()
        
        
    def BuildTransitionGraph(self):
        ''' Compute the transition graph from all the available edges in the transition model '''
        self.g = nx.DiGraph()
        for a in self.locG.nodes():
            for b in self.locG.nodes():
                if a != b:
                    i, j = self.GetXYfromNodeStr(a); x,y = self.GetXYfromNodeStr(b)
                    for t1 in range(0,self.tMax):
                        edge_str = '%d,%d,%d,%d,%d'%(t1,i,j,x,y)
                        if self.gm.TransModel.has_key(edge_str):
                            W_,H_,T_ = self.gm.TransModel[edge_str][2].shape
                            rwd = self.GetRewardForStateAction((t1,i,j),edge_str)
                            for t2 in range(t1,t1+T_):
                                self.g.add_edge((t1,i,j),(t2,x,y),weight=rwd,trapped=False)
        # Store a copy of g, so that we can re-run the MDP when needed. This
        # is in case we end up adding multiple goals etc.
        self.g_copy = self.g.copy()
                                
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
                                
    def GetRewardForStateAction(self,state,action):
        ''' Get the reward for a state-action pair. Use a dictionary
        to perform a lookup if we have already computed this earlier.
        Args:
            state (tuple) : node we are currently evaluating. (t1,x1,y1)
            action (tuple): action (or edge) we are currently computing the reward for.
            
        Updates:
            self.Rwd[state-action-pair] with computed reward.
        
        Returns:
            self.Rwd[state-action-pair] if previously computed, else compute it and return result.
        '''
        OffMapNotObs = True # Treat locations off the map as high-risk locations
        state_action_pair = (state,action)
        if self.Rwd.has_key( state_action_pair ) and not self.RewardsHaveChanged:
            return self.Rwd[ state_action_pair ]
        else:
            t,x,y = state
            X,Y,T = self.gm.FinalLocs[ action ]
            tot_rwd = 0.
            totNum = len( np.nonzero(self.gm.FinalLocs[ action ][0][0]))
            for i in range(0,totNum):
                lat,lon = self.gm.GetLatLonfromXY(x+X[i],y+Y[i])
                riskVal = self.gm.GetRisk(lat,lon,OffMapNotObs) * self.w_r
                tot_rwd += riskVal
            
            if totNum > 0:
                self.Rwd[ state_action_pair ] = tot_rwd / totNum
            else:
                self.Rwd[ state_action_pair ] = tot_rwd
            print state, action, self.Rwd[ state_action_pair ]
            self.RewardsHaveChanged = False
            
            return self.Rwd[ state_action_pair ]
        
    
    def SetGoalAndInitTerminalStates(self, goal, rewardVal = 10. ):
        ''' Set the goal location and initialize everything including terminal states.
        
        Args:
            goal(x,y) : tuple with (x,y) given in graph coordinates.
            rewardVal (float) : Reward value for getting to the goal. Defaults to 10.
        '''
        self.ReInitializeMDP()
        self.mdp['U'][goal[1],goal[0]] = rewardVal
        self.mdp['Uprime'] = self.mdp['U'].copy()
        self.goal = goal
        self.goalReached = False
        ''' The goal is a trapping state, so we remove all the out-going edges from the goal, and
        add a self-edge with weight zero. '''
        for t1 in range(0,self.tMax):
            for u,v,d in self.g.in_edges((t1,goal[0],goal[1]),data=True):
                d['weight'] = rewardVal
                d['trapped'] = False
                d['goal_edge'] = True
                
            for u,v,d in self.g.out_edges((t1,goal[0],goal[1]),data=True):
                self.g.remove_edge( u, v )
                self.g.add_edge( (t1,goal[0],goal[1]),(t1,goal[0],goal[1]),weight=0.)
    
    def SetGoalAndRewardsAndInitTerminalStates(self,goal,theta):
        ''' Set the goal location and initialize everything including terminal states.
        
        Args:
            goal(x,y) : tuple with (x,y) given in graph coordinates.
            theta (dict) : theta['w_r'] - reward for normal states, 
                           theta['w_g'] - reward for goal states
        '''
        print 'Using new theta:',theta
        self.w_r = theta['w_r']
        self.w_g = theta['w_g']
        self.theta = theta
        self.RewardsHaveChanged = True
        
        self.ReInitializeMDP()
        for t1 in range(0,self.tMax):
            self.mdp['U'][(t1,goal[1],goal[0])] = self.w_g
            self.mdp['Uprime'] = self.mdp['U'].copy()
            self.goal = goal
            self.goalReached = False
            ''' The goal is a trapping state, so we remove all the out-going edges from the goal, and
            add a self-edge with weight zero. '''
            for u,v,d in self.g.in_edges( (t1,goal[0],goal[1]), data=True ):
                d['weight'] = self.w_g
                d['goal_edge'] = True
                
            for u,v,d in self.g.out_edges( (t1,goal[0],goal[1]), data=True):
                self.g.remove_edge( u, v )
            self.g.add_edge( (t1,goal[0],goal[1]), (t1,goal[0],goal[1]), weight=0. )
    
    
    def doValueIteration(self, eps = 0.00001, MaxRuns=50 ):
        ''' Perform Value Iteration. 
        Args:
            eps( float ): epsilon -> a small value which indicates the maximum change in utilities over
            an iteration.
            MaxRuns (int): maximum number of runs to do value iteration for. If negative, we will quit when the
                    epsilon criterion is reached.
                    
        Note: set the value of gamma between 0 and 1. Gamma is 1 by default.
        '''
        print 'Doing Value Iteration'
        for i in range( 0, MaxRuns ):
            print 'Iteration %d'%(i)
            iterStartTime = time.time()
            lastTime = time.time()
            self.mdp['U'] = self.mdp['Uprime'].copy()
            self.delta = 0.
            for nodeNum,node in enumerate(self.g.nodes()):
                t1,x,y = node
                Utils = self.CalculateTransUtilities( (t1,x,y) )
                ExpUtilVec = Utils.values()
                if nodeNum%10==0:
                    print '%d) %.3f'%(nodeNum,time.time()-iterStartTime),(t1,x,y)
                #print t1,x,y,ExpUtilVec
                #import pdb; pdb.set_trace()
                if len(ExpUtilVec):
		  try:
                    maxExpectedUtility = np.max(ExpUtilVec)
                    #print x,y,maxExpectedUtility
                    self.mdp['Uprime'][t1,y,x] = maxExpectedUtility
		  except ValueError:
		    import pdb; pdb.set_trace()
                    maxExpectedUtility = np.max(ExpUtilVec.all())
		    print maxExpectedUtility,ExpUtilVec
                
                absDiff = abs(self.mdp['Uprime'][t1,y,x]-self.mdp['U'][t1,y,x])
                if(absDiff>self.delta):
                    self.delta = absDiff
            print 'delta=%f'%(self.delta)
            print 'U',self.mdp['U']
            if (self.delta<=eps*(1-self.gamma)/self.gamma):
                print 'delta is smaller than eps %f. Terminating.'%(self.delta)
                break
            iterEndTime = time.time()
            print 'Took %f seconds for iteration %d.'%(iterEndTime-iterStartTime, i)
        # Get Policy tree.
        self.GetPolicyTreeForMDP()
                
                
    def CalculateTransUtilities(self,state):
        ''' Get all the transition utilities based upon all the actions we can take from this state.
        Args:
            state( t, x, y ) : tuple containing time, x and y locations in graph co-ordinates.
        '''
        t1,x,y = state
        # Transition graph should have all the outgoing edges from this place via neighbors of this node.
        # To see weights in graph we can do self.g[(i,j)][(k,l)]['weight']
        UtilVec= {}
        for u,v,d in self.g.out_edges( (t1,x,y), data = True ):
            
            sa_rwd = d['weight']
            ''' Goals are trapping terminal states '''
            if d.has_key('goal_edge'):
                if self.goalReached:
                    sa_rwd = 0.
                else:
                    self.goalReached = True
                    # Now, set the weight of this edge to zero.
                    d['weight'] = 0.
                    d['trapped'] = True
                    
            t1,x1,y1 = u; t2,x2,y2 = v
            UtilVec[(u,v)] = sa_rwd + self.gamma * self.GetUtilityForStateTransition( u, v )
        return UtilVec
    
    def GetUtilityForStateTransition(self, state, state_prime):
        ''' Compute the utility for performing the state transition of going from state to state_prime.
        
        Args:
            state( tuple of int, int, int ) : state t, x, y in planning graph coods.
            state_prime (int, int, int) : state_prime t,x,y in planning graph coods.
            
        Returns:
            Utility (float) : utility for this state transition. '''
        t1,x,y = state
        tp,xp,yp= state_prime
        width, height = self.gm.Width, self.gm.Height
        Util = 0.
        totalProb = 0
        transProb = 0
        
        if yp == self.goal[1] and xp==self.goal[0]:
            return self.mdp['U'][t1,y,x]
        
        stateTrans = '%d,%d,%d,%d,%d'%(t1,x,y,xp,yp)
    
        if self.gm.TransModel.has_key( stateTrans ):
            transProbs = self.gm.TransModel[ stateTrans ][2]
            tPSize = self.gm.TransModel[ stateTrans ][1]
            zeroLoc = self.gm.TransModel[ stateTrans ][0]
            W_,H_,T_ = self.gm.TransModel[ stateTrans ][2].shape
            # iterate over all possible actions
            for j in range( 0 , int(tPSize)):
                for i in range( 0, int(tPSize)):
                    for t2 in range( 0, T_ ):
                        state_action = ( t1, x+i-zeroLoc, y+j-zeroLoc )
                        if i!=j:
                            if self.isOnMap(state_prime) and self.isOnMap(state_action):
                                if not self.gm.ObsDetLatLon(self.gm.lat_pts[yp],self.gm.lon_pts[xp], \
                                    self.gm.lat_pts[y], self.gm.lon_pts[x]):
                                    Util += transProbs[j][i][t2] * self.mdp['U'][t1+t2,y+j-zeroLoc,x+i-zeroLoc]
                                    transProb += transProbs[j][i][t2]
        if totalProb!=1:
            transProb = 1-totalProb
            Util += transProb * self.mdp['U'][ t1,y,x ]
        return Util
    
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
            s (tuple(t,x,y) ) : tuple with  't','x' and 'y' values
        '''
        t,x,y = s
        if x<0 or x>=self.gm.Width:
            return False
        if y<0 or y>=self.gm.Height:
            return False
        return True
    
    ''' -------------------------------------------------------------------------------------------
    ---------------------------------- Code to create the policy tree -----------------------------   
    --------------------------------------------------------------------------------------------'''
    def DisplayPolicyAtTimeT(self,t,FigHandle = None):
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
        plt.quiver(Xloc,Yloc,Xpolicy,Ypolicy,scale=10*math.sqrt(maxU**2+maxV**2))
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
            t1,x,y = a
            UtilVec = np.zeros(10)
            maxUtil = -float('inf')
            k,maxU,maxV = 0,0,0
            for u,v,d in self.g.out_edges(a,data=True):
                t2,i,j = v
                UtilVec[k] = Uprime[ v ]
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
        #self.gLat, self.gLon = self.gm.GetLatLonfromXY(self.b[0], self.b[1])
        #if (self.gLat,self.gLon)!=self.lastGoal:
        #    self.lastGoal = (self.gLat,self.gLon)
        #    self.PolicyToGoal.append(lastGoal)
        targetX,targetY = None,None
        print 'CurNode:',curNode
        print 'Goal:',self.goal
        #print 'curNode :%s, goal: %s'%(str(curNode),str(goal))
        print 'Current Node: (%f,%f)'%(curNode[0],curNode[1])
        print 'Goal Node: (%f,%f)'%(self.goal[0],self.goal[1])
        #import pdb;pdb.set_trace()
        if curNode==self.goal:
            targetX,targetY = self.goal[0],self.goal[1]
            #return self.goal[0], self.goal[1]
        else:
            try:
                neighborNode = self.gm2.neighbors('(%d,%d)'%(int(curNode[0]+0.5),int(curNode[1]+0.5)))
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
                    targetX,targetY = int(m.group(1)),int(m.group(2))
                    
        if targetX==None and targetY==None:
            targetX,targetY = self.FindNearestNodeOnGraph(curNode)
        
        targetLat, targetLon = self.gm.GetLatLonfromXY(targetX,targetY)
        if (targetX,targetY) != self.lastGoal:
            self.lastGoal = (targetX,targetY)
            self.PolicyToGoal.append((targetLat,targetLon))
    
        print 'Next Node: (%f,%f)'%(targetX, targetY)
        return targetX,targetY
    
    def FindNearestNodeOnGraph(self,curNode):
        nearest_dist = float('inf')
        best_utility = -float('inf')
        nearest_node = (None,None)
        for a in self.g.nodes():
            i,j = curNode
            x,y = self.GetXYfromNodeStr(a)
            dist = math.sqrt((i-x)**2+(j-y)**2)
            #if not self.gm.ObsDetLatLon(self.gm.lat_pts[j],self.gm.lon_pts[i], \
            #                    self.gm.lat_pts[y],self.gm.lon_pts[x]):
            lat1,lon1 = self.gm.GetLatLonfromXY(i,j)
            lat2,lon2 = self.gm.GetLatLonfromXY(x,y)
            
            if not self.gm.ObsDetLatLon(lat1,lon1,lat2,lon2):
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
        self.PolicyToGoal = []
        self.lastGoal = (None,None)
        
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
        
        self.PolicyToGoal = [] # A new addition which uses the simulated policy to goal
                                # to have a policy look-ahead so that in case
                                # the glider does not communicate back, there is a 
                                # fall-back plan for it toward the goal.
        self.lastGoal = (None,None)
        

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
                    self.bx,self.by = self.GetPolicyAtCurrentNode((self.a[0],self.a[1]),(self.bx,self.by))
                    if PostSurfaceCallbackFn != None:
                        PostSurfaceCallbackFn(self.latArray,self.lonArray)
                    self.b = (self.bx, self.by)
                    self.sLat, self.sLon = self.gm.GetLatLonfromXY(self.a[0], self.a[1])
                    self.gLat, self.gLon = self.gm.GetLatLonfromXY(self.b[0], self.b[1])
                    if (self.gLat,self.gLon)!=self.lastGoal:
                        self.lastGoal = (self.gLat,self.gLon)
                        self.PolicyToGoal.append(self.lastGoal)
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
    
if __name__=='__main__':
    yy,mm,dd = 2013,7,29
    posNoise = 0.001
    curNoise = None
    start,goal = (0,0), (6,2)
    print 'State Action Non-Stationary MDP'
    import gpplib.Utils
    conf = gpplib.Utils.GppConfig('../../config.shelf')
    saNS_Mdp = SA_NS_MDP(conf.myDataDir+'RiskMap3.shelf',conf.romsDataDir)
    saNS_Mdp.GetTransitionModelFromShelf( yy, mm, dd, 0, 48, posNoise, curNoise, conf.myDataDir+'/gliderModelNS/' )
#    saNS_Mdp.SetGoalAndInitTerminalStates(goal, 100.)
#    saNS_Mdp.doValueIteration(0.0001,25)
#    saNS_Mdp.DisplayPolicy()
#    plt.savefig('SAmdp.png')
#    saNS_Mdp.GetRomsData(yy, mm, dd, numDays, True)
#    saNS_Mdp.SimulateAndPlotMDP_PolicyExecution(start, goal, 0, True, 'r-')
