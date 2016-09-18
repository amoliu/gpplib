from gpplib.GliderFileTools import *
import random
from sets import Set
import gpplib
from gpplib.Utils import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.StateAction_NonStationaryMDP import *
from gpplib.LatLonConversions import *
from gpplib.PseudoWayptGenerator import *
import datetime
import ftplib

class WriteTransitionModel( SA_NS_MDP ):
    def __init__(self,shelfName='RiskMap3.shelf',sfcst_directory='./',dMax=1.5):
        super(WriteTransitionModel,self).__init__(shelfName,sfcst_directory,dMax)
        self.LastPolicyLoaded = ''
        self.shelfName = shelfName
        
        
    
    def GetTransitionModelFromShelf(self,yy,mm,dd,s_indx,e_indx,posNoise=None,shelfDirectory='.'):
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
        self.currentNoise = 0. 
        #import pdb; pdb.set_trace()
        shelfName = '%sgliderModelNS_GP_%04d%02d%02d_%d_%d_%.3f.shelf'%(shelfDirectory,yy,mm,dd,s_indx,e_indx,posNoise)
        print shelfName
        gmShelf = shelve.open( shelfName, writeback=False)
        self.gm.TransModel = gmShelf['TransModel']
        #if gmShelf.has_key('FinalLocs'):
        self.gm.FinalLocs = gmShelf['FinalLocs']
        if gmShelf.has_key('TracksInModel'):
            self.gm.TracksInModel = gmShelf['TracksInModel']
        gmShelf.close()
        
        
    def WriteTransitionModels(self,statesFileName,actionFileName,rewTransModelName):
        ''' Write out planning graph '''
        self.stateNumLookup={}
        self.revStateLookup = {}
        stateNum = 0
        # States
        stateF = open( statesFileName,'w')
        for a in self.locG.nodes():
            i, j = self.GetXYfromNodeStr(a)
            for t1 in range(0,self.tMax):
                stateStr = '%d,%d,%d'%(t1,i,j)
                self.stateNumLookup[stateStr] = stateNum; self.revStateLookup[stateNum] = (t1,i,j);
                outStr = '%d=%s\n'%(stateNum,stateStr)
                stateNum+=1
                stateF.write(outStr)
        stateF.close()
        
        W_,H_,T_ = None, None, None
        # Actions
        self.actionNumLookup={}
        self.revActionLookup={}
        actionNum = 0
        actionF = open( actionFileName, 'w')
        for a in self.locG.nodes():
            for b in self.locG.nodes():
                if a!=b:
                    i, j = self.GetXYfromNodeStr(a); x,y = self.GetXYfromNodeStr(b)
                    
                    for t1 in range(0,self.tMax+self.tExtra):
                        actionStr = '%d,%d,%d,%d,%d'%(t1,i,j,x,y)
                        self.actionNumLookup[actionStr] = actionNum; 
                        self.revActionLookup[actionNum] = (t1,i,j,x,y)
                        actionNum+=1
                        outStr = '%d=%s\n'%(actionNum,actionStr)
                        actionF.write( outStr )
        actionF.close()
        
        rewardF = open( rewTransModelName, 'w' )
        self.TransProbs = {}
        lastStateTrans = None
        # Transition Models
        for actionNum in range(len(self.actionNumLookup)):
            t1,i,j,x,y = self.revActionLookup[actionNum]
            firstStateStr = '%d,%d,%d'%(t1,i,j)
            if self.stateNumLookup.has_key( firstStateStr ):
                s1 = self.stateNumLookup[ firstStateStr ]
                stateTrans = '%d,%d,%d,%d,%d'%(t1,i,j,x,y)
                if self.gm.TransModel.has_key(stateTrans):
                    tPSize = self.gm.TransModel[ stateTrans ][1]
                    zeroLoc = self.gm.TransModel[ stateTrans ][0]
                    W_,H_,T_ = self.gm.TransModel[ stateTrans ][2].shape
                    transProbs = self.gm.TransModel[ stateTrans ][2]
                    for t2 in range(0,T_):
                        for b in range(int(tPSize)):
                            for a in range(int(tPSize)):
                                state_action = ( t1+t2, x+a-zeroLoc, y+b-zeroLoc )
                                tp,xp,yp = t1+t2, x+a-zeroLoc, y+b-zeroLoc 
                                if a!=b and transProbs[b][a][t2]>0.:
                                    state = t1,i,j; state_prime = tp, xp, yp
                                    if self.isOnMap(state_prime) and self.isOnMap(state):
                                        if not self.gm.ObsDetLatLon(self.gm.lat_pts[j],self.gm.lon_pts[i], \
                                            self.gm.lat_pts[y], self.gm.lon_pts[x]):
                                            nextStateStr = '%d,%d,%d'%(tp,xp,yp)
                                            if self.stateNumLookup.has_key(nextStateStr):
                                                    s2  = self.stateNumLookup[ nextStateStr ]
                                                    self.TransProbs[(s1,s2,actionNum)] = transProbs[b][a][t2]
                                                    if self.g.has_edge((t1,i,j),(tp,x,y)):
                                                        rwd = self.g.edge[(t1,i,j)][(tp,x,y)]['weight']
                                                        outStr = '%d,%d,%d=%f,%f\n'%(s1,actionNum,s2,rwd,self.TransProbs[(s1,s2,actionNum)])
                                                        rewardF.write( outStr )
                                            else:
                                                s2 = -1 # Bad! Bad! Bad! state...
                                                if lastStateTrans==(s1,s2,actionNum):
                                                    self.TransProbs[(s1,s2,actionNum)] += transProbs[b][a][t2]
                                                else:
                                                    self.TransProbs[(s1,s2,actionNum)] = transProbs[b][a][t2]
                                                rwd = -1.0
                                                outStr = '%d,%d,%d=%f,%f\n'%(s1,actionNum,s2,rwd,self.TransProbs[(s1,s2,actionNum)])
                                                rewardF.write( outStr )
                                                lastStateTrans = (s1,s2,actionNum)
                                            #else:
                                            #    print 'Not found: %s'%(nextStateStr)
        rewardF.close()
        #probTransF.close()
        
#        self.rewardsLookup={}
#        self.revRewardsLookup={}
#        rewardF = open( rewTransModelName, 'w' )
#        # Rewards
#        for u,v,d in self.g.edges(data=True):
#            t1,x1,y1 = u
#            t2,x2,y2 = v
#            s1Str, s2Str = '%d,%d,%d'%(t1,x1,y1), '%d,%d,%d'%(t2,x2,y2)
#            import pdb; pdb.set_trace()
#            if self.stateNumLookup.has_key(s1Str):
#                s1 = self.stateNumLookup[s1Str]
#                if self.stateNumLookup.has_key(s2Str):
#                    s2 = self.stateNumLookup[s2Str]
#                    action = self.actionNumLookup['%d,%d,%d,%d,%d'%(t1,x1,y1,x2,y2)]
#                    rwd = d['weight']
#                    outStr=''
#                    if self.TransProbs.has_key((s1,s2,action)):
#                        outStr = '%d,%d,%d=%f,%f\n'%(s1,action,s2,rwd,self.TransProbs[(s1,s2,action)])
#                    #else:
#                    #    outStr = '%d,%d,%d=%f,%f\n'%(s1,action,s2,rwd,1.0)
#                    rewardF.write( outStr )
#        rewardF.close()
            
                
if __name__=='__main__':
    yy,mm,dd = 2013,8,9
    posNoise = 0.001
    curNoise = None
    start,goal = (0,0), (6,2)
    
    statesFileName,actionFileName,transRewardModelName = 'states.txt','actions.txt','transitions.txt'
    
    print 'Write Transaction Model for a Non-Stationary MDP'
    #import gpplib.Utils
    conf = gpplib.Utils.GppConfig('../config.shelf')
    writeTransModel = WriteTransitionModel(conf.myDataDir+'RiskMap3.shelf',conf.romsDataDir)
    writeTransModel.GetTransitionModelFromShelf( yy, mm, dd, 0, 48, posNoise, conf.myDataDir+'/gliderModelNS/' )
    theta={}; theta['w_g'] = 100.; theta['w_r']= -1.0 
    writeTransModel.SetGoalAndRewardsAndInitTerminalStates(goal, theta)
    writeTransModel.WriteTransitionModels(statesFileName,actionFileName,transRewardModelName)
#    saNS_Mdp.doValueIteration(0.0001,25)
#    saNS_Mdp.DisplayPolicy()
#    plt.savefig('SAmdp.png')
#    saNS_Mdp.GetRomsData(yy, mm, dd, numDays, True)
#    saNS_Mdp.SimulateAndPlotMDP_PolicyExecution(start, goal, 0, True, 'r-')

        