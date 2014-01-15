'''
 Report Comparison of MDP and MER trials done by mdp_replanner.py
'''
#from Replanner import *
#from MDP_class import *
#from GenGliderModelUsingRoms import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.Utils import *
import os
import shelve
import numpy as np
         
'''
    Reports comparisons between ensemble runs produced by the mdp_replanner.py
    Also contains certain helper functions which can build an index from the dictionary for efficient access of
    ensemble results indexed by start,goal tuples.

    romsDataDirectory = '/Users/arvind/data/roms/'
'''
class ReportComparison:
    def __init__(self,yy=None,mm=None,dd=None,numDays=None,romsDataDirectory=None):
        self.gm = GliderModel('RiskMap.shelf',romsDataDirectory)
        self.yy,self.mm,self.dd,self.numDays = yy,mm,dd,numDays
        self.mdpResultsG, self.mdpResultsB, self.allMdpResults  = None, None, None
        self.rpResultsG,   self.rpResultsB,  self.allRpResults  = None, None, None
        self.MRpResultsG, self.MRpResultsB, self.allMRpResults  = None, None, None
        self.sMdpResultsG, self.sMdpResultsB, self.allsMdpResults = None, None, None
        self.rbrpResultsG, self.rbrpResultsB, self.allRbrpResults = None, None, None
        
        if yy!=None and mm!=None and dd!=None and numDays!=None:
            print 'Loading data from shelf for %04d-%02d-%02d_%d'%(yy,mm,dd,numDays)
            self.GetResultsFromShelves(yy,mm,dd,numDays)
            print 'Finished loading data...'
        
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
    
    def BuildIndex(self,result):
        myIndex = {}
        nonStarts = {}
        for i in range(len(result)):
            myStart, myGoal = result[i]['start'], result[i]['goal']
            myIndex['(%d,%d),(%d,%d)'%(myStart[0],myStart[1],myGoal[0],myGoal[1])]=i
            
        return myIndex
    
    def GetStatsForRun(self,Result):
        totSuccessRisk, totNonCrashRisk = 0., 0.
        totNonCrashPathLen, totSuccessPathLen = 0., 0.
        numNonCrashes = 0
        totSuccessNumHops, totNonCrashNumHops = 0, 0
        totNonCrashTime, totSuccessTime = 0, 0
        totSuccessDistFromGoal, totNonCrashDistFromGoal = 0., 0.
    
        TotalStats={};  AvgStats={}
        
        numRuns = Result['numRuns']; #Result['numRuns']
        numSuccess = 0; #Result['Successes']
        numRomsNans = 0; #Result['RomsNans']
        numCrashes = 0; #Result['Crashes']
        numNonStarts = 0; #Result['NonStarts']
        numPolNotFound = 0;
        totNumRuns = 0;
        
        for i in range(0,numRuns):
            if Result['isSuccess'][i]==True: # and Result['CollisionReason'][i]==None:
                numSuccess +=1
                totSuccessTime += Result['Time'][i]
                totSuccessNumHops += Result['numHops'][i]
                totSuccessRisk += Result['Risk'][i]
                totSuccessPathLen += Result['pathLength'][i]
                totSuccessDistFromGoal += Result['distFromGoal'][i]
            elif Result['CollisionReason'][i]=='Obstacle':
                numCrashes+=1
            elif Result['CollisionReason'][i]=='RomsNanAtStart':
                numNonStarts+=1
            elif Result['CollisionReason'][i]=='RomsNanLater':
                numRomsNans+=1
            elif Result['CollisionReason'][i]=='PolicyNotFound':
                numPolNotFound+=1
            else:
                totNonCrashRisk += Result['Risk'][i]
                totNonCrashTime += Result['Time'][i]
                totNonCrashDistFromGoal += Result['distFromGoal'][i]
                totNonCrashNumHops += Result['numHops'][i]
                numNonCrashes +=1
            totNumRuns+=1
            
        if numSuccess+numCrashes+numRomsNans+numNonCrashes+numNonStarts != numRuns:
            print 'Did not match: NS=%d, NC=%d, NRN=%d, NRNS=%d, NNC=%d'%(numSuccess,numCrashes,numRomsNans,numNonStarts,numNonCrashes)
        #numNonCrashes = numRuns - (numSuccess+numRomsNans+numNonStarts)
        if numNonCrashes>0:
            AvgStats['avgNonCrashRisk'] = totNonCrashRisk/float(numNonCrashes)
            AvgStats['avgNCrashDistFromGoal'] = totNonCrashDistFromGoal/float(numNonCrashes)
            AvgStats['avgNCrashNumHops'] = totNonCrashNumHops/float(numNonCrashes)
        if numSuccess>0:
            AvgStats['avgSuccessRisk'] = totSuccessRisk/float(numSuccess)
            AvgStats['avgSuccessTime'] = totSuccessTime/float(numSuccess)
            AvgStats['avgSuccessNumHops'] = totSuccessNumHops/float(numSuccess)
        
        CrashStats={}
        CrashStats['Successes'] = numSuccess
        CrashStats['Crashes'] = numCrashes
        CrashStats['RomsNans'] = numRomsNans
        CrashStats['NonStarts'] = numNonStarts
        CrashStats['NumRuns'] = totNumRuns
        CrashStats['numNonCrashes'] = numNonCrashes
        CrashStats['numPolNotFound'] = numPolNotFound
        
        TotalStats['S_Risk']= totSuccessRisk
        TotalStats['S_Time']= totSuccessTime
        TotalStats['S_numHops']= totSuccessNumHops
        TotalStats['S_distFromGoal'] = totSuccessDistFromGoal
        TotalStats['S_pathLen'] = totSuccessPathLen
        TotalStats['Successes'] = numSuccess
        TotalStats['NC_Time']= totNonCrashTime
        TotalStats['NC_Risk']= totNonCrashRisk
        TotalStats['NC_distFromGoal'] = totNonCrashDistFromGoal
        TotalStats['NC_numHops'] = totNonCrashNumHops
        TotalStats['numNonCrashes'] = numNonCrashes
        TotalStats['numPolNotFound'] = numPolNotFound
        
        return TotalStats, AvgStats, CrashStats


    def GetResultsFromShelves(self,yy,mm,dd,numDays):
        tableResult = shelve.open('mdp_mer_results_rrp/SA_MDP_MER_Results_%04d%02d%02d.shelve'%(yy,mm,dd),writeback=False)
        try:
            self.mdpResultsG = tableResult['GoodCorr_MDP_%04d%02d%02d'%(yy,mm,dd)]
            print 'Loaded GoodCorr_MDP_%04d%02d%02d'%(yy,mm,dd)
            self.TotalStats_MDP_G = TotalStatsStore('MDP','Good A.Corr')
        except KeyError:
            pass
        try:
            self.rpResultsG = tableResult['GoodCorr_RP_%04d%02d%02d'%(yy,mm,dd)]
            print 'Loaded GoodCorr_RP_%04d%02d%02d'%(yy,mm,dd)
            self.TotalStats_RP_G = TotalStatsStore('RP','Good A.Corr')
        except KeyError:
            pass
        try:
            self.MRpResultsG = tableResult['GoodCorr_MRRP_%04d%02d%02d'%(yy,mm,dd)]
            print 'Loaded GoodCorr_MRRP_%04d%02d%02d'%(yy,mm,dd)
            self.TotalStats_MRP_G = TotalStatsStore('MRRP','Good A.Corr')
        except KeyError:
            pass
        try:
            self.sMdpResultsG = tableResult['GoodCorr_SMDP_%04d%02d%02d'%(yy,mm,dd)]
            print 'Loaded GoodCorr_SMDP_%04d%02d%02d'%(yy,mm,dd)
            self.TotalStats_SMDP_G = TotalStatsStore('SMDP','Good A.Corr')
        except KeyError:
            pass
        try:
            self.allMdpResults = tableResult['All_MDP_%04d%02d%02d'%(yy,mm,dd)]
            print 'Loaded All_MDP_%04d%02d%02d'%(yy,mm,dd)
            self.TotalStats_MDP_All = TotalStatsStore('MDP','All A.Corr')
            print 'Creating index for All_MDP_%04d%02d%02d'%(yy,mm,dd)
            self.mdpIndx = self.BuildIndex(self.allMdpResults)
        except KeyError:
            pass
        try:
            self.allMRpResults = tableResult['All_MRRP_%04d%02d%02d'%(yy,mm,dd)]
            print 'Loaded All_MRRP_%04d%02d%02d'%(yy,mm,dd)
            self.TotalStats_MRP_All = TotalStatsStore('MRRP','All A.Corr')
            print 'Creating index for All_MRRP_%04d%02d%02d'%(yy,mm,dd)
            self.mrpIndx = self.BuildIndex(self.allMRpResults)
        except KeyError:
            pass
        try:
            self.allRpResults = tableResult['All_RP_%04d%02d%02d'%(yy,mm,dd)]
            print 'Loaded All_RP_%04d%02d%02d'%(yy,mm,dd)
            self.TotalStats_RP_All = TotalStatsStore('RP','All A.Corr')
            print 'Creating index for All_RP_%04d%02d%02d'%(yy,mm,dd)
            self.rpIndx = self.BuildIndex(self.allRpResults)
        except KeyError:
            pass
        try:
            self.allsMdpResults = tableResult['All_SMDP_%04d%02d%02d'%(yy,mm,dd)]
            print 'Loaded All_SMDP_%04d%02d%02d'%(yy,mm,dd)
            self.TotalStats_SMDP_All = TotalStatsStore('SMDP','All A.Corr')
            print 'Creating index for All_SMDP_%04d%02d%02d'%(yy,mm,dd)
            self.smdpIndx = self.BuildIndex(self.allsMdpResults)
        except KeyError:
            pass
        try:
            self.mdpResultsB = tableResult['BadCorr_MDP_%04d%02d%02d'%(yy,mm,dd)]
            print 'Loaded BadCorr_MDP_%04d%02d%02d'%(yy,mm,dd)
            self.TotalStats_MDP_B = TotalStatsStore('MDP','Bad A.Corr')
        except KeyError:
            pass
        try:
            self.rpResultsB = tableResult['BadCorr_RP_%04d%02d%02d'%(yy,mm,dd)]
            print 'Loaded BadCorr_RP_%04d%02d%02d'%(yy,mm,dd)
            self.TotalStats_RP_B = TotalStatsStore('RP','Bad A.Corr')
        except KeyError:
            pass
        try:
            self.MRpResultsB = tableResult['BadCorr_MRRP_%04d%02d%02d'%(yy,mm,dd)]
            print 'Loaded BadCorr_MRP_%04d%02d%02d'%(yy,mm,dd)
            self.TotalStats_MRP_B = TotalStatsStore('MRRP','Bad A.Corr')
        except KeyError:
            pass
        try:
            self.sMdpResultsB = tableResult['BadCorr_SMDP_%04d%02d%02d'%(yy,mm,dd)]
            print 'Loaded BadCorr_SMDP_%04d%02d%02d'%(yy,mm,dd)
            self.TotalStats_SMDP_B = TotalStatsStore('SMDP','Bad A.Corr')
        except KeyError:
            pass
        # FIXME: I'm being lazy again... Should rewrite this tester so that it is a standalone class.
        try:
            self.allRbrpResults = tableResult['All_RBRP_%04d%02d%02d'%(yy,mm,dd)]
            print 'Loaded All_RBRP_%04d%02d%02d'%(yy,mm,dd)
            self.TotalStats_RBRP_All = TotalStatsStore('RBRP','All A.Corr')
            self.TotalStats_RBRP_B = TotalStatsStore('RBRP','Bad A.Corr')
            self.TotalStats_RBRP_G = TotalStatsStore('RBRP','Good A.Corr')
        except KeyError:
            pass
         
        
        tableResult.close()
        
    def GetStatsForNodesAccordingToCorrelation(self,Thresh=0.5,TimeScale=48):
        GoodCorrLocsU,BadCorrLocsU,GoodCorrLocsV,BadCorrLocsV,GoodCorrLocsS,BadCorrLocsS = \
            self.GetGoodBadCorrLocs(Thresh, TimeScale)
        # First, go through all the poorly correlated nodes...
        
        for locA in BadCorrLocsS:
            for locB in BadCorrLocsS:
                if locA!=locB and not self.gm.GetObs(self.gm.lat_pts[locA[1]],self.gm.lon_pts[locA[0]])\
                    and not self.gm.GetObs(self.gm.lat_pts[locB[1]],self.gm.lon_pts[locB[0]]):
                        indx = 0
                        start,goal = locB, locA
                        if self.allMdpResults!=None:
                            if self.mdpIndx.has_key('(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])):
                                indx = self.mdpIndx['(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])]
                                TotalStats, AvgStats, CrashStats = self.GetStatsForRun(self.allMdpResults[indx])
                                self.TotalStats_MDP_B.AccumulateStats(TotalStats, AvgStats, CrashStats)
                        if self.allMRpResults!=None:
                            if self.mrpIndx.has_key('(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])):
                                indx = self.mrpIndx['(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])]
                                TotalStats, AvgStats, CrashStats = self.GetStatsForRun(self.allMRpResults[indx])
                                self.TotalStats_MRP_B.AccumulateStats(TotalStats, AvgStats, CrashStats)
                        if self.allRpResults!=None:
                            if self.rpIndx.has_key('(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])):
                                indx = self.rpIndx['(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])]
                                TotalStats, AvgStats, CrashStats = self.GetStatsForRun(self.allRpResults[indx])
                                self.TotalStats_RP_B.AccumulateStats(TotalStats, AvgStats, CrashStats)
                        if self.allsMdpResults!=None:
                            if self.smdpIndx.has_key('(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])):
                                indx = self.smdpIndx['(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])]
                                TotalStats, AvgStats, CrashStats = self.GetStatsForRun(self.allsMdpResults[indx])
                                self.TotalStats_SMDP_B.AccumulateStats(TotalStats, AvgStats, CrashStats)
                        if self.allRbrpResults!=None:
                            if self.smdpIndx.has_key('(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])):
                                indx = self.smdpIndx['(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])]
                                TotalStats, AvgStats, CrashStats = self.GetStatsForRun(self.allRbrpResults[indx])
                                self.TotalStats_RBRP_B.AccumulateStats(TotalStats, AvgStats, CrashStats)
        
        # Next, go through all the well correlated nodes...
        for locA in GoodCorrLocsS:
            for locB in GoodCorrLocsS:
                if locA!=locB and not self.gm.GetObs(self.gm.lat_pts[locA[1]],self.gm.lon_pts[locA[0]])\
                    and not self.gm.GetObs(self.gm.lat_pts[locB[1]],self.gm.lon_pts[locB[0]]):
                        indx = 0
                        start,goal = locB, locA
                        if self.allMdpResults!=None:
                            if self.mdpIndx.has_key('(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])):
                                indx = self.mdpIndx['(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])]
                                TotalStats, AvgStats, CrashStats = self.GetStatsForRun(self.allMdpResults[indx])
                                self.TotalStats_MDP_G.AccumulateStats(TotalStats, AvgStats, CrashStats)
                        if self.allMRpResults!=None:
                            if self.mrpIndx.has_key('(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])):
                                indx = self.mrpIndx['(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])]
                                TotalStats, AvgStats, CrashStats = self.GetStatsForRun(self.allMRpResults[indx])
                                self.TotalStats_MRP_G.AccumulateStats(TotalStats, AvgStats, CrashStats)
                        if self.allRpResults!=None:
                            if self.rpIndx.has_key('(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])):
                                indx = self.rpIndx['(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])]
                                TotalStats, AvgStats, CrashStats = self.GetStatsForRun(self.allRpResults[indx])
                                self.TotalStats_RP_G.AccumulateStats(TotalStats, AvgStats, CrashStats)
                        if self.allsMdpResults!=None:
                            if self.smdpIndx.has_key('(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])):
                                indx = self.smdpIndx['(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])]
                                TotalStats, AvgStats, CrashStats = self.GetStatsForRun(self.allsMdpResults[indx])
                                self.TotalStats_SMDP_G.AccumulateStats(TotalStats, AvgStats, CrashStats)
                        if self.allRbrpResults!=None:
                            if self.smdpIndx.has_key('(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])):
                                indx = self.smdpIndx['(%d,%d),(%d,%d)'%(start[0],start[1],goal[0],goal[1])]
                                TotalStats, AvgStats, CrashStats = self.GetStatsForRun(self.allRbrpResults[indx])
                                self.TotalStats_RBRP_G.AccumulateStats(TotalStats, AvgStats, CrashStats)

'''
    A class that handles data accumulation.
    It is initialized with the name of the planner whose stats are to be accumulated.
    There is also a field which indicates whether the type of nodes being auto-correlated are
    good or bad.
'''
class TotalStatsStore:
    def __init__(self,plannerName,corrType=' Unknown A.Corr '):
        self.totSuccessRisk, self.totSuccessTime, self.totSuccessDistFromGoal = 0., 0., 0.
        self.totSuccessPathLen, self.totNumSuccess, self.totSuccessNumHops = 0., 0., 0.
        self.totAvgSuccessRisk, self.totAvgSuccessTime, self.totAvgSuccessNumHops = 0., 0., 0.
        self.totAvgNCRisk, self.totAvgNCdistFromGoal, self.totAvgNCnumHops = 0., 0., 0.
        self.totAvgNCRisk, self.totAvgNCdistFromGoal, self.totAvgNCnumHops = 0., 0., 0.
        self.totNC_Risk, self.totNC_Time, self.totNC_DistFromGoal, self.totNCnumHops = 0., 0., 0., 0
        self.totNumPolNotFound, self.totNumNC, self.totNumRomsNans = 0,0,0
        self.totNumCrashes, self.totNumNonStarts = 0, 0
        self.totAvgSuccessNum,self.totNumRuns, self.totAvgNCnum = 0,0,0
        self.totNodesCompared = 0
        self.pName = plannerName
        self.corrType = corrType

    def AccumulateStats(self, TotalStats, AvgStats, CrashStats):
        self.totNodesCompared +=1
        # Compute the accumulated 
        self.totNumNC               += TotalStats['numNonCrashes']; 
        self.totSuccessRisk         += TotalStats['S_Risk']; 
        self.totSuccessTime         += TotalStats['S_Time'];
        self.totNC_Risk             += TotalStats['NC_Risk']; 
        self.totNC_Time             += TotalStats['NC_Time'];
        self.totSuccessDistFromGoal += TotalStats['S_distFromGoal']; 
        self.totSuccessPathLen      += TotalStats['S_pathLen'];
        self.totSuccessNumHops      += TotalStats['S_numHops'];
        self.totNumPolNotFound      += TotalStats['numPolNotFound'];
        self.totNC_DistFromGoal     += TotalStats['NC_distFromGoal']; 
        self.totNCnumHops           += TotalStats['NC_numHops'];
        
        self.totNumRomsNans         += CrashStats['RomsNans']; 
        self.totNumCrashes          += CrashStats['Crashes'];
        self.totNumNonStarts        += CrashStats['NonStarts'];
        self.totNumRuns             += CrashStats['NumRuns']; 
        self.totNumSuccess          += CrashStats['Successes'];
        
        # Compute the accumulated average statistics, if any...
        if len(AvgStats)>0:
            if AvgStats.has_key('avgSuccessRisk'):
                self.totAvgSuccessRisk   += AvgStats['avgSuccessRisk']; 
                self.totAvgSuccessTime   += AvgStats['avgSuccessTime'];
                self.totAvgSuccessNumHops+= AvgStats['avgSuccessNumHops'];
                self.totAvgSuccessNum +=1
            if AvgStats.has_key('avgNonCrashRisk'):
                self.totAvgNCRisk       += AvgStats['avgNonCrashRisk'];
                self.totAvgNCdistFromGoal+=AvgStats['avgNCrashDistFromGoal'];
                self.totAvgNCnumHops    += AvgStats['avgNCrashNumHops'];
                self.totAvgNCnum += 1
                
    def PrintAccumulatedResults(self,yy,mm,dd):
        print self.totNumRuns,self.totNumNonStarts,self.totNumRomsNans,self.totNumPolNotFound
        print 'Stats from the Run from %04d-%02d-%02d are:'%(yy,mm,dd)
        print 'Number of Successes for %s for %s nodes: %.0f, (%.1f)'%(self.pName,self.corrType,self.totNumSuccess,(self.totNumSuccess*100.)/(self.totNumRuns-self.totNumNonStarts-self.totNumRomsNans-self.totNumPolNotFound))
        print 'Number of Crashes for %s for %s nodes: %.0f, (%.1f)'%(self.pName,self.corrType,self.totNumCrashes,(self.totNumCrashes*100.)/(self.totNumRuns-self.totNumNonStarts-self.totNumRomsNans-self.totNumPolNotFound))
        print 'Number of Non-Crashes for %s (without Success) for %s: %.0f, (%.1f)'%(self.pName,self.corrType,self.totNumNC,(self.totNumNC*100.)/(self.totNumRuns-self.totNumNonStarts-self.totNumRomsNans-self.totNumPolNotFound))
        print 'Number of RomsNANs for %s for %s nodes: %.0f'%(self.pName,self.corrType,self.totNumRomsNans+self.totNumNonStarts)
        print 'Number of NoPolicies for %s for %s nodes: %.0f'%(self.pName,self.corrType,self.totNumPolNotFound)
        print 'Average Risk for %s successful paths between %s nodes: %.3f'%(self.pName,self.corrType,self.totSuccessRisk/self.totNumSuccess)
        print 'Average P.Length for %s successful paths between %s nodes: %.3f'%(self.pName,self.corrType,self.totSuccessPathLen/self.totNumSuccess)
        print 'TotRuns for %s between %s nodes = %d '%(self.pName,self.corrType,self.totNumRuns)
        print
        
        
'''
    Example Usage:
'''
def main():
    yy,mm,dd,numDays = 2011,2,1,2        
    rc = ReportComparison(yy,mm,dd,numDays)
    rc.GetStatsForNodesAccordingToCorrelation(0.5, 48)
    if rc.mdpResultsG:
        rc.TotalStats_MDP_G.PrintAccumulatedResults(yy,mm,dd)
    if rc.rpResultsG:
        rc.TotalStats_RP_G.PrintAccumulatedResults(yy,mm,dd)
    if rc.MRpResultsG!=None:
        rc.TotalStats_MRP_G.PrintAccumulatedResults(yy,mm,dd)
    if rc.sMdpResultsG!=None:
        rc.TotalStats_SMDP_G.PrintAccumulatedResults(yy,mm,dd)
    if rc.allRbrpResults:
        rc.TotalStats_RBRP_G.PrintAccumulatedResults(yy,mm,dd)
        rc.TotalStats_RBRP_B.PrintAccumulatedResults(yy,mm,dd)
    if rc.mdpResultsB:
        rc.TotalStats_MDP_B.PrintAccumulatedResults(yy,mm,dd)
    if rc.rpResultsB:
        rc.TotalStats_RP_B.PrintAccumulatedResults(yy,mm,dd)
    if rc.sMdpResultsB!=None:
        rc.TotalStats_SMDP_B.PrintAccumulatedResults(yy,mm,dd)
    if rc.MRpResultsB!=None:
        rc.TotalStats_MRP_B.PrintAccumulatedResults(yy,mm,dd)
    

if __name__ == '__main__':
    main()
