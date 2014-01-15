from gpplib.GenGliderModelUsingRoms import GliderModel
import numpy as np
from matplotlib import pyplot as plt
import math
from gpplib.gppExceptions import Error as gppError



class GliderSimulator_R(object):
    ''' Stand-alone generic re-entrant simulator for a glider in ROMS data.
    Earlier, each of my planners had its own implementation of a simulator built into it.
    This is highly repetitive and as someone wisely said 
    "Repetition" is defined as "a host site for a defect infection".

    So henceforth, we are going to use this as the entry-point for simulation.
    Users create a simulation instance where they define the type of simulation they need, 
    and then forward propagate this.
    
    This class could have been written using Generators on the GliderSimulator, but I have
    used this version mainly because I intend porting this over to C++ which does not 
    have generators.
    '''
    
    def __init__(self,riskMap,romsDataDir='./',acceptR=0.6,**kwargs):
        self.gm = GliderModel( riskMap, romsDataDir )
        self.Init_Simulation()
        self.acceptR = acceptR
    
    def Init_Simulation(self):
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
        self.totalRisk = 0
        self.distFromGoal = float('inf')
        self.totalPathLength = 0.
        self.totalTime = 0
        self.numHops = 0
        self.isSuccess = False
        self.done = False
        self.Indx = 0
        self.possibleCollision = False
        #x_sims,y_sims = np.zeros((24*gm.numDays,1)),np.zeros((24*gm.numDays,1))
        #if startT>=(24*self.gm.numDays):
        #   startT = 24*self.gm.numDays-1
        self.x_sims,self.y_sims = 0,0
        self.latArray, self.lonArray = [], []
        #self.gm.InitSim(self.sLat,self.sLon,self.gLat,self.gLon,self.gm.MaxDepth,startT,self.DoFullSim,self.HoldValsOffMap)
        #import pdb; pdb.set_trace()
        self.lastLegComplete = True
        self.bx,self.by = None, None
        self.lastTransition = None
        
    def Start_Simulation(self,start,goal,startT,maxDepth=80.,lineType='r-',newFig=False):
        self.goal = goal
        self.start = start
        self.a= self.start
        self.startT = startT
        self.lineType = lineType
        self.finX,self.finY = start[0],start[1]
        self.sLat,self.sLon = self.gm.GetLatLonfromXY(self.start[0],self.start[1])
        self.gLat,self.gLon = self.gm.GetLatLonfromXY(self.goal[0],self.goal[1])
        self.Init_Simulation()

        if newFig:
            plt.figure()
            plt.title('Plotting Min-Exp Risk Ensemble')
            self.gm.PlotNewRiskMapFig()
            
    def SetupCallbacks(self,GetPolicyAtNodeCallbackFn=None,PostDeltaSimCallbackFn=None,PostSurfaceCallbackFn=None):
        self.GetPolicyAtNodeCallbackFn = GetPolicyAtNodeCallbackFn
        self.PostSurfaceCallbackFn = PostSurfaceCallbackFn
        self.PostDeltaSimCallbackFn = PostDeltaSimCallbackFn
    
    def GetRiskFromXY(self,x,y):
        '''  Looks up the risk value for x,y from the risk-map
        
        Args:
            x,y (float,float) : x and y in graph coordinates.
        '''
        lat,lon = self.gm.GetLatLonfromXY(x,y)
        return self.gm.GetRisk(lat,lon)
    
    def SimulateAndPlot_PolicyExecution_R(self,simulTime=-1):
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
                    #print 'Simulate.py before getpolicy:',self.bx, self.by
                    self.lastTransition = [(int(self.a[0]+0.5),int(self.a[1]+0.5)),(self.bx,self.by)]
                    # Used to be an integer
                    #self.bx, self.by = self.GetPolicyAtNodeCallbackFn((int(self.a[0]+0.5),int(self.a[1]+0.5)), self.goal)
                    #self.bx, self.by = self.GetPolicyAtNodeCallbackFn(self.a[0],self.a[1], self.goal) # Seems to be causing issues with debugSA_MDP.py
                    self.bx, self.by = self.GetPolicyAtNodeCallbackFn((self.a[0],self.a[1]), self.goal)
                    
                    #self.bx, self.by = self.GetPolicyAtNodeCallbackFn('(%d,%d)' % (int(self.a[0]), int(self.a[1])), '(%d,%d)' % (self.goal[0], self.goal[1]))
                    #print 'Simulate.py after getpolicy:',self.bx, self.by
                    if self.PostSurfaceCallbackFn != None:
                        self.PostSurfaceCallbackFn(self.latArray,self.lonArray)
                        self.plot(a[0],a[1],'k.')
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
                if self.PostDeltaSimCallbackFn!=None:
                    self.PostDeltaSimCallbackFn(latArray,lonArray)
                
                self.distFromGoal = math.sqrt((self.a[0] - self.goal[0]) ** 2 + (self.a[1] - self.goal[1]) ** 2)
                if self.distFromGoal <= self.acceptR:
                    self.isSuccess = True
                    self.done = True
                
                if len(tArray) > 0:
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
                    import pdb; pdb.set_trace()
                if self.lastLegComplete == True: # Finished simulating a leg.
                    i = i + 1
                else: # Since this is a re-entrant simulator... Get done here...
                    self.done = True
        else: # We did not get a policy here.
                self.CollisionReason = 'DidNotFindPolicy'
                self.done = True
        return self.totalRisk, False
    
    def SimulateAndPlot_PolicyExecution_NS_R(self,simulTime=-1):
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
                    #import pdb;pdb.set_trace()
                    #print 'Simulate.py before getpolicy:',self.bx, self.by
                    self.lastTransition = [(int(self.a[0]+0.5),int(self.a[1]+0.5)),(self.bx,self.by)]
                    # Used to be an integer
                    #self.bx, self.by = self.GetPolicyAtNodeCallbackFn((int(self.a[0]+0.5),int(self.a[1]+0.5)), self.goal)
                    #self.bx, self.by = self.GetPolicyAtNodeCallbackFn(self.a[0],self.a[1], self.goal) # Seems to be causing issues with debugSA_MDP.py
                    self.bx, self.by = self.GetPolicyAtNodeCallbackFn((self.a[0],self.a[1]), self.goal,tStart)
                    
                    #self.bx, self.by = self.GetPolicyAtNodeCallbackFn('(%d,%d)' % (int(self.a[0]), int(self.a[1])), '(%d,%d)' % (self.goal[0], self.goal[1]))
                    #print 'Simulate.py after getpolicy:',self.bx, self.by
                    if self.PostSurfaceCallbackFn != None:
                        self.PostSurfaceCallbackFn(self.latArray,self.lonArray)
                        self.plot(a[0],a[1],'k.')
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
                if self.PostDeltaSimCallbackFn!=None:
                    self.PostDeltaSimCallbackFn(latArray,lonArray)
                
                self.distFromGoal = math.sqrt((self.a[0] - self.goal[0]) ** 2 + (self.a[1] - self.goal[1]) ** 2)
                if self.distFromGoal <= self.acceptR:
                    self.isSuccess = True
                    self.done = True
                
                if len(tArray) > 0:
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
                    import pdb; pdb.set_trace()
                if self.lastLegComplete == True: # Finished simulating a leg.
                    i = i + 1
                else: # Since this is a re-entrant simulator... Get done here...
                    self.done = True
        else: # We did not get a policy here.
                self.CollisionReason = 'DidNotFindPolicy'
                self.done = True
        return self.totalRisk, False


class GliderSimulator(GliderSimulator_R):
    ''' Stand-alone generic non re-entrant simulator for a glider. This is essentially a wrapper
    around the re-entrant simulator. Why use this?
    '''
    def __init__(self,shelfName='RiskMap.shelf',sfcst_directory='./',acceptR=0.6,**kwargs):
        ''' Initialize Glider Simulator.
        '''
        super(GliderSimulator,self).__init__(shelfName,sfcst_directory,acceptR,**kwargs)
        self.PostDeltaSimCallbackFn, self.PostSurfaceCallbackFn = None, None
        

    def SimulateAndPlot_PolicyExecution(self,start,goal,startT,maxDepth=80.,GetPolicyAtNodeCallbackFn=None,lineType='r-',newFig=False,maxNumHops=50):
        #import pdb; pdb.set_trace()
        self.Start_Simulation(start,goal,startT,maxDepth,lineType,newFig)
        if GetPolicyAtNodeCallbackFn!=None:
            self.GetPolicyAtNodeCallbackFn = GetPolicyAtNodeCallbackFn
        else:
            raise CallbackNotDefinedError('Need to specify a callback function for the policy to take.')
        if maxNumHops<0:
            print '**** Warning, this simulation will not end if you do not reach the goal! ****'
        for i in range(0,maxNumHops):
            if not self.done:
                self.SimulateAndPlot_PolicyExecution_R(-1)
        return self.totalRisk, self.possibleCollision
    
    def SimulateAndPlot_PolicyExecution_NS(self,start,goal,startT,maxDepth=80.,GetPolicyAtNodeCallbackFn=None,lineType='r-',newFig=False,maxNumHops=50):
        #import pdb; pdb.set_trace()
        self.Start_Simulation(start,goal,startT,maxDepth,lineType,newFig)
        if GetPolicyAtNodeCallbackFn!=None:
            self.GetPolicyAtNodeCallbackFn = GetPolicyAtNodeCallbackFn
        else:
            raise CallbackNotDefinedError('Need to specify a callback function for the policy to take.')
        if maxNumHops<0:
            print '**** Warning, this simulation will not end if you do not reach the goal! ****'
        for i in range(0,maxNumHops):
            if not self.done:
                self.SimulateAndPlot_PolicyExecution_NS_R(-1)
        return self.totalRisk, self.possibleCollision
    
    

class CallbackNotDefinedError(gppError):
    ''' Exception raised for errors when a callback that should
    be defined is not defined. 
    
    Attributes:
        msg 
    '''
    def __init__(self,msg):
        self.msg = msg
