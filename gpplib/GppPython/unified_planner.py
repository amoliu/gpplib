'''
   Unified Planner. This is what the journal paper will be about.
'''
import gpplib
from gpplib.Replanner import *
from gpplib.MDP_class import *
import os, sys


class UnifiedPlanner:
    def __init__(self,shelfLocation='./',romsDataDir='roms',gliderModelDir='NoisyGliderModels'):
        self.conf = gpplib.Utils.GppConfig()
        self.riskMapShelf = shelfLocation+'RiskMap.shelf'
        self.romsDataDir = romsDataDir
        self.gliderModelDir = 'NoisyGliderModels'
        self.pngDir = 'uplan_pngs'
        self.lastGoal = (-1,-1)
        self.posNoise = 0.1
        self.lastStart = (0.5,0.5)
        self.StopExecutionOnError = False
        self.LastTransModelLoaded = None
        self.LastPolicyLoaded = None
        self.LastCurrentDataLoaded = None
        try:
            os.mkdir(self.pngDir)
        except OSError as (errno,strerror):
            pass
        self.PolicyTableLoaded = False
        self.tourLocs = [(1,6),(5,1),(8,1)]
        self.curNoiseList = [0.01, 0.025, 0.05, 0.1, 0.15, 0.2, 0.32, 0.5]
        self.curNoise =  None
        self.mdp = MDP(self.riskMapShelf,self.romsDataDir)
        self.mdp.UseNetworkX = True
        
        self.predGM = GliderModel(self.riskMapShelf,self.romsDataDir)
        
        self.TransStats={}
        #self.rp = Replanner('RiskMap.shelf',self.romsDataDir)
        
    def LoadTransitionModelsFromShelf(self,yy,mm,dd,numDays,posNoise=0.1,curNoise=0.01):
        transModelBeingLoaded = '%04d%02d%02d_%d_%.3f_%.3f'%(yy,mm,dd,numDays,posNoise,curNoise)
        if not (transModelBeingLoaded == self.LastTransModelLoaded):
            try:
                self.mdp.GetTransitionModelFromShelf(yy,mm,dd,numDays,posNoise,curNoise,self.gliderModelDir)
                self.LastTransModelLoaded = transModelBeingLoaded
            except:
                if self.StopExecutionOnError:
                    sys.exit(-1)
                else:
                    print 'Could not find the data for that day. Sticking with the current one.'
                    pass
    
    '''
        For any given day, we can retrieve the mean, var in position associated 
        with each transition.
    '''
    def GetStatsFromTransition(self,start,goal,yy,mm,dd,numDays,posNoise=0.1,curNoise=0.01):
        #import pdb; pdb.set_trace()
        edgeKey = '%d,%d,%d,%d'%(start[0],start[1],goal[0],goal[1])
        myKey = '%04d%02d%02d_%d_%.3f_%.3f_%s'%(yy,mm,dd,numDays,posNoise,curNoise,edgeKey)
        if not self.TransStats.has_key(myKey):
            print 'Getting Stats %s'%(myKey)
            self.LoadTransitionModelsFromShelf(yy, mm, dd, numDays, posNoise, curNoise)
            if self.mdp.gm.FinalLocs.has_key(edgeKey):
                xFin, yFin = self.mdp.gm.FinalLocs[edgeKey]
                xFinNZ,yFinNZ = xFin[xFin.nonzero()[0]],yFin[yFin.nonzero()[0]]
                xFin_mu,xFin_var,yFin_mu,yFin_var = xFinNZ.mean(),xFinNZ.var(), yFinNZ.mean(),yFinNZ.var()
                self.TransStats[myKey] = [(xFin_mu,xFin_var),(yFin_mu,yFin_var)]
                return [(xFin_mu,xFin_var),(yFin_mu,yFin_var)]
            else:
                return None # Edge does not exist!
        else:
            return self.TransStats[myKey]
            
            
    '''
        Run a prediction starting at startTime, and figure out where 
        the glider will end up at the end of this.
    '''
    def GetPredictedLoc(self,start,goal,startTime):
        self.predGM.UseRomsNoise = False
        sLat,sLon = self.predGM.GetLatLonfromXY(start[0],start[1])
        gLat,gLon = self.predGM.GetLatLonfromXY(goal[0],goal[1])
        xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist = \
        self.predGM.SimulateDive(sLat,sLon,gLat,gLon,self.predGM.MaxDepth,self.mdp.u,self.mdp.v,self.mdp.lat,self.mdp.lon,self.mdp.depth,startTime,False,True)
        tempX, tempY = self.predGM.GetXYfromLatLon(np.array(latArray), np.array(lonArray))
        predLocX,predLocY = tempX[-1:],tempY[-1:]
        
        return predLocX, predLocY, possibleCollision
    
    '''
        Loads the policy corresponding to the goal, date, noise from shelf. 
        (Need to create these before-hand using StoreAllPolicies.py)
        Also need to ensure that all locations in this tour are also the same in StoreAllPolicies.py 
    '''
    def LoadPolicyFromShelve(self,yy,mm,dd,numDays,goal,posNoise=0.1,curNoise=0.01):
        policyStr = 'Policy_%04d%02d%02d_%d_G_%d_%d_%.3f_%.3f'%(yy,mm,dd,numDays,goal[0],goal[1],posNoise,curNoise)
        if self.LastPolicyLoaded != policyStr:
            policyTable = shelve.open('PolicyTable_%04d%02d%02d_%d.shelve'%(yy,mm,dd,numDays),writeback=False)
            keyForGoalAndNoise = 'Pol_G_%d_%d_PN_%.3f_RN_%.3f'%(goal[0],goal[1],posNoise,curNoise)
            mdp_key = 'MDP_%s'%(keyForGoalAndNoise);
            if policyTable.has_key(mdp_key):
                print 'Loading policy for %s'%(policyStr)
                if policyTable[mdp_key].has_key('U'):
                        self.mdp.mdp['U'] = policyTable[mdp_key]['U']
                if policyTable[mdp_key].has_key('polTree'):
                        self.mdp.pol_tree = policyTable[mdp_key]['polTree']
                        self.mdp.gm2 = self.mdp.pol_tree # Actually a hack. FIXME
                self.LastPolicyLoaded = policyStr
            policyTable.close()
    
    '''
        Loads Roms data for simulation purposes.
        This data is stored in the form of sfcst_yyyymmdd_nD.mat files.
    '''
    def LoadCurrentsFromShelve(self,yy,mm,dd,numDays):
        currentStr = 'Current_%04d%02d%02d_%d'%(yy,mm,dd,numDays)
        if self.LastCurrentDataLoaded!= currentStr:
            print 'Loading current data for %s'%(currentStr)
            self.mdp.GetRomsData(yy,mm,dd,numDays)
            self.predGM.GetRomsData(yy,mm,dd,numDays)
            self.mdp.gm.GetRomsData(yy,mm,dd,numDays)
            self.mdp.gm.yy,self.mdp.gm.mm,self.mdp.gm.dd = yy,mm,dd
            self.LastCurrentDataLoaded = currentStr
    
    '''
       Find the best planner to use by looking at the prediction Error.
       The best planner is the one based upon the model which is the best.
       pred_err**2 = (predX-finX)**2 + (predY-finY)*2
       sd_r**2 = sd_x**2 + sd_y**2
       
       After finding the prediction error in ROMS that best explains the 
       deviation, it returns the current noise std. deviation.
       The policy can be retrieved using this noise value.
    '''
    def FindBestPlannerToUse(self,relX,relY,predX,predY):
        # Start off with the least conservative...
        predErrSqrd = ((predX-relX)**2 + (predY-relY)**2)
        print 'Looking for best planner to use...'
        bestCurrentNoise = self.curNoiseList[0]
        for i in range(0,len(self.curNoiseList)):
            [(xFin_mu,xFin_var),(yFin_mu,yFin_var)] = self.GetStatsFromTransition(self.mdp.lastTransition[0],self.mdp.lastTransition[1],self.yy,self.mm,(self.dd%2),self.numDays,0.1,self.curNoiseList[i]);
            rFinVar = (xFin_var+yFin_var)
            print '%d) predErrSqrd=%.3f, rFinVar=%.3f'%(i, predErrSqrd,rFinVar)
            
            if predErrSqrd>=rFinVar:
                new_best=i+1; 
                if new_best>=len(self.curNoiseList):
                    new_best = len(self.curNoiseList)-1;
                print 'new cur-noise=%.3f'%(self.curNoiseList[new_best])
                bestCurrentNoise = self.curNoiseList[new_best]
                
        # Returns the prediction Noise value
        print 'Best Current Noise estimate is: %.3f'%(bestCurrentNoise)
        return bestCurrentNoise
    
    def DoPostSurfacingThings(self,latArray,lonArray):
        #self.PlotAndSaveExecution(latArray, lonArray)
        if self.mdp.lastTransition != None:
            print 'Surfaced... Now doing Post Surfacing things!!!'
            if self.mdp.lastTransition[1][0] !=None:
                predLocX, predLocY, possibleCollision = self.GetPredictedLoc(self.mdp.lastTransition[0],self.mdp.lastTransition[1],(self.tHrs%48))
                print 'Predicted Location is: %.1f, %.1f'%(predLocX,predLocY)
                predX = predLocX - self.mdp.lastTransition[0][0];
                predY = predLocY - self.mdp.lastTransition[0][1]; # Use locs relative to start.
                tempX, tempY = self.mdp.gm.GetXYfromLatLon(np.array(latArray),np.array(lonArray))
                relX, relY = tempX[-1:]-self.mdp.lastTransition[0][0], tempY[-1:]-self.mdp.lastTransition[0][1]
                bestPredNoiseVal = self.FindBestPlannerToUse(relX,relY,predX,predY)
                # Use this noise policy...
                self.policyPredNoise = bestPredNoiseVal
                self.LoadPolicyFromShelve(self.yy,self.mm,self.dd,self.numDays,self.goal,self.posNoise,self.policyPredNoise)
            
    
    def PlotAndSaveExecution(self,latArray,lonArray):
        import matplotlib.axes as axes
        fig1 = plt.gcf()
        fig1.set_size_inches(12,6)
        ax1=plt.subplot(1,2,1)
        self.mdp.gm.PlotNewRiskMapFig(False)
        self.mdp.gm.PlotCurrentField(int(self.tHrs)%24)
        tempX, tempY = self.mdp.gm.GetXYfromLatLon(np.array(latArray), np.array(lonArray))
        ax1.plot(tempX, tempY, self.mdp.lineType)
        ax1.text(3,10,'Simulation at: %04d-%02d-%02d %.1f hrs'%(self.mdp.gm.yy,self.mdp.gm.mm,self.mdp.gm.dd,self.tHrs))
        ax1.text(3,9,'Goal : (%d,%d)'%(self.goal[0],self.goal[1]))
        # Also show the MDP policy on the other figure.
        ax2=plt.subplot(1,2,2)
        self.mdp.DisplayPolicy(fig1)
        plt.title('MDP Policy for Noise %.3f'%(self.policyPredNoise))
        #plt.quiver([self.mdp.a[0]],[self.mdp.a[1]],[self.mdp.bx-int(self.mdp.a[0])],[self.mdp.by-int(self.mdp.a[1])],color='r',lw=2)
        plt.savefig('%s/Ensembles_%04d%02d%02d_%05.1f.png'%(self.pngDir,yy,mm,dd,self.tHrs),bbox_inches='tight')
        plt.close()
        
    
    '''
        Run a simulation for N hours, given noise.
    '''
    def RunUPforNhoursGivenNoise(self,yy,mm,day,numDays,startTime,Nhrs,PredNoise=None):
        self.posNoise = 0.1; self.curNoise = 0.025;
        self.policyPredNoise = 0.2;
        self.LoadTransitionModelsFromShelf(yy,mm,day,numDays,self.posNoise,self.curNoise)
        self.tHrs = startTime
        simulTime = 6.0
        self.numDays = numDays
        self.start = (8,1)
        plt.figure()
        self.mdp.gm.PlotNewRiskMapFig(False)
        daysInMonths = [31,28,31,30,31,30,31,31,30,31,30,31]
        dd = day
        
        if (yy%4)==0:
            daysInMonths[2-1] = 29;
        i,j=0,0
        numLocs = len(self.tourLocs)
        goal = self.tourLocs[j]; self.goal = goal
        #self.mdp.gm.InitSim(sLat,sLon,tLat,tLon,maxDepth,startT,FullSimulation=True,HoldValsOffMap=True)
        self.mdp.InitMDP_Simulation(self.start,self.goal,startTime,'-r',False)
        while ( self.tHrs < Nhrs):
            i = int(self.tHrs/24);
            dd = day+i
            if dd>daysInMonths[mm-1]:
                dd = 1; mm = (mm+1)%12;
            self.yy,self.mm,self.dd = yy,mm,dd
            self.LoadPolicyFromShelve(yy,mm,self.dd,numDays,goal,self.posNoise,self.policyPredNoise)
            self.LoadCurrentsFromShelve(yy, mm, self.dd, numDays)
            self.LoadTransitionModelsFromShelf(self.yy,self.mm,self.dd,numDays,self.posNoise,self.curNoise)
            self.tHrs += simulTime
            print 'Number of hours :',self.tHrs
           
            tempRiskMDP, landedMDP = self.mdp.SimulateAndPlotMDP_PolicyExecution_R(simulTime,self.PlotAndSaveExecution,self.DoPostSurfacingThings)
            #tempRiskMDP, landedMDP = self.mdp.SimulateAndPlotMDP_PolicyExecution(self.start,goal,self.tHrs%24,newFig=False)
            
            if self.mdp.possibleCollision==True:
                print 'Possible Collision. Quitting!'
                break
            
            if self.mdp.isSuccess:
                #self.tHrs = self.mdp.totalTime/3600.
                j=j+1; j = j%numLocs;
                print 'At (%d,%d). Reached goal (%d,%d). Now going to (%d,%d)'%(self.mdp.a[0],self.mdp.a[1],goal[0],goal[1],self.tourLocs[j][0],self.tourLocs[j][1])
                self.mdp.InitMDP_Simulation((self.mdp.a[0],self.mdp.a[1]),(self.tourLocs[j][0],self.tourLocs[j][1]),self.tHrs%(24*numDays),'-r',False)
                goal = self.tourLocs[j]; self.goal = goal
                self.start = (self.mdp.a[0], self.mdp.a[1]);
                                
yy,mm,dd,numDays = 2011,2,1,2
PredNoise = None
Nhrs = 500
startTime = 0
uplan = UnifiedPlanner()
uplan.RunUPforNhoursGivenNoise(yy, mm, dd, numDays, startTime, Nhrs, PredNoise)