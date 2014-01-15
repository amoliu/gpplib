'''
**Replanner class** - This is a class that helps do re-planning. There are two basic 
types of planning that are supported and both are based upon shortest-paths.

See also `MDP Class_` ,  GenGliderModelUsingRoms_

'''
import numpy as np
import matplotlib.pyplot as plt
import os,sys,math,re
import shelve
from InterpRoms import *
import networkx as nx
from Simulate import *
from GenGliderModelUsingRoms import GliderModel

class Replanner(object):
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
        self.UseNetworkX = None
        self.maxDepth = 60.
        '''
        try:
            from pygraph.classes.digraph import digraph
            from pygraph.algorithms.searching import depth_first_search
            from pygraph.algorithms.minmax import shortest_path_bellman_ford
            from pygraph.algorithms.minmax import shortest_path
            from pygraph.readwrite.dot import write
            self.UseNetworkX = False
        except ImportError:
            print 'Please install or specify path to pygraph'
            pass
        '''
        # Import graphviz
        try:
            import pygraphviz as gv
        except ImportError:
            print 'Please install or specify path to pygraphviz'
            pass
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
        self.gModel = {}
        self.gModel['TransModel'] = gmShelf['TransModel']
        gmShelf.close()
        
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
        #u,v,time1,depth,lat,lon = self.gsR.gm.GetRomsData(yy,mm,dd,numDays,useNewFormat,usePredictionData)
        if UpdateSelf:
            self.u,self.v,self.time1,self.depth,self.lat,self.lon = u,v,time1,depth,lat,lon
            self.yy,self.mm,self.dd = yy,mm,dd
        self.numDays = numDays
        self.gm.numDays = numDays
        return u,v,time1,depth,lat,lon
    
    '''    
    def GetRomsData(self,yy,mm,dd,numDays,UseNewFormat=True,usePredictionData=False):
        UpdateSelf=True
        u,v,time1,depth,lat,lon = self.gs.gm.GetRomsData(yy,mm,dd,numDays,UseNewFormat,usePredictionData)
        u,v,time1,depth,lat,lon = self.gm.GetRomsData(yy,mm,dd,numDays,UseNewFormat,usePredictionData)
        self.u,self.v,self.time1,self.depth,self.lat,self.lon = u,v,time1,depth,lat,lon
        self.numDays = numDays
        return u,v,time1,depth,lat,lon
    '''
    
    def isOnMapRP(self,s):
        width, height = self.gm.Width, self.gm.Height
        if s[0]<0 or s[0]>=width:
            return False
        if s[1]<0 or s[1]>=height:
            return False
        return True
    
    def GetExpRiskOld(self,v1,v2):
        x,y = v1[0],v1[1]
        xp,yp = v2[0],v2[1]
        expRisk = 0
        stateTrans = '%d,%d,%d,%d'%(x,y,xp,yp)
        if self.gModel['TransModel'].has_key(stateTrans):
            transProbs, tPSize, zeroLoc = self.gModel['TransModel'][stateTrans][2], \
                                          self.gModel['TransModel'][stateTrans][1], \
                                          self.gModel['TransModel'][stateTrans][0]
            totalProb = 0
            for j in range(0,int(tPSize)):
                for i in range(0,int(tPSize)):
                    xp2,yp2 = x+i-zeroLoc, y+j-zeroLoc
                    transProb = transProbs[i][j]
                    totalProb += transProb
                    if self.isOnMapRP((xp2,yp2)):
                        expRisk += transProb * self.gm.GetRisk(self.gm.lat_pts[yp2],self.gm.lon_pts[xp2])
                    else:
                        expRisk += transProb * 1.0 # Off map locations get high-risk!
        else:
            expRisk = None
        
        return expRisk
    
    
    def GetExpRisk(self,v1,v2):
        x,y = v1[0],v1[1]
        xp,yp = v2[0],v2[1]
        expRisk = 0
        stateTrans = '%d,%d,%d,%d'%(x,y,xp,yp)
        if self.gModel['TransModel'].has_key(stateTrans):
            transProbs, tPSize, zeroLoc = self.gModel['TransModel'][stateTrans][2], \
                                          self.gModel['TransModel'][stateTrans][1], \
                                          self.gModel['TransModel'][stateTrans][0]
            totalProb = 0
            for j in range(0,int(tPSize)):
                for i in range(0,int(tPSize)):
                    xp2,yp2 = x+i-zeroLoc, y+j-zeroLoc
                    transProb = transProbs[i][j]
                    totalProb += transProb
                    if self.isOnMapRP((xp2,yp2)):
                        expRisk += transProb * self.gm.GetRisk(self.gm.lat_pts[yp2],self.gm.lon_pts[xp2])
                    else:
                        expRisk += transProb * 1.0 # Off map locations get high-risk!
                    
        else:
            expRisk = None
        
        return expRisk    
                        
    
    def CreateExpRiskGraph(self):
        # Short-circuit this!
        return self.CreateGraphUsingProximityGraph('MinExpRisk')
        
        # This is what we used to do earlier. Won't be running
        # unless we actually want it to.
        self.g = nx.DiGraph()
        
        for j in range(0,self.gm.Height):
            for i in range(0,self.gm.Width):
                    self.g.add_node('(%d,%d)'%(i,j))
        
        for j in range(0,self.gm.Height):
            for i in range(0,self.gm.Width):
                for y in range(0,self.gm.Height):
                    for x in range(0,self.gm.Width):
                        if math.sqrt((i-x)**2+(j-y)**2)<=self.Dmax:
                            if self.gm.ObsDetLatLon(self.gm.lat_pts[j],self.gm.lon_pts[i],self.gm.lat_pts[y],self.gm.lon_pts[x])==False:
                                expRisk = self.GetExpRisk((i,j),(x,y))
                                if expRisk !=None:
                                        self.g.add_edge('(%d,%d)'%(i,j),'(%d,%d)'%(x,y),weight=expRisk)
        ### If we want to write this graph out.
        #dot = write(g)
        #G = gv.AGraph(dot)
        #G.layout(prog ='dot')
        #G.draw('SCB.png')
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
        num_nodes_compared, num_nodes_added = 0,0
        for a in self.g.nodes():
            for b in self.g.nodes():
                if a!=b:
                    num_nodes_compared += 1
                    i,j = self.GetXYfromNodeStr(a); x,y = self.GetXYfromNodeStr(b)
                    if math.sqrt((i-x)**2+(j-y)**2)<=self.Dmax:
                        print 'Considering: (%d,%d) to (%d,%d):'%(i,j,x,y)
                        if self.gm.ObsDetLatLon(self.gm.lat_pts[j],self.gm.lon_pts[i],self.gm.lat_pts[y],self.gm.lon_pts[x])==False:
                            if graphType == 'MinExpRisk':
                                expRisk = self.GetExpRisk((i,j),(x,y))
                                if expRisk !=None:
                                    self.g.add_edge('(%d,%d)'%(i,j),'(%d,%d)'%(x,y),weight=expRisk)
                                    print 'Added edge (%d,%d) to (%d,%d) with weight=%.2f'%(i,j,x,y,expRisk)
                                else:
                                    print 'Rejected edge (%d,%d) to (%d,%d) with weight=None'%(i,j,x,y)
                            elif graphType == 'MinRisk':
                                riskVal = self.gm.GetRisk(self.gm.lat_pts[y],self.gm.lon_pts[x])
                                if riskVal!=None:
                                    self.g.add_edge('(%d,%d)'%(i,j),'(%d,%d)'%(x,y),weight=riskVal)
                                    print 'Added edge (%d,%d) to (%d,%d) with weight=%.2f'%(i,j,x,y,riskVal)
                                    num_nodes_added+=1
                                else:
                                    print 'Rejected edge (%d,%d) to (%d,%d) with weight=None'%(i,j,x,y)
                            elif graphType == 'ShortestPath':
                                self.g.add_edge('(%d,%d)'%(i,j),'(%d,%d)'%(x,y),weight=math.sqrt((x-i)**2.+(y-j)**2.))
                        else:
                            print 'Rejected due to collision!'
                            
        print 'Total # of edges compared=%d, # of edges added=%d'%(num_nodes_compared, num_nodes_added)
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
        except:
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
    
    def PlotMRpaths(self,goal):
        fig = plt.figure()
        plt.title('Plot of Min-Exp Risk MST (Goal at:(%d,%d))'%(goal[0],goal[1]))
        #plt.imshow(rMap.transpose()+0.5,origin='upper')
        #plt.imshow(1-GetRiskMap(),origin='upper')    
        self.gm.PlotNewRiskMapFig(False)
        sp_mst,dist = self.GetShortestPathMST(goal)
        for a in self.g.nodes():
            i,j = self.GetXYfromNodeStr(a);
            path2goal,pathX,pathY = self.BackTrackNxPath((i,j), goal)
            plt.plot(pathX,pathY,'k*-')
        
        
        #for j in range(0,self.gm.Height):
        #    for i in range(0,self.gm.Width):
        #        if not self.gm.GetObs(self.gm.lat_pts[j],self.gm.lon_pts[i]):
        #           path2goal,pathX,pathY = self.BackTrackNxPath((i,j), goal)
        #           plt.plot(pathX,pathY,'k*-') # TODO: Check why this is so!!!
        #plt.xlim((-0.5,self.gm.Width-0.5))
        #plt.ylim((-0.5,self.gm.Height-0.5))
        return fig
    
    def GetPolicyAtCurrentNode(self,curNode,goal,forceGoal=False):
        #print 'curNode',curNode
        x,y = curNode
        return self.GetPolicyNxMR((x,y))
    
    def GetPolicyNxMR(self,curNode):
        if curNode == self.goal:
            return self.goal[0],self.goal[1]
        
        path2goal,pathX,pathY = self.BackTrackNxPath(curNode, self.goal)
        if pathX==None and pathY==None:
            return self.FindNearestNodeOnGraph(curNode,self.goal)
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
            if not self.gm.ObsDetLatLon(self.gm.lat_pts[int(j)],self.gm.lon_pts[int(i)], \
                                                            self.gm.lat_pts[int(y)],self.gm.lon_pts[int(x)]):
                if (dist<self.Dmax):
                    if self.dist['(%d,%d)'%(x,y)]['(%d,%d)'%(goal[0],goal[1])] < nearest_dist:
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
        self.totalRisk = 0
        self.totalPathLength = 0.
        self.distFromGoal = float('inf')
        self.totalTime = 0.
        self.goal = goal
        self.start = start
        self.numHops = 0
        self.isSuccess = False
        
        if newFig:
            plt.figure()
            plt.title('Plotting Min-Exp Risk Ensemble')
            self.gm.PlotNewRiskMapFig()

        return self.gs.SimulateAndPlot_PolicyExecution(start,goal,simStartTime,self.maxDepth,self.GetPolicyAtCurrentNode,lineType,newFig)
        
        a= start
        done = False
        i=0
        k = simStartTime
        #x_sims,y_sims = np.zeros((24*gm.numDays,1)),np.zeros((24*gm.numDays,1))
        if k>=(24*self.gm.numDays):
           k = 24*self.gm.numDays-1
        x_sims,y_sims = 0,0
        self.finX,self.finY = start[0],start[1]
        #import pdb; pdb.set_trace()
        while (not done):
            self.numHops += 1
            try:
                bx,by = self.GetPolicyNxMR((int(a[0]+0.5),int(a[1]+0.5)))
                print 'At :(%.1f,%.1f). Going to: (%d,%d)'%(a[0],a[1],bx,by)
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
                    self.finX, self.finY = a
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
        
