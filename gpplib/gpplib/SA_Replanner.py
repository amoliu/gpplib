'''
**StateAction_Replanner class** - This is a class that helps do re-planning. There are two basic 
types of planning that are supported and both are based upon shortest-paths.

See also `MDP Class_` ,  GenGliderModelUsingRoms_

'''
import numpy as np
import matplotlib.pyplot as plt
import os,sys,math,re
import shelve
from InterpRoms import *
from Simulate import *
from GenGliderModelUsingRoms import GliderModel

class SA_Replanner(object):
    ''' Replanner - A class that executes one of two types of planners (Min-Risk or Min-Expected-Risk).
    The replanning stems from the fact that when the robot surfaces at the waypoint it thinks
    it hit, it replans and resumes execution (at-least during simulation of such a planner).
    '''
    def __init__(self,shelfName='RiskMap.shelf',sfcst_directory='./',dMax = 1.5):
        self.gm = GliderModel(shelfName,sfcst_directory) # Initializes risk, obs maps.
        self.gs = GliderSimulator(shelfName,sfcst_directory)
        self.Dmax = dMax
        self.maxLengths = 50
        self.numDays = 3
        self.acceptR = 0.6
        self.maxDepth = 60.
        self.UseNetworkX = None
        self.SARisks={}
        try:
            if self.UseNetworkX == None:
                import networkx as nx
                self.UseNetworkX = True
        except ImportError:
            print 'Please install networkX'
            pass
    
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
        self.posNoise = posNoise; self.currentNoise = currentNoise
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
        self.gm.FinalLocs = gmShelf['FinalLocs']
        self.gm.TracksInModel = gmShelf['TracksInModel']
        self.gModel = {}
        self.gModel['TransModel'] = gmShelf['TransModel']
        gmShelf.close()
        
    def GetRomsData(self,yy,mm,dd,numDays,UpdateSelf=True,usePredictionData=False):
        useNewFormat = True
        u,v,time1,depth,lat,lon = self.gs.gm.GetRomsData(yy,mm,dd,numDays,useNewFormat,usePredictionData)
        u,v,time1,depth,lat,lon = self.gm.GetRomsData(yy,mm,dd,numDays,useNewFormat,usePredictionData)
        self.u,self.v,self.time1,self.depth,self.lat,self.lon = u,v,time1,depth,lat,lon
        self.numDays = numDays
        return u,v,time1,depth,lat,lon
    
    def isOnMapRP(self,s):
        width, height = self.gm.Width, self.gm.Height
        if s[0]<0 or s[0]>=width:
            return False
        if s[1]<0 or s[1]>=height:
            return False
        return True
    
    def GetExpRiskForStateAction(self,state_str,action_str):
        ''' Get the expected risk for a state-action pair.We use a dictionary here to 
        perform a lookup if we have already computed this earlier.
        
        Args:
            state (node_str) :
        '''
        OffMapNotObs = False
        state_action_str = '%s_%s'%(state_str,action_str)
        if self.SARisks.has_key(state_action_str):
            return self.SARisks[state_action_str]
        else:
            m=re.match('([0-9\.]+),([0-9\.]+)',state_str)
            if m:
                x,y = float(m.group(1)),float(m.group(2))
            X = self.gm.FinalLocs[action_str][0]; Y = self.gm.FinalLocs[action_str][1]
            tot_cost = 0
            for i in range(0,len(X)):
                lat,lon = self.gm.GetLatLonfromXY(x+X[i],y+Y[i])
                #print X[i],Y[i],lat,lon
                tot_cost += self.gm.GetRisk(lat,lon,OffMapNotObs)
            self.SARisks[state_action_str] = tot_cost
            return self.SARisks[state_action_str]
    
    def CreateExpRiskGraph(self):
        import networkx as nx
        self.g = self.gm.lpGraph.copy()

        OffMapNotObs = False
        for a in self.g.nodes():
            for b in self.g.nodes():
                x,y = self.GetXYfromNodeStr(a)
                i,j = self.GetXYfromNodeStr(b)
                if a!=b:
                    if self.gm.FinalLocs.has_key('%d,%d,%d,%d'%(x,y,i,j)):
                        expRisk = self.GetExpRiskForStateAction('%d,%d'%(x,y),'%d,%d,%d,%d'%(x,y,i,j))
                        if expRisk !=None:
                            self.g.add_edge('(%d,%d)'%(x,y),'(%d,%d)'%(i,j),weight=expRisk)
                            print 'Added edge (%d,%d) to (%d,%d) with weight=%.2f'%(i,j,x,y,expRisk)
        return self.g
    
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
        '''
        m = re.match('([0-9]+),([0-9]+),([0-9]+),([0-9]+)',edgeStr)
        x1,y1,x2,y2 = None,None,None,None
        if m:
            x1,y1,x2,y2 = int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4))
        return x1,y1,x2,y2
    
    def CreateGraphUsingProximityGraph(self,graphType='MinExpRisk'):
        import networkx as nx
        self.g = nx.DiGraph()
        
        self.g = self.gm.lpGraph.copy()
        
        for a in self.g.nodes():
            for b in self.g.nodes():
                if a!=b:
                    i,j = self.GetXYfromNodeStr(a); x,y = self.GetXYfromNodeStr(b)
                    if math.sqrt((i-x)**2+(j-y)**2)<=self.Dmax:
                        #print 'Considering: (%d,%d) to (%d,%d):'%(i,j,x,y)
                        if self.gm.ObsDetLatLon(self.gm.lat_pts[j],self.gm.lon_pts[i],self.gm.lat_pts[y],self.gm.lon_pts[x])==False:
                            if graphType == 'MinExpRisk':
                                expRisk = self.GetExpRisk((i,j),(x,y))
                                if expRisk !=None:
                                    self.g.add_edge('(%d,%d)'%(i,j),'(%d,%d)'%(x,y),weight=expRisk)
                                    #print 'Added edge (%d,%d) to (%d,%d) with weight=%.2f'%(i,j,x,y,expRisk)
                                else:
                                    print 'Rejected edge (%d,%d) to (%d,%d) with weight=None'%(i,j,x,y)
                            elif graphType == 'MinRisk':
                                riskVal = self.gm.GetRisk(self.gm.lat_pts[y],self.gm.lon_pts[x])
                                if riskVal!=None:
                                    self.g.add_edge('(%d,%d)'%(i,j),'(%d,%d)'%(x,y),weight=riskVal)
        ### If we want to write this graph out.
        #dot = write(g)
        #G = gv.AGraph(dot)
        #G.layout(prog ='dot')
        #G.draw('SCB.png')
        return self.g
    
    def CreateMinRiskGraph(self):
        '''
        A ROMS unaware planner. This planner totally avoids locations 
        
        '''
         # Short-circuit this!
        return self.CreateGraphUsingProximityGraph('MinRisk')
        
        # This is what we used to do earlier. Won't be running
        # unless we actually want it to.
        
        import networkx as nx
        self.g = nx.DiGraph()
        
        for j in range(0,self.gm.Height):
            for i in range(0,self.gm.Width):
                if self.UseNetworkX:
                    self.g.add_node('(%d,%d)'%(i,j))
                else:
                    self.g.add_nodes(['(%d,%d)'%(i,j)])
                    self.g.add_node_attribute('(%d,%d)'%(i,j),('position',(i,j)))
        
        for j in range(0,self.gm.Height):
            for i in range(0,self.gm.Width):
                for y in range(0,self.gm.Height):
                    for x in range(0,self.gm.Width):
                        if math.sqrt((i-x)**2+(j-y)**2)<=self.Dmax:
                            if self.gm.ObsDetLatLon(self.gm.lat_pts[j],self.gm.lon_pts[i],self.gm.lat_pts[y],self.gm.lon_pts[x])==False:
                                riskVal = self.gm.GetRisk(self.gm.lat_pts[y],self.gm.lon_pts[x])
                                if riskVal!=None:
                                    if self.UseNetworkX==True:
                                            self.g.add_edge('(%d,%d)'%(i,j),'(%d,%d)'%(x,y),weight=riskVal)
                                    else:
                                            self.g.add_edge(('(%d,%d)'%(i,j),'(%d,%d)'%(x,y)),wt=riskVal)
        return self.g
    
    def GetShortestPathMST(self,goal):
        ''' Find the shortest path Minimum-Spanning Tree
        '''
        if self.g!= None:
            if self.UseNetworkX:
                import networkx as nx
                self.sp_mst = nx.all_pairs_dijkstra_path(self.g)
                self.dist = nx.all_pairs_dijkstra_path_length(self.g)
            else:
                from pygraph.algorithms.minmax import shortest_path
                self.sp_mst, self.dist = shortest_path(self.g,'(%d,%d)'%(goal[0],goal[1]))
            return self.sp_mst, self.dist
        else:
            print 'CreateExpRiskGraph first before calling GetShortestPathMST(goal)'
            return None, None
    
    def GetPathXYfromPathList(self,path2goal):
        ''' Find the path in two lists (pathX,pathY) from the string values of path-list
        '''
        pathX,pathY = [],[]
        for pathEl in path2goal:
            m = re.match('\(([0-9]+),([0-9]+)\)', pathEl)
            if(m):
                pathX.append(int(m.group(1)))
                pathY.append(int(m.group(2)))
        return pathX,pathY
    
    def BackTrackNxPath(self,source,goal):
        source_str = '(%d,%d)'%(source[0],source[1])
        goal_str = '(%d,%d)'%(goal[0],goal[1])
        try:
            path2goal = self.sp_mst[source_str][goal_str]
        except KeyError:
            return None, None, None
        pathX,pathY = self.GetPathXYfromPathList(path2goal)
        return path2goal, pathX, pathY
    
    def BackTrackPath(self,mst,source):
        # source and goal are specified as tuples
        #import pdb; pdb.set_trace()
        source_str = '(%d,%d)'%(source[0],source[1])
        path2goal = []
        pathX,pathY = [],[]
        path_str = source_str  
        path2goal.append(path_str) 
        try:
            while(mst[path_str]!=None):
                    path_str = mst[path_str]
                    path2goal.append(path_str)
                    #path2goal.reverse()
            print path2goal
            pathX,pathY = self.GetPathXYfromPathList(path2goal)
        except KeyError:
                return None, None, None
        return path2goal, pathX, pathY
    
    def PlotMRpaths(self,goal,figHandle=None):
        if figHandle==None:
            fig = plt.figure()
        else:
            fig = figHandle
        plt.title('Plot of SA - Min-Exp Risk MST (Goal at:(%d,%d))'%(goal[0],goal[1]))
        #plt.imshow(rMap.transpose()+0.5,origin='upper')
        #plt.imshow(1-GetRiskMap(),origin='upper')    
        self.gm.PlotNewRiskMapFig(False)
        sp_mst,dist = self.GetShortestPathMST(goal)
        for j in range(0,self.gm.Height):
            for i in range(0,self.gm.Width):
                if not self.gm.GetObs(self.gm.lat_pts[j],self.gm.lon_pts[i]):
                    if self.UseNetworkX:
                        path2goal,pathX,pathY = self.BackTrackNxPath((i,j), goal)
                    else:
                        path2goal,pathX,pathY = self.BackTrackPath(sp_mst,(i,j))
                    plt.plot(pathX,pathY,'k*-') # TODO: Check why this is so!!!
        #plt.xlim((-0.5,self.gm.Width-0.5))
        #plt.ylim((-0.5,self.gm.Height-0.5))
        return fig
    
    def GetPolicyAtCurrentNode(self,curNode,goal,forceGoal=False):
        #print 'curNode',curNode
        x,y = curNode #self.GetXYfromNodeStr(curNode)
        return self.GetPolicyNxMR((x,y))
    
    def GetPolicyNxMR(self,curNode):
        #newcurNode = self.FindNearestNodeOnGraph(curNode,self.goal)
        
        if curNode == self.goal:
            return self.goal[0],self.goal[1]
        
        path2goal,pathX,pathY = self.BackTrackNxPath(curNode, self.goal)
        if pathX==None and pathY==None:
            #import pdb; pdb.set_trace()
            newcurNode = self.FindNearestNodeOnGraph(curNode,self.goal)
            return newcurNode
            #path2goal, pathX, pathY = self.BackTrackNxPath(newcurNode, self.goal)
            #print 'debug: ',curNode, newcurNode, pathX, pathY
        if len(path2goal)>1:
            return pathX[1],pathY[1]
        else:
            return pathX[0],pathY[0]

    def FindNearestNodeOnGraph(self,curNode,goal):
        nearest_dist = float('inf')
        nearest_node = (None,None)
        #import pdb; pdb.set_trace()
        for a in self.g.nodes():
            i,j = curNode
            x,y = self.GetXYfromNodeStr(a)
            dist = math.sqrt((i-x)**2+(j-y)**2)
            lat1,lon1 = self.gm.GetLatLonfromXY(i,j)
            lat2,lon2 = self.gm.GetLatLonfromXY(x,y)
            if not self.gm.ObsDetLatLon(lat1,lon1,lat2,lon2):
                    if self.dist['(%d,%d)'%(x,y)]['(%d,%d)'%(goal[0],goal[1])] < nearest_dist and dist<self.Dmax:
                        nearest_dist = self.dist['(%d,%d)'%(x,y)]['(%d,%d)'%(goal[0],goal[1])]
                        nearest_node =  (x,y)
        return nearest_node


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
        
    
    
    def GetPolicyMR(self,mst,curNode):
        m1 = re.match('\(([0-9]+),([0-9]+)\)', curNode)
        if m1:
            if mst.has_key(curNode):
                nextNode = mst[curNode]
                if nextNode!=None:
                    m2 = re.match('\(([0-9]+),([0-9]+)\)', nextNode )
                    if m2:
                        return int(m2.group(1)),int(m2.group(2))
            return int(m1.group(1)),int(m1.group(2))
        return None,None
    
    def GetRiskFromXY(self,x,y):
        lat,lon = self.gm.GetLatLonfromXY(x,y)
        return self.gm.GetRisk(lat,lon)
    
    def SimulateAndPlotMR_PolicyExecution(self,start,goal,mst,simStartTime,newFig=True,lineType='y-'):
        if newFig:
            plt.figure()
            plt.title('Plotting Min-Exp Risk Ensemble')
            self.gm.PlotNewRiskMapFig()
        self.totalRisk = 0
        self.totalPathLength = 0.
        self.distFromGoal = float('inf')
        self.totalTime = 0.
        self.goal = goal
        self.start = start
        self.numHops = 0
        self.isSuccess = False

        return self.gs.SimulateAndPlot_PolicyExecution(start,goal,simStartTime,self.maxDepth,self.GetPolicyAtCurrentNode)
        
        
        #---------- Moving away from running our own version of the simulation -----
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
            self.numHops += 1
            try:
                if self.UseNetworkX==True:
                    bx,by = self.GetPolicyNxMR((int(a[0]+0.5),int(a[1]+0.5)))
                else:
                    bx,by = self.GetPolicyMR(mst,'(%d,%d)'%(int(a[0]+0.5),int(a[1]+0.5)))
            except TypeError:
                bx,by = None, None
            if bx!=None and by!=None:
                b = (bx,by)
                
                self.distFromGoal = math.sqrt((a[0]-goal[0])**2+(a[1]-goal[1])**2)
                if self.distFromGoal <=self.acceptR:
                    self.isSuccess = True
                    done = True
                sLat,sLon = self.gm.GetLatLonfromXY(a[0],a[1])
                gLat,gLon = self.gm.GetLatLonfromXY(b[0],b[1])
                tStart = k + self.totalTime/3600.
                if tStart>=24*self.gm.numDays:
                    tStart = 24*self.gm.numDays-1
                xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist = \
                    self.gm.SimulateDive(sLat,sLon,gLat,gLon, self.gm.maxDepth, self.u, self.v, self.lat, self.lon, self.depth, tStart, False )
                self.totalPathLength += totalDist
                self.CollisionReason = CollisionReason
                    #gm.SimulateDive(gm.lat_pts[a[1]], gm.lon_pts[a[0]], gm.lat_pts[b[1]], gm.lon_pts[b[0]], gm.maxDepth, u, v, lat, lon, depth, k)    
                
                # This will allow us to compute how far from the goal we are...
                self.xFin,self.yFin,self.latFin,self.lonFin,self.latArray,self.lonArray,self.depthArray,self.tArray,self.possibleCollision = \
                    xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision
                
                if len(tArray>0):
                    self.totalTime+=tArray[-1]
                
                if possibleCollision == False:
                    tempX,tempY = self.gm.GetXYfromLatLon(np.array(latArray),np.array(lonArray))
                    x_sims,y_sims = tempX[-1:][0],tempY[-1:][0]
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
                        if self.CollisionReason == 'Obstacle' or self.CollisionReason == 'RomsNanLater':
                            self.totalRisk+= self.GetRiskFromXY(tempX[-1:], tempY[-1:])
                            self.finX, self.finY = tempX[-1:], tempY[-1:]
                        plt.plot(tempX,tempY,lineType)
                    x_sims,y_sims = 0,0
                    done=True
                    return self.totalRisk,True # landed = true
                    
                #plt.plot([a[0],x_sims[0]],[a[1],y_sims[0]],lineType)
                try:
                    a = (x_sims[0],y_sims[0])
                except IndexError:
                    done = True
                    return self.totalRisk, True
                    #import pdb; pdb.set_trace()
                i=i+1
                if i>self.maxLengths:
                    done = True
            else:
                self.CollisionReason = 'DidNotFindPolicy'
                done = True
        return self.totalRisk,False
    
    
    
    def InitSARP_Simulation(self,start,goal,startT,lineType='r',newFig = False):
        ''' Initialize Simulation of the SARP policy execution.
        
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
        

    def SimulateAndPlotSARP_PolicyExecution_R(self,simulTime=-1,PostDeltaSimCallback=None,PostSurfaceCallbackFn=None):
        ''' Simulate and plot the SARP policy execution in a re-entrant manner. This simulation is very useful
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

        