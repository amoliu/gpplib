'''
@Summary: This program implements a class which handles the running of MDP/MER replanners which are based upon
the State-Action pair instead of the older State-only 
@Author: Arvind A de Menezes Pereira
@Date: 2012-5-28


'''
#!env python
import UseAgg
import os
import gpplib
import sys
from gpplib.Replanner import *
from gpplib.StateMDP import *
from gpplib.SA_Replanner import *
from gpplib.StateActionMDP import *
from gpplib.RuleBasedRePlanner import *

class sa_mdpRbReplanner:
    ''' MDP Replanner test class.
    '''
    def __init__(self,riskMapShelf='RiskMap.shelf',romsDataDirectory='/Users/arvind/data/roms/',myDataDir='./'):
        self.pngDir = 'pngs_rrp'
	self.myDataDir = myDataDir
        self.lastGoal = (-1,-1)
        self.numRuns = 10
        try:
            os.mkdir(self.pngDir)
        except OSError as (errno,strerror):
            pass
        conf = gpplib.Utils.GppConfig()
        self.samdp = SA_MDP(riskMapShelf,romsDataDirectory)
        '''
        self.rp = SA_Replanner(riskMapShelf,romsDataDirectory)
        self.samdp = SA_MDP(riskMapShelf,romsDataDirectory)
        self.MRrp = Replanner(riskMapShelf,romsDataDirectory)
        self.smdp = MDP(riskMapShelf,romsDataDirectory)
        '''
        self.rbrp = RuleBasedReplanner(riskMapShelf,romsDataDirectory,myDataDir)
        
    def GetCorrLocLists(self,BinCorrMat):
        GoodCorrLocs,BadCorrLocs=[],[]
        sX,sY = BinCorrMat.shape
        for y in range(sY):
            for x in range(sX):
                if BinCorrMat[x,y]==1.0:
                    GoodCorrLocs.append((x,y))
                if BinCorrMat[x,y]==0.0:
                    BadCorrLocs.append((x,y))
        return GoodCorrLocs, BadCorrLocs
    
    def GetGoodBadCorrLocs(self,Thresh=0.5,TimeScale=48):
        CorrShelf = shelve.open('CorrModel_%.2f_%d.shelf'%(Thresh,TimeScale),writeback=False)
        BinCorrMatU,BinCorrMatV,BinCorrMatS = CorrShelf['BinCorrMatU'],CorrShelf['BinCorrMatV'],CorrShelf['BinCorrMatS']
        CorrShelf.close()
        GoodCorrLocsU,BadCorrLocsU = self.GetCorrLocLists(BinCorrMatU)
        GoodCorrLocsV,BadCorrLocsV = self.GetCorrLocLists(BinCorrMatV)
        GoodCorrLocsS,BadCorrLocsS = self.GetCorrLocLists(BinCorrMatS)
        sX,sY = BinCorrMatS.shape
        
        return GoodCorrLocsU,BadCorrLocsU,GoodCorrLocsV,BadCorrLocsV,GoodCorrLocsS,BadCorrLocsS

    def RunMDPandReplanners(self,start,goal,yy,mm,dd,numDays,startT = 1):
        saMdpResult, RpResult, MRpResult, sMdpResult, RbRpResult = {}, {}, {}, {}, {}
	self.yy, self.mm, self.dd, self.numDays = yy,mm,dd,numDays
        if goal!= self.lastGoal:
            '''
            self.samdp.SetGoalAndInitTerminalStates(goal,10.)
            print 'Doing Value Iteration for State-Action MDP'
            self.samdp.doValueIteration(0.0001,50)
            Xpolicy,Ypolicy = self.samdp.DisplayPolicy()
            plt.title('SA-MDP Policy with goal (%d,%d)'%(goal[0],goal[1]))
            plt.savefig('%s/SA_MDP_Policy_Goal_%04d%02d%02d_%d_%d.png'%(self.pngDir,yy,mm,dd,goal[0],goal[1]))
            plt.close()
            
            self.smdp.SetGoalAndInitTerminalStates(goal,10.)
            print 'Doing Value Iteration'
            self.smdp.doValueIteration(0.0001,50)
            Xpolicy,Ypolicy = self.smdp.DisplayPolicy()
            plt.title('S-MDP Policy with goal (%d,%d)'%(goal[0],goal[1]))
            plt.savefig('%s/S_MDP_Policy_Goal_%04d%02d%02d_%d_%d.png'%(self.pngDir,yy,mm,dd,goal[0],goal[1]))
            plt.close()
            
            self.sp_mst, self.dist = self.rp.GetShortestPathMST(goal)
            self.sp_mstMR, self.distMR = self.MRrp.GetShortestPathMST(goal)
            
            self.rp.PlotMRpaths(goal); 
            plt.title('SA_Replanner Min-Exp-Risk MST with goal (%d,%d)'%(goal[0],goal[1]))
            plt.savefig('%s/SA_Replanner_MER_MST_%04d%02d%02d_%d_%d.png'%(self.pngDir,yy,mm,dd,goal[0],goal[1]))
            plt.close()
            
            self.MRrp.PlotMRpaths(goal)
            plt.title('Replanner Min-Risk MST with goal (%d,%d)'%(goal[0],goal[1]))
            plt.savefig('%s/Replanner_MR_MST_%04d%02d%02d_%d_%d.png'%(self.pngDir,yy,mm,dd,goal[0],goal[1]))
            plt.close()
            '''
            self.lastGoal = goal
            
        plt.figure()
        
        self.samdp.gm.PlotNewRiskMapFig(startT)
        '''
        saMdpResult['Risk'], saMdpResult['pathLength'], saMdpResult['Time'] = [], [], []
        saMdpResult['numHops'], saMdpResult['distFromGoal'], saMdpResult['CollisionReason'] = [], [], []
        saMdpResult['isSuccess']= []; saMdpResult['startTime'] = []
        saMdpResult['finalLoc'] = []
        
        RpResult['Risk'], RpResult['pathLength'], RpResult['Time'] = [], [], []
        RpResult['numHops'], RpResult['distFromGoal'], RpResult['CollisionReason'] = [], [], []
        RpResult['isSuccess']= []; RpResult['startTime'] = []
        RpResult['finalLoc'] = []
        
        MRpResult['Risk'], MRpResult['pathLength'], MRpResult['Time'] = [], [], []
        MRpResult['numHops'], MRpResult['distFromGoal'], MRpResult['CollisionReason'] = [], [], []
        MRpResult['isSuccess']= []; MRpResult['startTime'] = []
        MRpResult['finalLoc'] = []
        
        sMdpResult['Risk'], sMdpResult['pathLength'], sMdpResult['Time'] = [], [], []
        sMdpResult['numHops'], sMdpResult['distFromGoal'], sMdpResult['CollisionReason'] = [], [], []
        sMdpResult['isSuccess']= []; sMdpResult['startTime'] = []
        sMdpResult['finalLoc'] = []
        '''
        RbRpResult['Risk'], RbRpResult['pathLength'], RbRpResult['Time'] = [], [], []
        RbRpResult['numHops'], RbRpResult['distFromGoal'], RbRpResult['CollisionReason'] = [], [], []
        RbRpResult['isSuccess']= []; RbRpResult['startTime'] = []
        RbRpResult['finalLoc'] = []
        
        '''
        s_totRiskMDP, s_totHopsMDP, s_totSuccessMDP, s_totCrashesMDP, s_totFalseStartsMDP, s_totTimeMDP, s_totDistMDP = 0.,0.,0.,0.,0.,0.,0.        
        sa_totRiskMDP, sa_totHopsMDP, sa_totSuccessMDP, sa_totCrashesMDP, sa_totFalseStartsMDP, sa_totTimeMDP, sa_totDistMDP = 0.,0.,0.,0.,0.,0.,0.
        totRiskRP, totHopsRP, totSuccessRP, totCrashesRP, totFalseStartsRP, totTimeRP, totDistRP = 0.,0.,0.,0.,0.,0.,0.
        totRiskMRP, totHopsMRP, totSuccessMRP, totCrashesMRP, totFalseStartsMRP, totTimeMRP, totDistMRP = 0.,0.,0.,0.,0.,0.,0.
        sa_totNonStartsMDP, totNonStartsRP, sa_totNanMDP, totNanRP, totNonStartsMRP, totNanMRP  = 0,0, 0, 0, 0, 0
        sa_totNoPolicyMDP, totNoPolicyRP, totNoPolicyMRP = 0, 0, 0
        s_totNoPolicyMDP, s_totNonStartsMDP, s_totNanMDP = 0,0,0
        '''
        totRiskRRP, totHopsRRP, totSuccessRRP, totCrashesRRP, totFalseStartsRRP, totTimeRRP, totDistRRP = 0.,0.,0.,0.,0.,0.,0.
        totNoPolicyRRP, totNonStartsRRP, totNanRRP = 0,0,0
        
        for i in range(0,self.numRuns):
            '''
            tempRiskMDP, landedMDP = self.samdp.SimulateAndPlotMDP_PolicyExecution(start,goal,startT+i, False )
            saMdpResult['Risk'].append(self.samdp.gs.totalRisk); saMdpResult['pathLength'].append(self.samdp.gs.totalPathLength/1000.)
            saMdpResult['Time'].append(self.samdp.gs.totalTime/3600.); saMdpResult['numHops'].append(self.samdp.gs.numHops)
            saMdpResult['CollisionReason'].append(self.samdp.gs.CollisionReason); saMdpResult['isSuccess'].append(self.samdp.gs.isSuccess)
            saMdpResult['distFromGoal'].append(self.samdp.gs.distFromGoal); saMdpResult['startTime'].append(startT+i)
            saMdpResult['finalLoc'].append((self.samdp.gs.finX,self.samdp.gs.finY))
            sa_totRiskMDP+=self.samdp.gs.totalRisk; sa_totHopsMDP+=self.samdp.gs.numHops; sa_totTimeMDP+=self.samdp.gs.totalTime/3600.; sa_totDistMDP+=self.samdp.gs.totalPathLength/1000.
            if self.samdp.gs.isSuccess==True:
                sa_totSuccessMDP+=1
            
            if self.samdp.gs.CollisionReason!=None:
                if self.samdp.gs.CollisionReason=='Obstacle':
                    sa_totCrashesMDP+=1
                else:
                    if self.samdp.gs.CollisionReason=='RomsNansAtStart':
                        sa_totNonStartsMDP+=1
                    else:
                        if self.samdp.gs.CollisionReason == 'RomsNanLater':
                            sa_totNanMDP +=1
                        elif self.samdp.gs.CollisionReason == 'DidNotFindPolicy':
                            sa_totNoPolicyMDP +=1
                            
            tempRiskMDP, landedMDP = self.smdp.SimulateAndPlotMDP_PolicyExecution(start,goal,startT+i, False, 'm-' )
            sMdpResult['Risk'].append(self.smdp.gs.totalRisk); sMdpResult['pathLength'].append(self.smdp.gs.totalPathLength/1000.)
            sMdpResult['Time'].append(self.smdp.gs.totalTime/3600.); sMdpResult['numHops'].append(self.smdp.gs.numHops)
            sMdpResult['CollisionReason'].append(self.smdp.gs.CollisionReason); sMdpResult['isSuccess'].append(self.smdp.gs.isSuccess)
            sMdpResult['distFromGoal'].append(self.smdp.gs.distFromGoal); sMdpResult['startTime'].append(startT+i)
            sMdpResult['finalLoc'].append((self.smdp.gs.finX,self.smdp.gs.finY))
            s_totRiskMDP+=self.smdp.gs.totalRisk; s_totHopsMDP+=self.smdp.gs.numHops; s_totTimeMDP+=self.smdp.gs.totalTime/3600.; s_totDistMDP+=self.smdp.gs.totalPathLength/1000.
            if self.smdp.gs.isSuccess==True:
                s_totSuccessMDP+=1
            
            if self.smdp.gs.CollisionReason!=None:
                if self.smdp.gs.CollisionReason=='Obstacle':
                    s_totCrashesMDP+=1
                else:
                    if self.smdp.gs.CollisionReason=='RomsNansAtStart':
                        s_totNonStartsMDP+=1
                    else:
                        if self.smdp.gs.CollisionReason == 'RomsNanLater':
                            s_totNanMDP +=1
                        elif self.smdp.gs.CollisionReason == 'DidNotFindPolicy':
                            s_totNoPolicyMDP +=1
            
            tempRiskMER,landedMER= self.rp.SimulateAndPlotMR_PolicyExecution(start,goal,self.sp_mst,startT+i,False)
            RpResult['Risk'].append(self.rp.gs.totalRisk); RpResult['pathLength'].append(self.rp.gs.totalPathLength/1000.)
            RpResult['Time'].append(self.rp.gs.totalTime/3600.); RpResult['numHops'].append(self.rp.gs.numHops)
            RpResult['CollisionReason'].append(self.rp.gs.CollisionReason); RpResult['isSuccess'].append(self.rp.gs.isSuccess)
            RpResult['distFromGoal'].append(self.rp.gs.distFromGoal); RpResult['startTime'].append(startT+i)
            RpResult['finalLoc'].append((self.rp.gs.finX,self.rp.gs.finY))
            totRiskRP+=self.rp.gs.totalRisk; totHopsRP+=self.rp.gs.numHops; totTimeRP+=self.rp.gs.totalTime/3600.; totDistRP+=self.rp.gs.totalPathLength/1000.
            if self.rp.gs.isSuccess==True:
                totSuccessRP+=1
            
            if self.rp.gs.CollisionReason!=None:
                if self.rp.gs.CollisionReason=='Obstacle':
                    totCrashesRP+=1
                else:
                    if self.rp.gs.CollisionReason=='RomsNanAtStart':
                        totNonStartsRP+=1
                    else:
                        if self.rp.gs.CollisionReason == 'RomsNanLater':
                            totNanRP +=1
                        elif self.rp.gs.CollisionReason == 'DidNotFindPolicy':
                            totNoPolicyRP +=1
                            
            tempRiskMRP, landedMRP = self.MRrp.SimulateAndPlotMR_PolicyExecution(start,goal,self.sp_mstMR,startT+i,False,'g-')
            MRpResult['Risk'].append(self.MRrp.gs.totalRisk); MRpResult['pathLength'].append(self.MRrp.gs.totalPathLength/1000.)
            MRpResult['Time'].append(self.MRrp.gs.totalTime/3600.); MRpResult['numHops'].append(self.MRrp.gs.numHops)
            MRpResult['CollisionReason'].append(self.MRrp.gs.CollisionReason); MRpResult['isSuccess'].append(self.MRrp.gs.isSuccess)
            MRpResult['distFromGoal'].append(self.MRrp.gs.distFromGoal); MRpResult['startTime'].append(startT+i)
            MRpResult['finalLoc'].append((self.MRrp.gs.finX,self.MRrp.gs.finY))
            totRiskMRP+=self.MRrp.gs.totalRisk; totHopsMRP+=self.MRrp.gs.numHops; totTimeMRP+=self.MRrp.gs.totalTime/3600.; totDistMRP+=self.MRrp.gs.totalPathLength/1000.
            if self.MRrp.gs.isSuccess==True:
                    totSuccessMRP+=1
                
            if self.MRrp.gs.CollisionReason!=None:
                    if self.MRrp.gs.CollisionReason=='Obstacle':
                        totCrashesMRP+=1
                    else:
                        if self.MRrp.gs.CollisionReason=='RomsNansAtStart':
                            totNonStartsMRP+=1
                        else:
                            if self.MRrp.gs.CollisionReason == 'RomsNanLater':
                                totNanMRP +=1
                            elif self.MRrp.gs.CollisionReason == 'DidNotFindPolicy':
                            	totNoPolicyMRP +=1
            '''
            tempRiskRRP, landedRRP = self.rbrp.SimulateAndPlotRBRP_PolicyExecution(start,goal,startT+i,False,'c-')
            RbRpResult['Risk'].append(self.rbrp.gs.totalRisk); RbRpResult['pathLength'].append(self.rbrp.gs.totalPathLength/1000.)
            RbRpResult['Time'].append(self.rbrp.gs.totalTime/3600.); RbRpResult['numHops'].append(self.rbrp.gs.numHops)
            RbRpResult['CollisionReason'].append(self.rbrp.gs.CollisionReason); RbRpResult['isSuccess'].append(self.rbrp.gs.isSuccess)
            RbRpResult['distFromGoal'].append(self.rbrp.gs.distFromGoal); RbRpResult['startTime'].append(startT+i)
            RbRpResult['finalLoc'].append((self.rbrp.gs.finX,self.rbrp.gs.finY))
            totRiskRRP+=self.rbrp.gs.totalRisk; totHopsRRP+=self.rbrp.gs.numHops; totTimeRRP+=self.rbrp.gs.totalTime/3600.; totDistRRP+=self.rbrp.gs.totalPathLength/1000.
            if self.rbrp.gs.isSuccess==True:
                    totSuccessRRP+=1
                
            if self.rbrp.gs.CollisionReason!=None:
                    if self.rbrp.gs.CollisionReason=='Obstacle':
                        totCrashesRRP+=1
                    else:
                        if self.rbrp.gs.CollisionReason=='RomsNansAtStart':
                            totNonStartsRRP+=1
                        else:
                            if self.rbrp.gs.CollisionReason == 'RomsNanLater':
                                totNanRRP +=1
                            elif self.rbrp.gs.CollisionReason == 'DidNotFindPolicy':
                                totNoPolicyRRP +=1


        
        # Now that we have everything, store the totals and compute averages.
        '''
        saMdpResult['TotalRisk'] = sa_totRiskMDP; saMdpResult['Crashes'] = sa_totCrashesMDP; saMdpResult['NonStarts'] = sa_totNonStartsMDP;
        saMdpResult['RomsNans'] = sa_totNanMDP 
        saMdpResult['numRuns'] = self.numRuns;  saMdpResult['Successes'] = sa_totSuccessMDP;
        saMdpResult['U'] = self.samdp.mdp['U']
        saMdpResult['start'] = start; saMdpResult['goal'] = goal;
        
        sMdpResult['TotalRisk'] = s_totRiskMDP; sMdpResult['Crashes'] = s_totCrashesMDP; sMdpResult['NonStarts'] = s_totNonStartsMDP;
        sMdpResult['RomsNans'] = s_totNanMDP 
        sMdpResult['numRuns'] = self.numRuns;  sMdpResult['Successes'] = s_totSuccessMDP;
        sMdpResult['U'] = self.smdp.mdp['U']
        sMdpResult['start'] = start; sMdpResult['goal'] = goal;
        
        RpResult['Successes'] = totSuccessRP; RpResult['numRuns']= self.numRuns;
        RpResult['RomsNans'] = totNanRP
        RpResult['start'] = start; RpResult['goal'] = goal
        RpResult['MST'] = self.sp_mst
        RpResult['TotalRisk'] = totRiskRP; RpResult['Crashes'] = totCrashesRP; RpResult['NonStarts'] = totNonStartsRP;
        
        MRpResult['TotalRisk'] = totRiskMRP; MRpResult['Crashes'] = totCrashesMRP; MRpResult['NonStarts'] = totNonStartsMRP;
        MRpResult['RomsNans'] = totNanMRP
        MRpResult['numRuns'] = self.numRuns; MRpResult['Successes'] = totSuccessMRP;
        MRpResult['start'] = start; MRpResult['goal'] = goal;
        MRpResult['MST'] = self.sp_mstMR; MRpResult['Dist'] = self.distMR;
        '''
        RbRpResult['Successes'] = totSuccessRRP; RbRpResult['numRuns']= self.numRuns;
        RbRpResult['RomsNans'] = totNanRRP
        RbRpResult['start'] = start; RbRpResult['goal'] = goal
        RbRpResult['MST'] = self.rbrp.sp_mst
        RbRpResult['U'] = self.rbrp.samdp.mdp['U']
        RbRpResult['TotalRisk'] = totRiskRRP; RbRpResult['Crashes'] = totCrashesRRP; RbRpResult['NonStarts'] = totNonStartsRRP;
        
        #
        self.samdp.gm.PlotCurrentField(startT);
        plt.title('Ensembles simulated on %04d-%02d-%02d: (%d,%d) to (%d,%d)'%(yy,mm,dd,start[0],start[1],goal[0],goal[1]))
        '''
        plt.text(1.5,10,'Risks: RRP=%.2f, MDP=%.2f, SAmdp=%.2f, RP=%.2f, MR=%.2f'%(totRiskRRP,s_totRiskMDP,sa_totRiskMDP,totRiskRP,totRiskMRP))
        plt.text(1.5,9.5,'Avg. Hops: RRP=%.2f, MDP=%.2f, SAmdp=%.2f, RP=%.2f, MR=%.2f'%(totHopsRRP/float(self.numRuns),s_totHopsMDP/float(self.numRuns),sa_totHopsMDP/float(self.numRuns),totHopsRP/float(self.numRuns),totHopsMRP/float(self.numRuns)))
        plt.text(1.5,9,'Avg.Path-Len: RRP=%.2f, MDP=%.2f, SAmdp=%.2f, RP=%.2f, MR=%.2f'%(totDistRRP/float(self.numRuns),s_totDistMDP/float(self.numRuns),sa_totDistMDP/float(self.numRuns),\
                                                    totDistRP/float(self.numRuns), totDistMRP/float(self.numRuns)))
        plt.text(1.5,8.5,'Successes: RRP=%d, SMDP=%d, SAmdp=%d, RP=%d, MR=%d'%(totSuccessRRP,s_totSuccessMDP,sa_totSuccessMDP,totSuccessRP,totSuccessMRP))
        plt.text(1.5,8,'Non-Starts: RRP=%d, SMDP=%d, SAmdp=%d, RP=%d, MR=%d'%(totNonStartsRRP,s_totNonStartsMDP,sa_totNonStartsMDP,totNonStartsRP,totNonStartsMRP))
        plt.text(1.5,7.5,'Crashes: RRP=%d, SMDP=%d, SAmdp=%d, RP=%d, MR=%d'%(totCrashesRRP,s_totCrashesMDP,sa_totCrashesMDP,totCrashesRP,totCrashesMRP))
        '''
        plt.text(1.5,10,'Risks: RRP=%.2f'%totRiskRRP)
        plt.text(1.5,9.5,'Avg.Hops: RRP=%.2f'%(totHopsRRP/float(self.numRuns)))
        plt.text(1.5,9,'Avg.Path-Len: RRP=%.2f'%(totDistRRP/float(self.numRuns)))
        plt.text(1.5,8.5,'Successes: RRP=%d'%totSuccessRRP)
        plt.text(1.5,8,'Non-Starts: RRP=%d'%totNonStartsRRP)
        plt.text(1.5,7.5,'Crashes: RRP=%d'%totCrashesRRP)
        plt.savefig('%s/Ensembles_%04d%02d%02d_%d_%d_%d_%d.png'%(self.pngDir,self.yy,self.mm,self.dd,start[0],start[1],goal[0],goal[1]))
        plt.close()
        
        #return saMdpResult, RpResult, MRpResult, sMdpResult, RbRpResult
        return RbRpResult
    
conf = gpplib.Utils.GppConfig()
mrp = sa_mdpRbReplanner(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir )
GoodCorrLocsU,BadCorrLocsU,GoodCorrLocsV,BadCorrLocsV,GoodCorrLocsS,BadCorrLocsS = mrp.GetGoodBadCorrLocs()
yy,mm,dd,numDays = 2011,6,1,2
posNoise, romsNoise = 0.1, 0.01

mrp.samdp.GetTransitionModelFromShelf(yy,mm,dd,numDays,posNoise,romsNoise,conf.myDataDir+'NoisyGliderModels2')
'''
mrp.smdp.GetTransitionModelFromShelf(yy,mm,dd,numDays,posNoise,romsNoise,conf.myDataDir+'NoisyGliderModels2')
mrp.rp.GetTransitionModelFromShelf(yy,mm,dd,numDays,posNoise,romsNoise,conf.myDataDir+'NoisyGliderModels2')
mrp.MRrp.GetTransitionModelFromShelf(yy,mm,dd,numDays,posNoise,romsNoise,conf.myDataDir+'NoisyGliderModels2')
'''
mrp.rbrp.GetTransitionModelFromShelf(yy,mm,dd,numDays,posNoise,romsNoise,conf.myDataDir+'NoisyGliderModels2')
'''
mrp.rp.CreateExpRiskGraph()
mrp.MRrp.CreateMinRiskGraph()

u,v,time1,depth,lat,lon = mrp.rp.GetRomsData(yy,mm,dd,numDays)
u,v,time1,depth,lat,lon = mrp.MRrp.GetRomsData(yy,mm,dd,numDays)
u,v,time1,depth,lat,lon = mrp.smdp.GetRomsData(yy,mm,dd,numDays)
'''
u,v,time1,depth,lat,lon = mrp.samdp.GetRomsData(yy,mm,dd,numDays)
mrp.rbrp.GetRomsData(yy,mm,dd,numDays)

startT = 0
plt.figure(); mrp.samdp.gm.PlotNewRiskMapFig(); mrp.samdp.gm.PlotCurrentField(startT); 
plt.title('Currents at %d hrs on %04d-%02d-%02d'%(startT,yy,mm,dd)); 
plt.savefig('%s/Currents_%04d%02d%02d_%dhrs.png'%(mrp.pngDir,yy,mm,dd,startT))
plt.close()


#mdpResultsG,rpResultsG,MRrpResultsG, sMdpResultsG, RbRpResultsG = [], [], [], [], []
#allMdpResults,allRpResults,allMRrpResults, all_sMdpResults, all_RbRpResults = [], [], [], [], []

RbRpResultsG, all_RbRpResults = [], []

for locA in GoodCorrLocsS:
    for locB in GoodCorrLocsS:
        if locA!=locB  and not mrp.samdp.gm.GetObs(mrp.samdp.gm.lat_pts[locA[1]],mrp.samdp.gm.lon_pts[locA[0]]) \
                and not mrp.samdp.gm.GetObs(mrp.samdp.gm.lat_pts[locB[1]],mrp.samdp.gm.lon_pts[locB[0]]):
            if mrp.samdp.gm.lpGraph.has_node('(%d,%d)'%(locA[0],locA[1])) and mrp.samdp.gm.lpGraph.has_node('(%d,%d)'%(locB[0],locB[1])):
                start,goal = locB, locA
                #mdp_res, rp_res, MRrp_res, sMdp_res, rbrp_res = mrp.RunMDPandReplanners(start, goal, yy, mm, dd, numDays, startT)
                rbrp_res = mrp.RunMDPandReplanners(start,goal,yy,mm,dd,numDays,startT)
                #mdpResultsG.append(mdp_res); rpResultsG.append(rp_res); MRrpResultsG.append(MRrp_res); sMdpResultsG.append(sMdp_res); RbRpResultsG.append(rbrp_res)
                RbRpResultsG.append(rbrp_res)
                #allMdpResults.append(mdp_res); allRpResults.append(rp_res); allMRrpResults.append(MRrp_res); all_sMdpResults.append(sMdp_res); all_RbRpResults.append(rbrp_res)
                all_RbRpResults.append(rbrp_res)
                #tableResult = shelve.open('SA_MDP_MER_Results_%04d%02d%02d.shelve'%(yy,mm,dd))
                tableResult = shelve.open('RBRP_Results_%04d%02d%02d.shelve'%(yy,mm,dd))
                '''
                tableResult['GoodCorr_MDP_%04d%02d%02d'%(yy,mm,dd)] = mdpResultsG
                tableResult['GoodCorr_RP_%04d%02d%02d'%(yy,mm,dd)] = rpResultsG
                tableResult['GoodCorr_MRRP_%04d%02d%02d'%(yy,mm,dd)] = MRrpResultsG
                tableResult['GoodCorr_SMDP_%04d%02d%02d'%(yy,mm,dd)] = sMdpResultsG
                tableResult['All_MDP_%04d%02d%02d'%(yy,mm,dd)] = allMdpResults
                tableResult['All_RP_%04d%02d%02d'%(yy,mm,dd)] = allRpResults
                tableResult['All_MRRP_%04d%02d%02d'%(yy,mm,dd)] = allMRrpResults
                tableResult['All_SMDP_%04d%02d%02d'%(yy,mm,dd)] = all_sMdpResults
                '''
                tableResult['GoodCorr_RBRP_%04d%02d%02d'%(yy,mm,dd)] = RbRpResultsG
                tableResult['All_RBRP_%04d%02d%02d'%(yy,mm,dd)] = all_RbRpResults
                tableResult.close()
            
#mdpResultsB,rpResultsB,MRrpResultsB,sMdpResultsB, RbRpResultsB = [], [], [], [], []
RbRpResultsB = []

for locA in BadCorrLocsS:
    for locB in BadCorrLocsS:
        if locA!=locB  and not mrp.samdp.gm.GetObs(mrp.samdp.gm.lat_pts[locA[1]],mrp.samdp.gm.lon_pts[locA[0]]) \
                and not mrp.samdp.gm.GetObs(mrp.samdp.gm.lat_pts[locB[1]],mrp.samdp.gm.lon_pts[locB[0]]):
            if mrp.samdp.gm.lpGraph.has_node('(%d,%d)'%(locA[0],locA[1])) and mrp.samdp.gm.lpGraph.has_node('(%d,%d)'%(locB[0],locB[1])):
                start,goal = locB, locA
                #mdp_res, rp_res, MRrp_res, sMdp_res, rbrp_res = mrp.RunMDPandReplanners(start, goal, yy, mm, dd, numDays, startT)
                rbrp_res = mrp.RunMDPandReplanners(start, goal, yy, mm, dd, numDays, startT)
                #mdpResultsB.append(mdp_res); rpResultsB.append(rp_res); MRrpResultsB.append(MRrp_res); sMdpResultsB.append(sMdp_res); RbRpResultsB.append(rbrp_res)
                RbRpResultsB.append(rbrp_res);
                #allMdpResults.append(mdp_res); allRpResults.append(rp_res); allMRrpResults.append(MRrp_res); all_sMdpResults.append(sMdp_res); all_RbRpResults.append(rbrp_res)
                all_RbRpResults.append(rbrp_res)
                tableResult = shelve.open('RBRP_Results_%04d%02d%02d.shelve'%(yy,mm,dd))
                '''
                tableResult['BadCorr_MDP_%04d%02d%02d'%(yy,mm,dd)] = mdpResultsB
                tableResult['BadCorr_SMDP_%04d%02d%02d'%(yy,mm,dd)] = sMdpResultsB
                tableResult['BadCorr_MRRP_%04d%02d%02d'%(yy,mm,dd)] = MRrpResultsB
                tableResult['BadCorr_RP_%04d%02d%02d'%(yy,mm,dd)] = rpResultsB
                tableResult['All_MDP_%04d%02d%02d'%(yy,mm,dd)] = allMdpResults
                tableResult['All_RP_%04d%02d%02d'%(yy,mm,dd)] = allRpResults
                tableResult['All_MRRP_%04d%02d%02d'%(yy,mm,dd)] = allMRrpResults
                tableResult['All_SMDP_%04d%02d%02d'%(yy,mm,dd)] = all_sMdpResults
                '''
                tableResult['GoodCorr_RBRP_%04d%02d%02d'%(yy,mm,dd)] = RbRpResultsB
                tableResult['All_RBRP_%04d%02d%02d'%(yy,mm,dd)] = all_RbRpResults
                tableResult.close()
