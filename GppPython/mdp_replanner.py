'''
    Official class which will perform the actual MDP and replanner comparison.
'''
import UseAgg
import os
import gpplib
import sys
from gpplib.Replanner import *
from gpplib.MDP_class import *

class mdpReplanner:
    ''' MDP Replanner test class.
    '''
    def __init__(self,riskMapShelf='RiskMap.shelf',romsDataDirectory='/Users/arvind/data/roms/'):
        self.pngDir = 'pngs_mr_mer_mdp'
        self.lastGoal = (-1,-1)
        self.numRuns = 10
        try:
            os.mkdir(self.pngDir)
        except OSError as (errno,strerror):
            pass
        conf = gpplib.Utils.GppConfig()
        self.rp = Replanner(riskMapShelf,romsDataDirectory)
        self.mdp = MDP(riskMapShelf,romsDataDirectory)
        self.MRrp = Replanner(riskMapShelf,romsDataDirectory)
        
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
        MdpResult, RpResult, MRpResult = {}, {}, {}
        if goal!= self.lastGoal:
            self.mdp.SetGoalAndInitTerminalStates(goal)
            print 'Doing Value Iteration'
            self.mdp.doValueIteration(0)
            Xpolicy,Ypolicy = self.mdp.DisplayPolicy()
            plt.title('MDP Policy with goal (%d,%d)'%(goal[0],goal[1]))
            plt.savefig('%s/MDP_Policy_Goal_%04d%02d%02d_%d_%d.pdf'%(self.pngDir,yy,mm,dd,goal[0],goal[1]))
            plt.close()
            
            self.sp_mst, self.dist = self.rp.GetShortestPathMST(goal)
            self.sp_mstMR, self.distMR = self.MRrp.GetShortestPathMST(goal)
            
            self.rp.PlotMRpaths(goal); 
            plt.title('Replanner Min-Exp-Risk MST with goal (%d,%d)'%(goal[0],goal[1]))
            plt.savefig('%s/Replanner_MER_MST_%04d%02d%02d_%d_%d.png'%(self.pngDir,yy,mm,dd,goal[0],goal[1]))
            plt.close()
            
            self.MRrp.PlotMRpaths(goal)
            plt.title('Replanner Min-Risk MST with goal (%d,%d)'%(goal[0],goal[1]))
            plt.savefig('%s/Replanner_MR_MST_%04d%02d%02d_%d_%d.png'%(self.pngDir,yy,mm,dd,goal[0],goal[1]))
            plt.close()
            
            self.lastGoal = goal
            
        plt.figure()
        self.mdp.gm.PlotNewRiskMapFig(startT)
        MdpResult['Risk'], MdpResult['pathLength'], MdpResult['Time'] = [], [], []
        MdpResult['numHops'], MdpResult['distFromGoal'], MdpResult['CollisionReason'] = [], [], []
        MdpResult['isSuccess']= []; MdpResult['startTime'] = []
        MdpResult['finalLoc'] = []
        
        RpResult['Risk'], RpResult['pathLength'], RpResult['Time'] = [], [], []
        RpResult['numHops'], RpResult['distFromGoal'], RpResult['CollisionReason'] = [], [], []
        RpResult['isSuccess']= []; RpResult['startTime'] = []
        RpResult['finalLoc'] = []
        
        MRpResult['Risk'], MRpResult['pathLength'], MRpResult['Time'] = [], [], []
        MRpResult['numHops'], MRpResult['distFromGoal'], MRpResult['CollisionReason'] = [], [], []
        MRpResult['isSuccess']= []; MRpResult['startTime'] = []
        MRpResult['finalLoc'] = []
        
        totRiskMDP, totHopsMDP, totSuccessMDP, totCrashesMDP, totFalseStartsMDP, totTimeMDP, totDistMDP = 0.,0.,0.,0.,0.,0.,0.
        totRiskRP, totHopsRP, totSuccessRP, totCrashesRP, totFalseStartsRP, totTimeRP, totDistRP = 0.,0.,0.,0.,0.,0.,0.
        totRiskMRP, totHopsMRP, totSuccessMRP, totCrashesMRP, totFalseStartsMRP, totTimeMRP, totDistMRP = 0.,0.,0.,0.,0.,0.,0.
        totNonStartsMDP, totNonStartsRP, totNanMDP, totNanRP, totNonStartsMRP, totNanMRP  = 0,0, 0, 0, 0, 0
        totNoPolicyMDP, totNoPolicyRP, totNoPolicyMRP = 0, 0, 0
        for i in range(0,self.numRuns):
            tempRiskMDP, landedMDP = self.mdp.SimulateAndPlotMDP_PolicyExecution(start,goal,startT+i,newFig=False)
            MdpResult['Risk'].append(self.mdp.totalRisk); MdpResult['pathLength'].append(self.mdp.totalPathLength/1000.)
            MdpResult['Time'].append(self.mdp.totalTime/3600.); MdpResult['numHops'].append(self.mdp.numHops)
            MdpResult['CollisionReason'].append(self.mdp.CollisionReason); MdpResult['isSuccess'].append(self.mdp.isSuccess)
            MdpResult['distFromGoal'].append(self.mdp.distFromGoal); MdpResult['startTime'].append(startT+i)
            MdpResult['finalLoc'].append((self.mdp.finX,self.mdp.finY))
            totRiskMDP+=self.mdp.totalRisk; totHopsMDP+=self.mdp.numHops; totTimeMDP+=self.mdp.totalTime/3600.; totDistMDP+=self.mdp.totalPathLength/1000.
            if self.mdp.isSuccess==True:
                totSuccessMDP+=1
            
            if self.mdp.CollisionReason!=None:
                if self.mdp.CollisionReason=='Obstacle':
                    totCrashesMDP+=1
                else:
                    if self.mdp.CollisionReason=='RomsNansAtStart':
                        totNonStartsMDP+=1
                    else:
                        if self.mdp.CollisionReason == 'RomsNanLater':
                            totNanMDP +=1
                        elif self.mdp.CollisionReason == 'DidNotFindPolicy':
                            totNoPolicyMDP +=1
            
            tempRiskMER,landedMER= self.rp.SimulateAndPlotMR_PolicyExecution(start,goal,self.sp_mst,startT+i,False)
            RpResult['Risk'].append(self.rp.totalRisk); RpResult['pathLength'].append(self.rp.totalPathLength/1000.)
            RpResult['Time'].append(self.rp.totalTime/3600.); RpResult['numHops'].append(self.rp.numHops)
            RpResult['CollisionReason'].append(self.rp.CollisionReason); RpResult['isSuccess'].append(self.rp.isSuccess)
            RpResult['distFromGoal'].append(self.rp.distFromGoal); RpResult['startTime'].append(startT+i)
            RpResult['finalLoc'].append((self.rp.finX,self.rp.finY))
            totRiskRP+=self.rp.totalRisk; totHopsRP+=self.rp.numHops; totTimeRP+=self.rp.totalTime/3600.; totDistRP+=self.rp.totalPathLength/1000.
            if self.rp.isSuccess==True:
                totSuccessRP+=1
            
            if self.rp.CollisionReason!=None:
                if self.rp.CollisionReason=='Obstacle':
                    totCrashesRP+=1
                else:
                    if self.rp.CollisionReason=='RomsNanAtStart':
                        totNonStartsRP+=1
                    else:
                        if self.rp.CollisionReason == 'RomsNanLater':
                            totNanRP +=1
                        elif self.rp.CollisionReason == 'DidNotFindPolicy':
                            totNoPolicyRP +=1
                            
            tempRiskMRP, landedMRP = self.MRrp.SimulateAndPlotMR_PolicyExecution(start,goal,self.sp_mstMR,startT+i,False,'g-')
            MRpResult['Risk'].append(self.MRrp.totalRisk); MRpResult['pathLength'].append(self.MRrp.totalPathLength/1000.)
            MRpResult['Time'].append(self.MRrp.totalTime/3600.); MRpResult['numHops'].append(self.MRrp.numHops)
            MRpResult['CollisionReason'].append(self.MRrp.CollisionReason); MRpResult['isSuccess'].append(self.MRrp.isSuccess)
            MRpResult['distFromGoal'].append(self.MRrp.distFromGoal); MRpResult['startTime'].append(startT+i)
            MRpResult['finalLoc'].append((self.MRrp.finX,self.MRrp.finY))
            totRiskMRP+=self.MRrp.totalRisk; totHopsMRP+=self.MRrp.numHops; totTimeMRP+=self.MRrp.totalTime/3600.; totDistMRP+=self.MRrp.totalPathLength/1000.
            if self.MRrp.isSuccess==True:
                    totSuccessMRP+=1
                
            if self.MRrp.CollisionReason!=None:
                    if self.MRrp.CollisionReason=='Obstacle':
                        totCrashesMRP+=1
                    else:
                        if self.MRrp.CollisionReason=='RomsNansAtStart':
                            totNonStartsMRP+=1
                        else:
                            if self.MRrp.CollisionReason == 'RomsNanLater':
                                totNanMRP +=1
                            elif self.MRrp.CollisionReason == 'DidNotFindPolicy':
                            	totNoPolicyMRP +=1
        
        # Now that we have everything, store the totals and compute averages.
        MdpResult['TotalRisk'] = totRiskMDP; MdpResult['Crashes'] = totCrashesMDP; MdpResult['NonStarts'] = totNonStartsMDP;
        MdpResult['RomsNans'] = totNanMDP 
        MdpResult['numRuns'] = self.numRuns;  MdpResult['Successes'] = totSuccessMDP;
        MdpResult['U'] = self.mdp.mdp['U']
        MdpResult['start'] = start; MdpResult['goal'] = goal;
        
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
        #
        self.mdp.gm.PlotCurrentField(startT);
        plt.title('Ensembles simulated on %04d-%02d-%02d: (%d,%d) to (%d,%d)'%(yy,mm,dd,start[0],start[1],goal[0],goal[1]))
        plt.text(3,10,'Risks: MDP=%.2f, RP=%.2f, MR=%.2f'%(totRiskMDP,totRiskRP,totRiskMRP))
        plt.text(3,9.5,'Avg. Hops: MDP=%.2f, RP=%.2f, MR=%.2f'%(totHopsMDP/float(self.numRuns),totHopsRP/float(self.numRuns),totHopsMRP/float(self.numRuns)))
        plt.text(3,9,'Avg.Path-Len: MDP=%.2f, RP=%.2f, MR=%.2f'%(totDistMDP/float(self.numRuns),\
                                                    totDistRP/float(self.numRuns), totDistMRP/float(self.numRuns)))
        plt.text(3,8.5,'Successes: MDP=%d, RP=%d, MR=%d'%(totSuccessMDP,totSuccessRP,totSuccessMRP))
        plt.text(3,8,'Non-Starts: MDP=%d, RP=%d, MR=%d'%(totNonStartsMDP,totNonStartsRP,totNonStartsMRP))
        plt.text(3,7.5,'Crashes: MDP=%d, RP=%d, MR=%d'%(totCrashesMDP,totCrashesRP,totCrashesMRP))
        plt.savefig('%s/Ensembles_%04d%02d%02d_%d_%d_%d_%d.png'%(self.pngDir,yy,mm,dd,start[0],start[1],goal[0],goal[1]))
        plt.close()
        
        return MdpResult, RpResult, MRpResult
    
conf = gpplib.Utils.GppConfig()
mrp = mdpReplanner(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir )
GoodCorrLocsU,BadCorrLocsU,GoodCorrLocsV,BadCorrLocsV,GoodCorrLocsS,BadCorrLocsS = mrp.GetGoodBadCorrLocs()
yy,mm,dd,numDays = 2011,3,1,2
posNoise, romsNoise = 0.1, 0.01

mrp.mdp.GetTransitionModelFromShelf(yy,mm,dd,numDays,posNoise,romsNoise,conf.myDataDir+'NoisyGliderModels2')
mrp.rp.GetTransitionModelFromShelf(yy,mm,dd,numDays,posNoise,romsNoise,conf.myDataDir+'NoisyGliderModels2')
mrp.rp.CreateExpRiskGraph()
mrp.MRrp.GetTransitionModelFromShelf(yy,mm,dd,numDays,posNoise,romsNoise,conf.myDataDir+'NoisyGliderModels2')
mrp.MRrp.CreateMinRiskGraph()

u,v,time1,depth,lat,lon = mrp.rp.GetRomsData(yy,mm,dd,numDays)
u,v,time1,depth,lat,lon = mrp.MRrp.GetRomsData(yy,mm,dd,numDays)
u,v,time1,depth,lat,lon = mrp.mdp.GetRomsData(yy,mm,dd,numDays)
startT = 0
plt.figure(); mrp.mdp.gm.PlotNewRiskMapFig(); mrp.mdp.gm.PlotCurrentField(startT); 
plt.title('Currents at %d hrs on %04d-%02d-%02d'%(startT,yy,mm,dd)); plt.savefig('%s/Currents_%04d%02d%02d_%dhrs.png'%(mrp.pngDir,yy,mm,dd,startT))
plt.close()

mdpResultsG,rpResultsG,MRrpResultsG = [], [], []
allMdpResults,allRpResults,allMRrpResults = [], [], []
for locA in GoodCorrLocsS:
    for locB in GoodCorrLocsS:
        if locA!=locB  and not mrp.mdp.gm.GetObs(mrp.mdp.gm.lat_pts[locA[1]],mrp.mdp.gm.lon_pts[locA[0]]) \
                and not mrp.mdp.gm.GetObs(mrp.mdp.gm.lat_pts[locB[1]],mrp.mdp.gm.lon_pts[locB[0]]):
            start,goal = locB, locA
            mdp_res, rp_res, MRrp_res = mrp.RunMDPandReplanners(start, goal, yy, mm, dd, numDays, startT)
            mdpResultsG.append(mdp_res); rpResultsG.append(rp_res); MRrpResultsG.append(MRrp_res)
            allMdpResults.append(mdp_res); allRpResults.append(rp_res); allMRrpResults.append(MRrp_res)
            tableResult = shelve.open('MDP_MER_Results_%04d%02d%02d.shelve'%(yy,mm,dd))
            tableResult['GoodCorr_MDP_%04d%02d%02d'%(yy,mm,dd)] = mdpResultsG
            tableResult['GoodCorr_RP_%04d%02d%02d'%(yy,mm,dd)] = rpResultsG
            tableResult['GoodCorr_MRRP_%04d%02d%02d'%(yy,mm,dd)] = MRrpResultsG
            tableResult['All_MDP_%04d%02d%02d'%(yy,mm,dd)] = allMdpResults
            tableResult['All_RP_%04d%02d%02d'%(yy,mm,dd)] = allRpResults
            tableResult['All_MRRP_%04d%02d%02d'%(yy,mm,dd)] = allMRrpResults
            tableResult.close()
            
mdpResultsB,rpResultsB,MRrpResultsB = [], [], []
for locA in BadCorrLocsS:
    for locB in BadCorrLocsS:
        if locA!=locB  and not mrp.mdp.gm.GetObs(mrp.mdp.gm.lat_pts[locA[1]],mrp.mdp.gm.lon_pts[locA[0]]) \
                and not mrp.mdp.gm.GetObs(mrp.mdp.gm.lat_pts[locB[1]],mrp.mdp.gm.lon_pts[locB[0]]):
            start,goal = locB, locA
            mdp_res, rp_res, MRrp_res = mrp.RunMDPandReplanners(start, goal, yy, mm, dd, numDays, startT)
            mdpResultsB.append(mdp_res); rpResultsB.append(rp_res); MRrpResultsB.append(MRrp_res)
            allMdpResults.append(mdp_res); allRpResults.append(rp_res); allMRrpResults.append(MRrp_res)
            tableResult = shelve.open('MDP_MER_Results_%04d%02d%02d.shelve'%(yy,mm,dd))
            tableResult['BadCorr_MDP_%04d%02d%02d'%(yy,mm,dd)] = mdpResultsB
            tableResult['BadCorr_MRRP_%04d%02d%02d'%(yy,mm,dd)] = MRrpResultsB
            tableResult['BadCorr_RP_%04d%02d%02d'%(yy,mm,dd)] = rpResultsB
            tableResult['All_MDP_%04d%02d%02d'%(yy,mm,dd)] = allMdpResults
            tableResult['All_RP_%04d%02d%02d'%(yy,mm,dd)] = allRpResults
            tableResult['All_MRRP_%04d%02d%02d'%(yy,mm,dd)] = allMRrpResults
            tableResult.close()
            
            
            
            
