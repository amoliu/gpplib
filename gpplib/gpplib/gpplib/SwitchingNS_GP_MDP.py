import gpplib
from gpplib.SA_Replanner2 import *
from gpplib.StateAction_NonStationaryMDP import *
#from gpplib.StateActionMDPGP import *
from gpplib.Utils import *
from gpplib.LatLonConversions import *
from gpplib.PseudoWayptGenerator import *
import os, sys
import time, datetime

class SwitchingNS_GP_MDP:
    def __init__(self , **kwargs ):
        ''' Keyword Args:
                shelfLocation (str) : Location of the RiskMap shelf defaults to ('./')
                riskMapShelf (str)  : RiskMap.shelf defaults to ('RiskMap.shelf')
                romsDataDir  (str)  : Location of the ROMS data defaults to ('roms')
                gliderModelDir (str) : Location of the transition models of the glider ('NoisyGliderModels')
                pngDir (str) : Png directory
                policyTableDir (str) : Directory in which the pre-computed policies have been stored
                plannerType (str) : Type of planner (saMdp/saMdpGP)
        '''
        self.conf = gpplib.Utils.GppConfig()
        riskMapShelf, romsDataDir = \
            self.conf.myDataDir+'RiskMap3.shelf', self.conf.romsDataDir
        gliderModelDir, policyTableDir = \
            self.conf.myDataDir+'gliderModelNS/', 'ReplayPolicies/'
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
        else: self.plannerType = 'saNS_MDP'
        
        if kwargs.has_key('num_hops'): self.maxNumHops = kwargs['num_hops']
        else: self.maxNumHops = 250
        
        if kwargs.has_key('theta'):
            theta = kwargs['theta']
        else:
            theta = {'w_r':-1, 'w_g':100.}
        self.theta = theta
        
        self.mdp_type_str = 'NS_GP'
        
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
        
        self.saNS_Mdp = SA_NS_MDP( self.riskMapShelf, self.romsDataDir )
        self.saNS_Mdp.shelfName = self.riskMapShelf
        self.predGM = GliderModel(self.riskMapShelf, self.romsDataDir)
        self.TransStats = {}
        
        
    def GetBestRomsIndex(self,yy,mm,dd,hr,mi):
        ''' Args:
                yy,mm,dd,hr,mi : date and time we're looking for ROMS data from.
        '''
        rtc = RomsTimeConversion()
        romsIndx = rtc.GetRomsIndexFromDateTime(yy,mm,dd,datetime.datetime(yy,mm,dd,hr,mi,0))
        return romsIndx # The NS_MDP is always valid for 48 hours...
                
    def LoadTransModelForPlanner(self,planner,gModName):
        shelfName = '%s%s.shelf'%(self.gliderModelDir,gModName)
        print 'Loading Model from %s'%( shelfName )
        gmShelf = shelve.open(shelfName,writeback=False)
        planner.gm.TransModel = gmShelf['TransModel']
        planner.gm.FinalLocs = gmShelf['FinalLocs']
        #planner.gm.TracksInModel = gmShelf['TracksInModel']
        planner.gModel={}
        planner.gModel['TransModel'] = gmShelf['TransModel']
        gmShelf.close()       
        
    def LoadTransitionModelsFromShelf(self,yy,mm,dd,s_indx,e_indx,posNoise = 0.001):
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
        
        gModName = 'gliderModelNS_GP_%04d%02d%02d_%d_%d_%.3f'%(yy,mm,dd,s_indx,e_indx,posNoise)
        print gModName
        if self.LastTransModelLoaded != gModName:
            self.LoadTransModelForPlanner(self.saNS_Mdp, gModName)
            self.saNS_Mdp.ReInitializeMDP()
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
            posNoise = 0.001
        
        if kwargs.has_key('theta'):
            theta = kwargs['theta']
        else:
            theta = {'w_r':-1, 'w_g':10.}
            self.theta = theta
        
        if kwargs.has_key('delta'):
            delta = kwargs['delta']
        else:
            delta = 0.00001
            
        if kwargs.has_key('numIters'):
            numIters = kwargs['numIters']
        else:
            numIters = 25
            
        if kwargs.has_key('gamma'):
            gamma = kwargs['gamma']
        else:
            gamma = 1.0
        self.gamma = gamma
        
        if kwargs.has_key('shelfDirectory'):
            shelfDirectory=kwargs['shelfDirectory']
        else:
            shelfDirectory='.'
        
        numDays = 0
        
        policyStr = 'PolGP_%s_%04d%02d%02d_%d_G_%d_%d_%.3f'%(self.saNS_Mdp.shelfName,yy,mm,dd,numDays,goal[0],goal[1],posNoise)
        if self.LastPolicyLoaded != policyStr:
            policyTable = shelve.open('%s/PolicyTableGP_%04d%02d%02d_%d.shelve'%(shelfDirectory,yy,mm,dd,numDays))
            keyForGoalAndNoise = 'G_%d_%d_PN_%.3f_WR_%.3f_WG_%.3f'%(goal[0],goal[1],posNoise,self.theta['w_r'],self.theta['w_g'])
            mdp_key = 'MDP_%s'%(keyForGoalAndNoise);
            if policyTable.has_key(mdp_key):
                print 'Loading policy for %s'%(policyStr)
                if policyTable[mdp_key].has_key('U'):
                        self.saNS_Mdp.mdp['U'] = policyTable[mdp_key]['U']
                if policyTable[mdp_key].has_key('polTree'):
                        self.saNS_Mdp.gm2 = policyTable[mdp_key]['polTree']
                        
                self.LastPolicyLoaded = policyStr
            else:
                print 'Policy not found. Doing Value iteration to find it.'
                self.saNS_Mdp.SetGoalAndRewardsAndInitTerminalStates(goal, theta)
                self.saNS_Mdp.doValueIteration(delta,numIters)
                policyForKey={}
                policyForKey['U'] = self.saNS_Mdp.mdp['U']
                policyForKey['polTree'] = self.saNS_Mdp.gm2
                policyTable[mdp_key] = policyForKey
                self.LastPolicyLoaded = policyStr
            policyTable.close()
            
    def LoadCurrentsFromShelve(self,yy,mm,dd,numDays):
        currentStr = 'Current_%04d%02d%02d_%d'%(yy,mm,dd,numDays)
        if self.LastCurrentDataLoaded!= currentStr:
            print 'Loading current data for %s'%(currentStr)
            self.saNS_Mdp.GetRomsData(yy,mm,dd,numDays)
            self.predGM.GetRomsData(yy,mm,dd,numDays)
            self.saNS_Mdp.gm.GetRomsData(yy,mm,dd,numDays)
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
            self.saNS_Mdp.gm.PlotNewRiskMapFig(False)
            td = self.t - self.dtStart;
            self.tHrs = td.total_seconds()/3600.
            self.saNS_Mdp.gm.PlotCurrentField(int(self.tHrs)%24)
            tempX, tempY = self.saNS_Mdp.gm.GetXYfromLatLon(np.array(latArray), np.array(lonArray))
            ax1.plot(tempX, tempY, self.saNS_Mdp.lineType)
            ax1.text(3,5,'Simulation at: %04d-%02d-%02d %.1f hrs'%(self.saNS_Mdp.gm.yy,self.saNS_Mdp.gm.mm,self.saNS_Mdp.gm.dd,self.tHrs))
            ax1.text(3,4,'Goal : (%d,%d)'%(self.goal[0],self.goal[1]))
            # Also show the MDP policy on the other figure.
            ax2=plt.subplot(1,2,2)
            self.saNS_Mdp.DisplayPolicyAtTimeT(int(self.tHrs)%48,fig1) 
            plt.title('SA NS-GP MDP  Policy at time %d'%(int(self.tHrs%48)))
             
            #plt.quiver([self.mdp.a[0]],[self.mdp.a[1]],[self.mdp.bx-int(self.mdp.a[0])],[self.mdp.by-int(self.mdp.a[1])],color='r',lw=2)
            plt.savefig('%s/Ensembles_NS_MDP_Goal_(%d_%d)_%04d%02d%02d_%05.1f.png'%(self.pngDir,self.goal[0],self.goal[1],self.saNS_Mdp.gm.yy,self.saNS_Mdp.gm.mm,self.saNS_Mdp.gm.dd,self.tHrs),bbox_inches='tight')
            plt.close()
            
    def RunSwitchingMDPforNhours(self,yy,mm,dd,hr,mi,start,goal,Nhrs,**kwargs):
        if kwargs.has_key('curNoise'):
            romsNoise = kwargs['curNoise']
        else:
            romsNoise = 0.01
        self.curNoise = romsNoise
        
        if kwargs.has_key('posNoise'):
            posNoise = kwargs['posNoise']
        else:
            posNoise = 0.001
        self.posNoise = posNoise
        
        if kwargs.has_key('lineType'):
            self.saNS_Mdp.lineType = kwargs['lineType']
        
        if kwargs.has_key('num_hops'):
            self.saNS_Mdp.num_hops = kwargs['num_hops']
        else:
            self.saNS_Mdp.num_hops = 100
        
        if kwargs.has_key('simul_end'):
            simul_end = kwargs['simul_end']
        else:
            simul_end = datetime.datetime(yy+1,mm,dd,hr,mi) # Run until a year ahead if you want me to.
        
        self.totalRisk, self.totalTime, self.totalPathLength = 0., 0., 0.
        self.totNumHops = 0.
        self.CollisionReason, self.isSuccess = None, False
        
        numDays = int(Nhrs/24.0)+1
        rtc = RomsTimeConversion()
        #self.start = start
        self.goal = goal
        #self.saNS_Mdp.gs.acceptR = 0.8
        self.dtStart = datetime.datetime(yy,mm,dd,hr,mi) # Start...
        self.dtEnd = datetime.datetime(yy,mm,dd,hr,mi)+datetime.timedelta(hours=Nhrs)
        if self.dtEnd>simul_end:
            self.dtEnd = simul_end
        self.t = self.dtStart
        startTime=rtc.GetRomsIndexFromDateTime(yy,mm,dd,self.t) # saMdp
        self.saNS_Mdp.InitMDP_Simulation(start,goal,startTime,self.saNS_Mdp.lineType,False)
        while( self.t < self.dtEnd ):
            #import pdb; pdb.set_trace()
            dd,mm,yy = self.t.day,self.t.month,self.t.year
            hr,mi = self.t.hour, self.t.minute
            #self.LoadTransitionModelsFromShelf(yy,mm,dd,0,48,self.posNoise)
            self.LoadCurrentsFromShelve(yy, mm, dd, 1 )
            self.GetIndexedPolicy(yy, mm, dd, hr, mi, goal,curNoise = self.curNoise)
            simulTime = 5 # rtc.GetRomsIndexFromDateTime(yy,mm,dd,self.t)
            tempRiskMDP, landedMDP = self.saNS_Mdp.SimulateAndPlotMDP_PolicyExecution_R(simulTime,self.PlotAndSaveExecution,self.DoPostSurfacingThings)
            print self.saNS_Mdp.totalTime
            self.t = self.dtStart + datetime.timedelta( hours= self.saNS_Mdp.totalTime/3600. )
            self.totalRisk = self.saNS_Mdp.totalRisk;
            self.totalTime = (self.t- self.dtStart).total_seconds()/3600.
            self.totalDistFromGoal = self.saNS_Mdp.distFromGoal
            print 'Total distance from goal=%f'%(self.totalDistFromGoal)
            self.totNumHops += 1
            #if self.totNumHops > 10:
            #    import pdb; pdb.set_trace()
            self.totPathLength = self.saNS_Mdp.totalPathLength/1000.
            print 'Risk=%f, TotalHops = %d, TotPathLen=%f'%(self.totalRisk,self.totNumHops,self.totPathLength)
            print self.t
            if self.saNS_Mdp.possibleCollision == True:
                print 'Possible Collision. Quitting!'
                self.CollisionReason = self.saNS_Mdp.CollisionReason
                break
            
            if self.saNS_Mdp.isSuccess:
                print 'Reached Goal. Done. Therefore, Quitting!'
                self.isSuccess = self.saNS_Mdp.isSuccess
                break
            
            if self.totNumHops >= self.maxNumHops:
                print 'Too many hops. Therefore Quitting!'
                self.CollisionReason = 'MaxHopsExceeded'
                break
                
            
        print 'Total Time=%.2f, Risk=%.4f, TotalHops = %d, TotPathLen=%f'%(self.totalTime,self.totalRisk,self.totNumHops,self.totPathLength)

