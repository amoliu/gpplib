'''
**MDP_class** - As the name suggests, this class creates an instance of MDPs - namely an MDP that
does Min-Risk planning.

It also depends upon the following modules:
    * 'Numpy<http://numpy.scipy.org/>' >= 1.6.0
    * 'Matplotlib<http://matplotlib.sourceforge.net/>' >= 0.9
    * 'Scipy<http://scipy.org/>' >= 0.9.0

See also Replanner_ , GenGliderModelUsingRoms_

'''
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import math
import re
import shelve
from   InterpRoms import * # This has our Trilinear interpolation
from   GenGliderModelUsingRoms import GliderModel

class MDP(object):
    """ Main MDP Class. Implementation of an MDP class that does minimum-risk planning.
    
    """
    def __init__(self,shelfName='RiskMap.shelf',sfcst_directory='../../../matlab/',dMax = 1.5):
        """ This function initializes the class.
        
            Args:
                * shelfName (str): Name of shelf-file that contains obstacle and risk maps
                * sfcst_directory (str): Directory in which ROMS small-forecast files have been stored.
        """
        self.gm = GliderModel(shelfName, sfcst_directory)
        self.Dmax = dMax
        self.maxLengths = 50
        self.numDays = 3
        self.acceptR = 0.6
        self.mdp = {}
        States = {}
        width, height = self.gm.Width, self.gm.Height
        #for j in range(0, height):
        #       for i in range(0, width):
        import networkx as nx
        self.g = self.gm.lpGraph.copy()
        for a in self.g.nodes():
                    i,j = self.GetXYfromNodeStr(a)
                    state_str = 'S_%d%d' % (i, j)
                    State = {}
                    State['x'] = i
                    State['y'] = j
                    States[state_str] = State
        self.mdp['States'] = States
        self.mdp['Obs'] = np.where(self.gm.riskMap >= 1., 1, 0)
        self.mdp['Rwd'] = -self.gm.riskMap
        np.set_printoptions(suppress=True)
        np.set_printoptions(precision=2)
        self.possibleCollision = False
        
    def GetXYfromNodeStr(self,nodeStr):
        ''' Convert from the name of the node string to the locations.
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
        if gmShelf.has_key('FinalLocs'):
            self.gm.FinalLocs = gmShelf['FinalLocs']
        if gmShelf.has_key('TracksInModel'):
            self.gm.TracksInModel = gmShelf['TracksInModel']
        self.gModel = {}
        self.gModel['TransModel']= gmShelf['TransModel']
        gmShelf.close()
        self.mdp['transProbs'] = self.gModel['TransModel']
        self.mdp['width'], self.mdp['height'] = self.gm.Width, self.gm.Height
    
    def GetRomsData(self,yy,mm,dd,numDays,UpdateSelf=True):
        ''' Loads up ROMs data from a particular day, for a certain number of days and supports self-update
            :param self:
            :param yy: year
            :param mm: month
            :param dd: day
            :param numDays: number of days the model is being built over
            :param UpdateSelf: Should the MDP update itself with the ROMS data being loaded?
            :type UpdateSelf: 
        '''
        u,v,time1,depth,lat,lon = self.gm.GetRomsData(yy,mm,dd,numDays)
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
        width, height = self.gm.Width, self.gm.Height
        if s['x']<0 or s['x']>=width:
            return False
        if s['y']<0 or s['y']>=height:
            return False
        return True
    
    def GetTrapStateForObs(self,x,y):
        ''' Get TrapStateForObstacles 
        '''
        State = {}
        State['x'],State['y'],State['trapped'] = x, y, False
        return State
    
    def SetGoalAndInitTerminalStates(self,goal,rewardVal=10):
        ''' Set the Goal location and initialize terminal states.
        '''
        TermStates=[]
        GState={}
        GState['x'],GState['y'],GState['trapped'] = goal[0], goal[1], False
        TermStates.append(GState)
        self.mdp['Rwd'] = -self.gm.riskMap
        self.mdp['Rwd'][goal[0],goal[1]] = rewardVal
        
        width, height = self.gm.Width, self.gm.Height
        # Also add obstacles as terminal states.
        for y in range(0,height):
            for x in range(0,width):
                if self.gm.GetObs(self.gm.lat_pts[x],self.gm.lon_pts[y]):
                    state = self.GetTrapStateForObs(x,y)
                    TermStates.append(state)
        self.mdp['TermStates'] = TermStates
    
    def identifyTerminalState(self,State):
        TermStates=self.mdp['TermStates']
        for i in range(0,len(TermStates)):
            if TermStates[i]['x']==State['x'] and TermStates[i]['y']==State['y'] :
                if not TermStates[i]['trapped']:
                    TermStates[i]['trapped']=True
                    return True,False,TermStates
                else:
                    return True,True,TermStates
        return False,False,TermStates   # Returns: isGoalState,isTrapped,TermStates
    
    def GetUtilityForStateTransition(self,State,sPrime):
        x,y = State['x'],State['y']
        xp,yp= sPrime['x'],sPrime['y']
        width,height=self.mdp['width'],self.mdp['height']
        Util = 0.
        totalProb = 0
        transProb = 0
        
        stateTrans = '%d,%d,%d,%d'%(x,y,xp,yp)
        if self.mdp['transProbs'].has_key(stateTrans):
            transProbs = self.mdp['transProbs'][stateTrans][2]
            tPSize = self.mdp['transProbs'][stateTrans][1]
            zeroLoc = self.mdp['transProbs'][stateTrans][0]
            
            stateAction={}
            Obs = self.mdp['Obs']
            # Iterate over all possible actions
            for j in range(0,int(tPSize)):
                for i in range(0,int(tPSize)):
                    stateAction['x'],stateAction['y'] = x+i-zeroLoc, y+j-zeroLoc
                    if i!=j:
                        if self.isOnMap(sPrime) and self.isOnMap(stateAction):
                            if not self.gm.ObsDetLatLon(self.gm.lat_pts[sPrime['y']],self.gm.lon_pts[sPrime['x']], \
                                                        self.gm.lat_pts[stateAction['y']],self.gm.lon_pts[stateAction['x']]):
                                transProb = transProbs[j][i]
                                totalProb += transProb
                                Util += transProb * self.mdp['U'][x+i-zeroLoc][y+j-zeroLoc]
        
        if totalProb !=1:
            transProb = 1-totalProb
            Util+=transProb * self.mdp['U'][x][y]
        #print Util
        return Util
    
    def CalculateTransUtilities(self, State):
        x, y = State['x'], State['y']
        width, height = self.mdp['width'], self.mdp['height']
        # We have 4 possible actions we can try. Up, Down, Left and Right.
        UtilVec = {}
        sPrime = {}
        for j in range(-1, 2):
            for i in range(-1, 2):
                if i != j:
                    sPrime['x'], sPrime['y'] = x + i, y + j
                    if not self.gm.GetObs(self.gm.lat_pts[y], self.gm.lon_pts[x]):
                        stateTrans = '%d,%d,%d,%d' % (x, y, x + i, y + j)
                        UtilVec[stateTrans] = self.GetUtilityForStateTransition(State, sPrime)
        return UtilVec
    
    def CalculateTransUtilitiesOld(self, State):
        x, y = State['x'], State['y']
        width, height = self.mdp['width'], self.mdp['height']
        # We have 4 possible actions we can try. Up, Down, Left and Right.
        UtilVec = {}
        sPrime = {}
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i != j:
                    sPrime['x'], sPrime['y'] = x + i, y + j
                    if not self.gm.GetObs(self.gm.lat_pts[y], self.gm.lon_pts[x]):
                        stateTrans = '%d,%d,%d,%d' % (x, y, x + i, y + j)
                        UtilVec[stateTrans] = self.GetUtilityForStateTransition(State, sPrime)
        return UtilVec
        
    def doValueIteration(self,eps,MaxRuns = 25 ):
        delta =0
        gamma = 1
        width,height = self.gm.Width, self.gm.Height
        U=np.zeros((width,height))
        Uprime = np.zeros((width,height))
        R=self.mdp['Rwd']
        print R
        self.mdp['U']=U
        self.mdp['Uprime']=Uprime
        
        for i in range(0,MaxRuns):
            print '------------------------------- Running Iteration: %d, Delta=%.3f.'%(i,delta)
            U=Uprime.copy()
            self.mdp['U']=U
            self.mdp['Uprime']=Uprime
            delta = 0
            for State in self.mdp['States'].values():
                Rwd = R[State['x']][State['y']]
                #print Rwd
                if not self.gm.GetObs(self.gm.lat_pts[State['y']],self.gm.lon_pts[State['x']]):
                    Utils = self.CalculateTransUtilities(State)
                    ExpUtilVec= Utils.values()#[item for sublist in Utils.values() for item in sublist]
                    maxExpectedUtility = max(ExpUtilVec)
                    isTermState,isTrapped,TermStateUpdate=self.identifyTerminalState(State)
                    if isTermState: # Don't give it a reward the second time around                    
                        if isTrapped:
                            Rwd = 0
                        else:
                            Rwd = R[State['x']][State['y']]
                            self.mdp['TermStates']=TermStateUpdate
                        Uprime[State['x']][State['y']]=Rwd + gamma * U[State['x']][State['y']]
                    else:
                        Uprime[State['x']][State['y']]=Rwd + gamma * maxExpectedUtility
                    
                    absDiff = abs(Uprime[State['x']][State['y']]-U[State['x']][State['y']])
                    if( absDiff>delta ):
                        delta = absDiff
           
            print 'delta=%f'%(delta)
            print 'U',U
            print 'Uprime',Uprime
            if (delta <= eps * (1-gamma)/gamma):
                print 'delta is smaller than eps %f. Terminating.'%(delta)
                break
        self.pol_tree = self.GetPolicyTreeForMDP()
    
    '''    
    def DisplayPolicy(self,FigHandle = None): # TODO: Check this up again... Most of the indices are reversed!!!
        width,height = self.gm.Width,self.gm.Height
        Xpolicy = np.zeros((width,height))
        Ypolicy = np.zeros((width,height))
        Xloc,Yloc = np.zeros((width,height)), np.zeros((width,height))
        Uprime = self.mdp['U']
        if self.mdp.has_key('TermStates'):
            TermStates= self.mdp['TermStates'][0]
        else:
            TermStates={}; TermStates['x']='None'; TermStates['y']=None
        if FigHandle==None:
            plt.figure()
        self.gm.PlotNewRiskMapFig()
        
        #for y in range(0,height):
        #    for x in range(0,width):
        for a in self.g.nodes():
                x,y = self.GetXYfromNodeStr(a) 
                Xloc[x][y],Yloc[x][y] = x,y
                UtilVec = np.zeros(10)
                maxUtil = -float('inf')
                k,maxU,maxV= 0,0,0
                if not self.gm.GetObs(self.gm.lat_pts[y],self.gm.lon_pts[x]) and not(TermStates['x']==x and TermStates['y']==y):
                    for j in range(-1,2):
                        for i in range(-1,2):
                            if (not(i==0 and j==0) and (x+i)>=0 and (x+i)<width and (y+j)>=0 and (y+j)<height \
                                and not self.gm.ObsDetLatLon(self.gm.lat_pts[y],self.gm.lon_pts[x],self.gm.lat_pts[y+j],self.gm.lon_pts[x+i])):
                                UtilVec[k] = Uprime[x+i][y+j]
                                if maxUtil<=UtilVec[k]:
                                    maxUtil = UtilVec[k]
                                    maxU,maxV = i,j
                                k=k+1
                    Xpolicy[x][y],Ypolicy[x][y] = 0.5*maxU, 0.5*maxV
        plt.quiver(Xloc,Yloc,Xpolicy,Ypolicy)
        plt.title('MDP Policy')
        return Xpolicy,Ypolicy
    '''
    
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
            
        if forceGoal==True:
            return self.goal[0],self.goal[1]
        else:
            return self.FindNearestNodeOnGraph()
    
    
    '''    
    def GetPolicyTreeForMDP(self):
        try:
            import pygraphviz as gv
        except ImportError:
            print 'pygraphviz not installed'
        try:
            import networkx as nx
            self.UseNetworkX = True
        except ImportError:
            print 'networkX not installed. Please install it!'
            
        width, height = self.gm.Width, self.gm.Height
        
        Uprime = self.mdp['Uprime']
        TermStates= self.mdp['TermStates'][0]
        if self.UseNetworkX == True:
            self.gm2 = nx.DiGraph()
        else:
            self.gm2 = digraph()
        
        for y in range(0,height):
            for x in range(0,width):
                #if mdp['Obs'][x][y]!=1:
                if not self.gm.GetObs(self.gm.lat_pts[y],self.gm.lon_pts[x]): #mdp['Obs'][y][x]!=1:
                    if self.UseNetworkX == True:
                        self.gm2.add_node('(%d,%d)'%(x,y))
                    else:
                        self.gm2.add_nodes(['(%d,%d)'%(x,y)])
                        self.gm2.add_node_attribute('(%d,%d)'%(x,y),('position',(x,y)))
        for y in range(0,height):
            for x in range(0,width):
                if not self.gm.GetObs(self.gm.lat_pts[y],self.gm.lon_pts[x]):
                    #if mdp['Obs'][x][y]!=1:
                    maxUtil = -float('inf')
                    UtilVec = np.zeros(20)
                    k,maxU,maxV = 0,0,0
                    if not (TermStates['x']==x and TermStates['y']==y):
                        for j in range(-1,2):
                            for i in range(-1,2):
                                #if (not(i==0 and j==0) and (x+i)>=0 and (x+i)<width and (y+j)>=0 and (y+j)<height and mdp['Obs'][x+i][y+j]!=1):
                                if (not(i==0 and j==0) and (x+i)>=0 and (x+i)<width and (y+j)>=0 and (y+j)<height \
                                    and not self.gm.ObsDetLatLon(self.gm.lat_pts[y],self.gm.lon_pts[x],self.gm.lat_pts[y+j],self.gm.lon_pts[x+i])):
                                    #UtilVec[k] = Uprime[x+i][y+j]
                                    UtilVec[k] = Uprime[x+i][y+j]
                                    if maxUtil<=UtilVec[k]:
                                        maxUtil = UtilVec[k]
                                        maxU,maxV = i,j
                                    k=k+1
                        if not(maxU==0 and maxV==0):
                            if self.UseNetworkX == False:
                                self.gm2.add_edge(('(%d,%d)'%(x,y),'(%d,%d)'%(x+maxU,y+maxV)),wt = maxUtil)
                            else:
                                self.gm2.add_edge('(%d,%d)'%(x,y),'(%d,%d)'%(x+maxU,y+maxV),weight=maxUtil)
        
        if self.UseNetworkX == False:
            dot = write(self.gm2)
            G = gv.AGraph(dot)
            G.layout(prog = 'dot')
            G.draw('SCB_MDP_MSG.png')
        return self.gm2
        
    
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
        
        if forceGoal==True:
            return self.goal[0],self.goal[1]
        else:
            return self.FindNearestNodeOnGraph(curNode)
    '''
        
    def FindNearestNodeOnGraph(self,curNode):
        nearest_dist = float('inf')
        nearest_node = (None,None)
        for a in self.g.nodes():
            i,j = self.GetXYfromNodeStr(curNode)
            x,y = self.GetXYfromNodeStr(a)
            dist = math.sqrt((i-x)**2+(j-y)**2)
            if (dist<nearest_dist):
                if not self.gm.ObsDetLatLon(self.gm.lat_pts[j],self.gm.lon_pts[i], \
                                                            self.gm.lat_pts[y],self.gm.lon_pts[x]):
                    nearest_dist = dist
                    nearest_node =  (x,y)
        return nearest_node
    
    def GetRiskFromXY(self,x,y):
        lat,lon = self.gm.GetLatLonfromXY(x,y)
        return self.gm.GetRisk(lat,lon)
    
    def SimulateAndPlotMDP_PolicyExecution(self,start,goal,k,newFig=True,lineType='r-',NoPlot='False'):
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
        
        a= start
        done = False
        i=0
        #x_sims,y_sims = np.zeros((24*gm.numDays,1)),np.zeros((24*gm.numDays,1))
        if k>=(24*self.gm.numDays):
           k = 24*self.gm.numDays-1
        x_sims,y_sims = 0,0
        self.finX,self.finY = start[0],start[1]
        #import pdb; pdb.set_trace()
        while (not done):
            self.numHops+=1
            try:
                bx,by = self.GetPolicyAtCurrentNode('(%d,%d)'%(int(a[0]+0.5),int(a[1]+0.5)),'(%d,%d)'%(goal[0],goal[1]))
            except TypeError:
                bx,by = None, None
            if bx!=None and by!=None:
                b = (bx,by)
                #tempRisk = self.GetRiskFromXY(bx,by)
                #totalRisk+=tempRisk
                self.distFromGoal = math.sqrt((a[0]-goal[0])**2+(a[1]-goal[1])**2)
                if self.distFromGoal<=self.acceptR:
                    self.isSuccess = True
                    done = True
                sLat,sLon = self.gm.GetLatLonfromXY(a[0],a[1])
                gLat,gLon = self.gm.GetLatLonfromXY(b[0],b[1])
                tStart = k + self.totalTime/3600.
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
                    a = (x_sims[0],y_sims[0])
                    self.finX,self.finY = a
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
    
    '''
        The Re-Entrant version of the MDP - Policy Execution. 
    '''
    def SimulateAndPlotMDP_PolicyExecution_R(self,simulTime=-1,PostDeltaSimCallback=None,PostSurfaceCallbackFn=None):
        i = self.Indx
        tStart = self.startT
        #self.lastLegComplete = self.gm.doneSimulating;
        if self.lastLegComplete == True:
                self.numHops += 1
                try:
                    self.lastTransition = [(int(self.a[0]+0.5),int(self.a[1]+0.5)),(self.bx,self.by)]
                    self.bx, self.by = self.GetPolicyAtCurrentNode('(%d,%d)' % (int(self.a[0]), int(self.a[1])), '(%d,%d)' % (self.goal[0], self.goal[1]))
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
                    self.x_sims, self.y_sims = tempX[-1:][0], tempY[-1:][0] 
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
