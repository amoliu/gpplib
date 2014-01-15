from gpplib import *
from gpplib.StateActionMDP import *
from gpplib.LatLonConversions import *
import datetime
import ftplib


class SA_MDP2( SA_MDP ):
    ''' Sub-class of SA_MDP dealing with the new type of Risk-map
    '''
    def __init__(self,shelfName='RiskMap3.shelf',sfcst_directory='./',dMax=1.5):
        super(SA_MDP2,self).__init__(shelfName,sfcst_directory,dMax)
        self.LastPolicyLoaded = ''
        self.shelfName = shelfName
                
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
            gmShelf = shelve.open('%s/gliderModel3_%04d%02d%02d_%d.shelf'%(shelfDirectory,yy,mm,dd,numDays), writeback=False )
        if posNoise!=None:
            if currentNoise!=None:
                gmShelf = shelve.open('%s/gliderModel3_%04d%02d%02d_%d_%.3f_RN_%.3f.shelf'%(shelfDirectory,yy,mm,dd,numDays,posNoise,currentNoise),writeback=False)
            else:
                gmShelf = shelve.open('%s/gliderModel3_%04d%02d%02d_%d_%.3f.shelf'%(shelfDirectory,yy,mm,dd,numDays,posNoise), writeback=False)
        if posNoise==None and currentNoise!=None:
            gmShelf=shelve.open('%s/gliderModel3_%04d%02d%02d_%d_RN_%.3f.shelf'%(shelfDirectory,yy,mm,dd,numDays,currentNoise), writeback=False)     
        self.gm.TransModel = gmShelf['TransModel']
        #if gmShelf.has_key('FinalLocs'):
        self.gm.FinalLocs = gmShelf['FinalLocs']
        #if gmShelf.has_key('TracksInModel'):
        self.gm.TracksInModel = gmShelf['TracksInModel']
        gmShelf.close()
        # Now that we have loaded the new transition model, we better update our graph.
        self.ReInitializeMDP()
        
    
    def GetIndexedPolicy(self,yy,mm,dd,numDays,goal,**kwargs):
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
            posNoise = 0.01
            
        if kwargs.has_key('curNoise'):
            romsNoise = kwargs['curNoise']
        else:
            romsNoise = 0.01
        
        if kwargs.has_key('theta'):
            theta = kwargs['theta']
        else:
            theta = {'w_r':-1, 'w_g':1.}
        self.theta = theta
        
        if kwargs.has_key('delta'):
            delta = kwargs['delta']
        else:
            delta = 0.00001
            
        if kwargs.has_key('numIters'):
            numIters = kwargs['numIters']
        else:
            numIters = 50
            
        if kwargs.has_key('gamma'):
            gamma = kwargs['gamma']
        else:
            gamma = 1.0
        self.gamma = gamma
        
        if kwargs.has_key('shelfDirectory'):
            shelfDirectory=kwargs['shelfDirectory']
        else:
            shelfDirectory='.'
        
        policyStr = 'Pol_%s_%04d%02d%02d_%d_G_%d_%d_%.3f_%.3f_WR_%.3f_WG_%.3f'%(self.shelfName,yy,mm,dd,numDays,goal[0],goal[1],posNoise,curNoise,self.theta['w_r'],self.theta['w_g'])
        if self.LastPolicyLoaded != policyStr:
            policyTable = shelve.open('%s/PolicyTable_%04d%02d%02d_%d.shelve'%(shelfDirectory,yy,mm,dd,numDays))
            keyForGoalAndNoise = '%s_G_%d_%d_PN_%.3f_RN_%.3f_WR_%.3f_WG_%.3f'%(self.shelfName,goal[0],goal[1],posNoise,curNoise,self.theta['w_r'],self.theta['w_g'])
            mdp_key = 'MDP_%s'%(keyForGoalAndNoise);
            if policyTable.has_key(mdp_key):
                print 'Loading policy for %s'%(policyStr)
                if policyTable[mdp_key].has_key('U'):
                        self.mdp['U'] = policyTable[mdp_key]['U']
                if policyTable[mdp_key].has_key('polTree'):
                        self.gm2 = policyTable[mdp_key]['polTree']
                        
                self.LastPolicyLoaded = policyStr
            else:
                print 'Policy not found. Doing Value iteration to find it.'
                self.SetGoalAndRewardsAndInitTerminalStates(goal, theta)
                self.doValueIteration(delta,numIters)
                policyForKey={}
                policyForKey['U'] = self.mdp['U']
                policyForKey['polTree'] = self.gm2
                policyTable[mdp_key] = policyForKey
                self.LastPolicyLoaded = policyStr
            policyTable.close()



#start,goal = (0,6),(8,1)
print 'debugSA_MDP!'
import gpplib.Utils
conf = gpplib.Utils.GppConfig()

saMdp = SA_MDP2(conf.myDataDir+'RiskMap5.shelf',conf.romsDataDir)

yy,mm,dd,numDays = 2012,7,30,0
posNoise = 0.01
curNoise = 0.03
util = LLConvert()
goal_wLat, goal_wLon = 3329.485, -11819.777
goalLat, goalLon = util.WebbToDecimalDeg(goal_wLat,goal_wLon)
goalX,goalY = saMdp.gm.GetXYfromLatLon(goalLat,goalLon)

start_wLat, start_wLon = 3331.5620, -11844.1030
startLat,startLon = util.WebbToDecimalDeg(start_wLat, start_wLon)
startX, startY = saMdp.gm.GetXYfromLatLon(startLat,startLon)

start = (startX,startY); goal=(goalX,goalY)

rtc = RomsTimeConversion()
nHrsHence = 0.0
s_indx =  0
#rtc.GetRomsIndexNhoursFromNow(yy,mm,dd, nHrsHence)

saMdp.GetTransitionModelFromShelf(yy, mm, dd, numDays, posNoise, curNoise, conf.myDataDir+'NoisyGliderModels4' )
'''
saMdp.SetGoalAndInitTerminalStates(goal, 10.)
saMdp.doValueIteration(0.0001,50)
'''
saMdp.GetIndexedPolicy(yy,mm,dd,numDays,goal,theta = {'w_r':-5, 'w_g':5.})
saMdp.DisplayPolicy()
plt.title('MDP Policy with goal (%d,%d)'%(goal[0],goal[1]))
plt.savefig('SAmdp_Jan.png')
saMdp.GetRomsData(yy, mm, dd, numDays, True, True)
plt.figure()
saMdp.gm.PlotNewRiskMapFig()
saMdp.gm.PlotCurrentField(s_indx)
#import pdb; pdb.set_trace()
saMdp.SimulateAndPlotMDP_PolicyExecution(start, goal, s_indx, False, 'y-')
plt.savefig('SAmdp_execution_Jan.png')
