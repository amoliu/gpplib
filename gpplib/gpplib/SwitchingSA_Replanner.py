import gpplib
from gpplib.SA_Replanner2 import *
from gpplib.StateActionMDPGP import *
from gpplib.Utils import *
from gpplib.LatLonConversions import *
from gpplib.PseudoWayptGenerator import *
import os, sys
import time, datetime

class SwitchingSA_Replanner:
    def __init__(self , **kwargs ):
        ''' Keyword Args:
                shelfLocation (str) : Location of the RiskMap shelf defaults to ('./')
                riskMapShelf (str)  : RiskMap.shelf defaults to ('RiskMap.shelf')
                romsDataDir  (str)  : Location of the ROMS data defaults to ('roms')
                gliderModelDir (str) : Location of the transition models of the glider ('NoisyGliderModels')
                pngDir (str) : Png directory
                policyTableDir (str) : Directory in which the pre-computed policies have been stored
                plannerType (str) : Type of planner (saReplanner/mrplanner)
        '''
        self.conf = gpplib.Utils.GppConfig()
        riskMapShelf, romsDataDir = \
            self.conf.myDataDir+'RiskMap3.shelf', self.conf.romsDataDir
        gliderModelDir, policyTableDir = \
            self.conf.myDataDir+'gliderModel3/', 'ReplayPolicies/'
        pngDir = 'replayPngs_All/'
        
        if kwargs.has_key('romsDataDir'): self.romsDataDir = kwargs['romsDataDir']
        else: self.romsDataDir = romsDataDir
        
        if kwargs.has_key('riskMapShelf'): self.riskMapShelf = kwargs['riskMapShelf']
        else: self.riskMapShelf = riskMapShelf
        
        if kwargs.has_key('romsDataDir'): self.romsDataDir = kwargs['romsDataDir']
        else: self.romsDataDir = romsDataDir
        
        if kwargs.has_key('gliderModelDir'): self.gliderModelDir = kwargs['gliderModelDir']
        else: self.gliderModelDir = gliderModelDir
        
        if kwargs.has_key('policyTableDir'): self.policyTableDir = kwargs['policyTableDir']
        else: self.policyTableDir = policyTableDir
        
        if kwargs.has_key('pngDir'): self.pngDir = kwargs['pngDir']
        else: self.pngDir = pngDir
        
        if kwargs.has_key('plannerType'): self.plannerType = kwargs['plannerType']
        else: self.plannerType = 'saReplanner'
        
        
        if kwargs.has_key('gliderModelType'): self.gliderModelType = kwargs['gliderModelType']
        else: self.gliderModelType = '3'
        
        if kwargs.has_key('theta'):
            theta = kwargs['theta']
        else:
            theta = {'w_r':-1, 'w_g':100.}
        self.theta = theta
        
        self.storeAllPngs = True
        if kwargs.has_key('StoreAllPngs'):
            self.storeAllPngs = kwargs['StoreAllPngs']
            
        try:
            os.mkdir( self.pngDir )
        except:
            pass
        
        try:
            os.mkdir( self.policyTableDir )
        except:
            pass
        
        self.PolicyTableLoaded = False
        self.LastPolicyLoaded = None
        self.LastTransModelLoaded  = None
        self.LastCurrentDataLoaded = None
        self.lastGoal = None
        self.curNoise = 0.01
        
        #self.saMdp = SA_MDP_GP( self.riskMapShelf, self.romsDataDir )
        self.saReplanner = SA_Replanner2( self.riskMapShelf, self.romsDataDir )
        self.sarp_type_str = 'saReplanner'
        #self.saFixedMdp = SA_MDP( self.riskMapShelf, self.romsDataDir )
        
        #if self.storeAllPngs == False:
        #    self.saMdp.gm.PlotNewRiskMapFig(False)
        
        self.predGM = GliderModel(self.riskMapShelf, self.romsDataDir)
        self.TransStats = {}
        
        
    def GetBestTimeSlot(self,yy,mm,dd,hr,mi):
        ''' Args:
                yy,mm,dd,hr,mi : (date and time at which we are attempting to find the best matching time-slot)
        '''
        timeTables = [ (0,12), (6,18), (12,24), (18,30), (24,36) ]
        t = time.mktime(datetime.datetime(yy,mm,dd,hr,mi).timetuple())
        bm = 0
        i = (hr/6)
        return timeTables[i]
                
    def LoadTransModelForPlanner(self,planner,gModName):
        gmShelf = shelve.open('%s/%s.shelf'%(self.gliderModelDir,gModName),writeback=False)
        planner.gm.TransModel = gmShelf['TransModel']
        planner.gm.FinalLocs = gmShelf['FinalLocs']
        planner.gm.TracksInModel = gmShelf['TracksInModel']
        planner.gModel={}
        planner.gModel['TransModel'] = gmShelf['TransModel']
        gmShelf.close()            
        
    def LoadTransitionModelsFromShelf(self,yy,mm,dd,hr,mi,posNoise=0.01,curNoise=0.01,numDays=0):
        ''' The transition model being loaded from the shelf according to the date and time
            being specified.
            
            Args:
                yy,mm,dd,hr,mi : (date and time at which we are attempting to 
                posNoise : position noise (sigma_pos)
                curNoise : current noise (sigma_cur)
        '''
        t1,t2 = self.GetBestTimeSlot(yy, mm, dd, hr, mi)
        gModName = 'gliderModel%s_%04d%02d%02d_%d_%d_%.3f_RN_%.3f'%(self.gliderModelType,yy,mm,dd,t1,t2,posNoise,curNoise)
        print gModName
        if self.LastTransModelLoaded != gModName:
            self.LoadTransModelForPlanner(self.saReplanner, gModName)
            self.saReplanner.CreateExpRiskGraph()
            #self.mrp.MRrp.CreateMinRiskGraph()
            
            #self.saMdp.ReInitializeMDP()
            self.LastTransModelLoaded = gModName
        
    def GetIndexedPolicy(self,yy,mm,dd,hr,mi,goal,**kwargs):
        '''
        Loads the policy corresponding to the goal, date, noise from shelf. 
        (Need to create these before-hand using StoreAllPolicies.py)
        Also need to ensure that all locations in this tour are also the same in StoreAllPolicies.py
        
        Args:
            yy, mm, dd, numDays (int) : Self-explanatory
            goal (tuple) : Goal in graph-coordinates
        
        Kwargs:
            posNoise (float) : How much noise in start position to assume. defaults to 0.01
            romsNoise (float): How much noise in ROMS predictions to assume. defaults to 0.01
            
            --- IMPORTANT ---- Always check to make sure that your risk-map is the right one!
            Policy will have the shelf-name in it, but you've got to be careful in any case.
        '''
        if kwargs.has_key('posNoise'):
            posNoise = kwargs['posNoise']
        else:
            posNoise = 0.010
        self.posNoise = posNoise
            
        if kwargs.has_key('theta'):
            self.theta = kwargs['theta']
            
        if kwargs.has_key('delta'):
            delta = kwargs['delta']
        else:
            delta = 0.00001
            
        if kwargs.has_key('numIters'):
            numIters = kwargs['numIters']
        else:
            numIters = 75
            
        if kwargs.has_key('gamma'):
            gamma = kwargs['gamma']
        else:
            gamma = 1.0
        self.gamma = gamma
        
        if kwargs.has_key('shelfDirectory'):
            shelfDirectory=kwargs['shelfDirectory']
        else:
            shelfDirectory=self.policyTableDir
        
        t1,t2 = self.GetBestTimeSlot(yy, mm, dd, hr, mi)
        
        policyStr = 'Pol_SARP_%04d%02d%02d_%d_%d_G_%d_%d_%.3f_%.3f'%(yy,mm,dd,t1,t2,goal[0],goal[1],posNoise,self.curNoise)
        if self.LastPolicyLoaded != policyStr:
            print '%s%s.shelve'%(shelfDirectory,policyStr)
            policyTable = shelve.open('%s%s.shelve'%(shelfDirectory,policyStr))
            keyForGoalAndNoise = 'G_%d_%d_PN_%.3f_WR_%.3f_WG_%.3f'%(goal[0],goal[1],posNoise,self.theta['w_r'],self.theta['w_g'])
            sarp_key = 'SARP_%s'%(keyForGoalAndNoise);
            if policyTable.has_key(sarp_key):
                print 'Loading policy for %s'%(policyStr)
                if policyTable[sarp_key].has_key('SP_DIST'):
                        self.saReplanner.dist = policyTable[sarp_key]['SP_DIST']
                if policyTable[sarp_key].has_key('SP_MST'):
                        self.saReplanner.sp_mst = policyTable[sarp_key]['SP_MST']
                self.LastPolicyLoaded = policyStr
            else:
                print 'Shortest path not found. Using Dijkstras algorithm to find it.'
                #self.saMdp.SetGoalAndRewardsAndInitTerminalStates(goal, self.theta)
                #self.saMdp.doValueIteration(delta,numIters)
                policyForKey={}
                sp_mst, sp_dist = self.saReplanner.GetShortestPathMST(goal)
                policyForKey['SP_DIST'] = sp_dist
                policyForKey['SP_MST'] = sp_mst
                policyTable[sarp_key] = policyForKey
                self.LastPolicyLoaded = policyStr
            policyTable.close()
            
    def LoadCurrentsFromShelve(self,yy,mm,dd,numDays):
        currentStr = 'Current_%04d%02d%02d_%d'%(yy,mm,dd,numDays)
        if self.LastCurrentDataLoaded!= currentStr:
            print 'Loading current data for %s'%(currentStr)
            self.saReplanner.GetRomsData(yy,mm,dd,numDays)
            self.predGM.GetRomsData(yy,mm,dd,numDays)
            self.saReplanner.gm.GetRomsData(yy,mm,dd,numDays)
            #self.mdp.gm.yy,self.mdp.gm.mm,self.mdp.gm.dd = yy,mm,dd
            self.LastCurrentDataLoaded = currentStr
            
    
    def DoPostSurfacingThings(self,latArray,lonArray):
        #self.PlotAndSaveExecution(latArray, lonArray)
        print 'Surfaced... Now doing Post Surfacing things!!!'
        yy,mm,dd,hr,mi = self.t.year,self.t.month,self.t.day,self.t.hour,self.t.minute
        goal = self.goal
        self.GetIndexedPolicy(yy, mm, dd, hr, mi, goal)
    
    def PlotAndSaveExecution(self,latArray,lonArray):
        if self.storeAllPngs:
            import matplotlib.axes as axes
            fig1 = plt.gcf()
            fig1.set_size_inches(12,6)
            ax1=plt.subplot(1,2,1)
            self.saReplanner.gm.PlotNewRiskMapFig(False)
            td = self.t - self.dtStart;
            self.tHrs = td.total_seconds()/3600.
            self.saReplanner.gm.PlotCurrentField(int(self.tHrs)%24)
            tempX, tempY = self.saReplanner.gm.GetXYfromLatLon(np.array(latArray), np.array(lonArray))
            ax1.plot(tempX, tempY, self.saReplanner.lineType)
            ax1.text(3,5,'Simulation at: %04d-%02d-%02d %.1f hrs'%(self.saReplanner.gm.yy,self.saReplanner.gm.mm,self.saReplanner.gm.dd,self.tHrs))
            ax1.text(3,4,'Goal : (%d,%d)'%(self.goal[0],self.goal[1]))
            # Also show the MDP policy on the other figure.
            ax2=plt.subplot(1,2,2)
            self.saReplanner.PlotMRpaths(self.goal,fig1)
            plt.title('MER MST')
             
            #plt.quiver([self.mdp.a[0]],[self.mdp.a[1]],[self.mdp.bx-int(self.mdp.a[0])],[self.mdp.by-int(self.mdp.a[1])],color='r',lw=2)
            plt.savefig('%s/Ensembles_SARP_%04d%02d%02d_%05.1f.png'%(self.pngDir,self.saReplanner.gm.yy,self.saReplanner.gm.mm,self.saReplanner.gm.dd,self.tHrs),bbox_inches='tight')
            plt.close()
            
    def RunSwitchingSARPforNhours(self,yy,mm,dd,hr,mi,start,goal,Nhrs,**kwargs):
        if kwargs.has_key('curNoise'):
            romsNoise = kwargs['curNoise']
        else:
            romsNoise = 0.01
        self.curNoise = romsNoise
        
        if kwargs.has_key('posNoise'):
            posNoise = kwargs['posNoise']
        else:
            posNoise = 0.01
        self.posNoise = posNoise
        
        if kwargs.has_key('lineType'):
            self.saReplanner.lineType = kwargs['lineType']
            
        if kwargs.has_key('simul_end'):
            simul_end = kwargs['simul_end']
        else:
            simul_end = datetime.datetime(yy+1,mm,dd,hr,mi) # Run until a year ahead if you want me to.
            
        if kwargs.has_key('num_hops'):
            self.saReplanner.num_hops = kwargs['num_hops']
        else:
            self.saReplanner.num_hops = 100
        
        self.totalRisk, self.totalTime, self.totalPathLength = 0., 0., 0.
        self.totNumHops = 0.
        self.CollisionReason, self.isSuccess = None, False
        
        numDays = int(Nhrs/24.0)+1
        rtc = RomsTimeConversion()
        #self.start = start
        self.goal = goal
        self.dtStart = datetime.datetime(yy,mm,dd,hr,mi) # Start...
        self.dtEnd = datetime.datetime(yy,mm,dd,hr,mi)+datetime.timedelta(hours=Nhrs)
        if self.dtEnd>simul_end:
            self.dtEnd = simul_end
        self.t = self.dtStart
        startTime=rtc.GetRomsIndexFromDateTime(yy,mm,dd,self.t)
        self.saReplanner.InitSARP_Simulation(start,goal,startTime,self.saReplanner.lineType,False)
        while( self.t < self.dtEnd ):
            dd,mm,yy = self.t.day,self.t.month,self.t.year
            hr,mi = self.t.hour, self.t.minute
            self.LoadTransitionModelsFromShelf(yy,mm,dd,hr,mi,self.posNoise,self.curNoise)
            self.LoadCurrentsFromShelve(yy, mm, dd, 1 )
            self.GetIndexedPolicy(yy, mm, dd, hr, mi, goal,curNoise = self.curNoise)
            simulTime = 5 # rtc.GetRomsIndexFromDateTime(yy,mm,dd,self.t)
            tempRiskReplanner, landedReplanner = self.saReplanner.SimulateAndPlotSARP_PolicyExecution_R(simulTime,self.PlotAndSaveExecution,self.DoPostSurfacingThings)
            print self.saReplanner.totalTime
            self.t = self.dtStart + datetime.timedelta( hours= self.saReplanner.totalTime/3600. )
            self.totalRisk = self.saReplanner.totalRisk;
            self.totalTime = (self.t- self.dtStart).total_seconds()/3600.
            self.totalDistFromGoal = self.saReplanner.distFromGoal
            self.totNumHops += 1
            self.totPathLength = self.saReplanner.totalPathLength/1000.
            print 'Risk=%f, TotalHops = %d, TotPathLen=%f'%(self.totalRisk,self.totNumHops,self.totPathLength)
            print self.t
            if self.saReplanner.possibleCollision == True:
                print 'Possible Collision. Quitting!'
                self.CollisionReason = self.saReplanner.CollisionReason
                break
            
            if self.saReplanner.isSuccess:
                print 'Reached Goal. Done. Therefore, Quitting!'
                self.isSuccess = self.saReplanner.isSuccess
                break
            
            if self.totNumHops >= self.saReplanner.num_hops:
                print 'Too many hops. Therefore Quitting!'
                break
            
        print 'Total Time=%.2f, Risk=%.4f, TotalHops = %d, TotPathLen=%f'%(self.totalTime,self.totalRisk,self.totNumHops,self.totPathLength)
