import UseAgg
import gpplib
from gpplib.SA_Replanner2 import *
from gpplib.SwitchingSA_MDP import *
from gpplib.SwitchingGP_MDP import *
from gpplib.Utils import *
from gpplib.LatLonConversions import *
from gpplib.PseudoWayptGenerator import *
import os, sys
import time, datetime
from gpplib.PlannerResult import *
from gpplib.SwitchingSA_Replanner import *
from gpplib.SwitchingMR_Replanner import *
#from collections import namedtuple


def GetAngularDifferences(ang1,ang2): # Both angles are in degrees.
    #return ((ang1-ang2)%360)
    return ((ang1-ang2+180)%360)-180

def ZeroAllPlannerStats( plannerStats ):
    plannerStats['totCount'] = 0
    plannerStats['totRisk'], plannerStats['avgRisk'], plannerStats['cntRisk'] = 0,0,0
    plannerStats['totTime'], plannerStats['avgTime'], plannerStats['cntTime'] = 0,0,0
    plannerStats['totDist'], plannerStats['avgDist'], plannerStats['cntDist'] = 0,0,0
    plannerStats['totPathLen'], plannerStats['avgPathLen'], plannerStats['cntPLen'] = 0,0,0
    plannerStats['totSuccess'], plannerStats['totCollisions'], plannerStats['totTimeOuts'] = 0,0,0
    
    return plannerStats
    

def UpdateResultWithValue( plannerStats, idx, result ):
    colReason = result['CollisionReason'][idx]
    plannerStats['totCount'] += 1
    if colReason==None:
        plannerStats['totRisk'] += result['Risk'][idx]; plannerStats['cntRisk'] += 1
        plannerStats['totTime'] += result['Time'][idx]; plannerStats['cntTime'] += 1
        plannerStats['totDist'] += result['distFromGoal'][idx]; plannerStats['cntDist'] +=1
        plannerStats['totPathLen'] += result['pathLen'][idx]; plannerStats['cntPLen'] +=1
    elif colReason=='Obstacle':
        plannerStats['totCollisions'] += 1
    if result['Successes'][idx]:
        plannerStats['totSuccess'] +=1

    return plannerStats

def GetAverageFromStats( plannerStats ):
    plannerStats['totTimeOuts'] = plannerStats['totCount'] - plannerStats['totSuccess'] - plannerStats['totCollisions']
    
    if plannerStats['cntRisk']:
        plannerStats['avgRisk'] = plannerStats['totRisk']/plannerStats['cntRisk']
        plannerStats['avgTime'] = plannerStats['totTime']/plannerStats['cntRisk']
        plannerStats['avgDist'] = plannerStats['totDist']/plannerStats['cntRisk']
        plannerStats['avgPathLen'] = plannerStats['totPathLen']/plannerStats['cntRisk']

    return plannerStats


# Use FindAverageCurrentDirection.py to compute the medianCurrentDirn for a date range
def ComputeAverageVsCurrents(PlannerResult,medianCurrentDirn=112.53):
    angularDiff, curType = {}, {}
    With, Perp, Against = {}, {}, {}
    
    With = ZeroAllPlannerStats( With ); Perp = ZeroAllPlannerStats( Perp ); Against = ZeroAllPlannerStats( Against ); 
    
    result = PlannerResult.Result
    for idx,colReason in enumerate(result['CollisionReason']):
        start,goal = result['start'][idx], result['goal'][idx]
        start_goal_pair = '%d,%d,%d,%d'%(start[0],start[1],goal[0],goal[1])
        if angularDiff.has_key(start_goal_pair):
            angDiff = angularDiff[start_goal_pair]
            dirType = curType[start_goal_pair]
        else:
            import math
            start2goal_angle = math.atan2(goal[1]-start[1],goal[0]-start[0])*180/math.pi
            angDiff = GetAngularDifferences(medianCurrentDirn,start2goal_angle)
            #print start_goal_pair, angDiff
            angularDiff[start_goal_pair] = angDiff
            if math.fabs(angDiff)<60:
                dirType='WithCurrent'
            elif math.fabs(angDiff)>=60 and math.fabs(angDiff)<=120:
                dirType='PerpCurrent'
            else:
                dirType='AgainstCurrent'
            curType[start_goal_pair] = dirType
        if dirType == 'WithCurrent':
            With = UpdateResultWithValue(With,idx,result)
        elif dirType == 'PerpCurrent':
            Perp = UpdateResultWithValue(Perp,idx,result)
        elif dirType == 'AgainstCurrent':
            Against = UpdateResultWithValue(Against,idx,result)
    With = GetAverageFromStats( With ); Perp = GetAverageFromStats( Perp ); Against = GetAverageFromStats( Against )
            
    print '(With) TotalCount: %d'%(With['totCount'])
    print '(With) Tot Success=%d, Collisions=%d, Timeouts=%d'%(With['totSuccess'],With['totCollisions'],With['totTimeOuts'])
    print '(With) Avg Risk= %.4f, Avg Time=%.4f, Avg Dist=%.3f, Avg P.Len=%.3f'%(With['avgRisk'],With['avgTime'],With['avgDist'],With['avgPathLen'])
    print '(Perp) TotalCount: %d'%(Perp['totCount'])
    print '(Perp) Tot Success=%d, Collisions=%d, Timeouts=%d'%(Perp['totSuccess'],Perp['totCollisions'],Perp['totTimeOuts'])
    print '(Perp) Avg Risk= %.4f, Avg Time=%.4f, Avg Dist=%.3f, Avg P.Len=%.3f'%(Perp['avgRisk'],Perp['avgTime'],Perp['avgDist'],Perp['avgPathLen'])    
    print '(Against) TotalCount: %d'%(Against['totCount'])
    print '(Against) Tot Success=%d, Collisions=%d, Timeouts=%d'%(Against['totSuccess'],Against['totCollisions'],Against['totTimeOuts'])
    print '(Against) Avg Risk= %.4f, Avg Time=%.4f, Avg Dist=%.3f, Avg P.Len=%.3f'%(Against['avgRisk'],Against['avgTime'],Against['avgDist'],Against['avgPathLen'])    
    return With, Perp, Against 



def ComputeAverages(PlannerResult):
    totRisk, avgRisk, cntRisk = 0,0,0
    totTime, avgTime, cntTime = 0,0,0
    totDist, avgDist, cntDist = 0,0,0
    totPathLen, avgPathLen, cntPLen = 0,0,0
    totSuccess, totCollisions, totTimeOuts  = 0,0,0
    result = PlannerResult.Result
    for idx,colReason in enumerate(result['CollisionReason']):
        if colReason == None:
            totRisk+= result['Risk'][idx]; cntRisk += 1
            totTime+= result['Time'][idx]; cntTime += 1
            totDist+= result['distFromGoal'][idx]; cntDist +=1
            totPathLen+= result['pathLen'][idx]; cntPLen +=1
        elif colReason == 'Obstacle':
            totCollisions +=1
        if result['Successes'][idx]:
            totSuccess +=1
    totTimeOuts = len(result['Successes']) - totCollisions - totSuccess
    
    if cntRisk>1:
        avgRisk = totRisk/float(cntRisk)
        avgTime = totTime/float(cntTime)
        avgDist = totDist/float(cntDist)
        avgPathLen = totPathLen/float(cntPLen)
    print 'Tot Success=%d, Collisions=%d, Timeouts=%d'%(totSuccess,totCollisions,totTimeOuts)
    print 'Avg Risk= %.4f, Avg Time=%.4f, Avg Dist=%.3f, Avg P.Len=%.3f'%(avgRisk,avgTime,avgDist,avgPathLen)    

def SaveToCsv( PlannerResult, csvFileName ):
    with open( csvFileName, "wb") as f:
        writer=csv.writer( f )
        writer.writerows( [ PlannerResult.Result['start'], PlannerResult.Result['goal'],\
        PlannerResult.Result['isSuccess'],PlannerResult.Result['CollisionReason'], PlannerResult.Result['DescStr'],PlannerResult.Result['pathLen'],PlannerResult.Result['Time'],PlannerResult.Result['numHops'],PlannerResult.Result['Risk'] ] )




llconv = LLConvert()
yy,mm,dd,hr,mi = 2013,8,12,0,0
posNoise, curNoise1, posNoise1 = 0.001, 0.01, 0.01
numDays = 0

thetaVal = {'w_r':-1.,'w_g':10.}

rmrrp = SwitchingMR_Replanner(StoreAllPngs = False); rmrrpPr = PlannerResult(PlannerType='Min-Risk Replanner')
rsarp = SwitchingSA_Replanner(StoreAllPngs = False); rsarpPr = PlannerResult(PlannerType='SA_Replanner')
rmdprGp = SwitchingMdpGP(StoreAllPngs=False, theta=thetaVal); rmdprGpPr = PlannerResult(PlannerType='SwitchingGP_MDP')
rmdpr = SwitchingMdp(StoreAllPngs=False, theta=thetaVal); rmdprPr = PlannerResult(PlannerType='SwitchingSA_MDP')
rmdprGp.saMdp.gm.PlotNewRiskMapFig(False)
#rmdpr.LoadTransitionModelsFromShelf(yy, mm, dd, hr, mi, posNoise, curNoise1 )
#start_wLat, start_wLon = 3331.063, -11820.310 # Real Start
start_wLat, start_wLon = 3330.150, -11843.898 # Reversed Start

start_Lat, start_Lon = llconv.WebbToDecimalDeg(start_wLat, start_wLon)
startX,startY = rmdpr.saMdp.gm.GetXYfromLatLon(start_Lat,start_Lon)
#goal_wLat, goal_wLon = 3330.150, -11843.898 # Real Goal
goal_wLat, goal_wLon = 3331.063, -11820.310 # Reversed Goal
goal_Lat, goal_Lon = llconv.WebbToDecimalDeg(goal_wLat, goal_wLon)
goalX,goalY = rmdpr.saMdp.gm.GetXYfromLatLon(goal_Lat,goal_Lon)

simul_end = datetime.datetime(2013,8,20,23,0)

wayPtList = [(33.449855,-118.359328),(33.543039,-118.331636),(33.46926,-118.418188),(33.523829,-118.588117),(33.488213,-118.701459),(33.522344,-118.757254)]
    
for wptGoal in wayPtList:
    for wptStart in wayPtList:
        startX,startY = rmdpr.saMdp.gm.GetXYfromLatLon(wptStart[0],wptStart[1])
        goalX,goalY = rmdpr.saMdp.gm.GetXYfromLatLon(wptGoal[0],wptGoal[1])
        start = (int(startX+0.5),int(startY+0.5))
        goal = (int(goalX+0.5),int(goalY+0.5))
        print 'Start is: (%d,%d)'%(start[0],start[1])
        print 'Goal is: (%d,%d)'%(goal[0],goal[1])
        if startX!=goalX and startY!=goalY:
            yy,mm,dd,hr,mi = 2013,8,12,0,0
            dt = datetime.datetime(yy,mm,dd,hr,mi)
            for i in range(0,30):
                newdt =dt +  datetime.timedelta(hours=i)
                yy,mm,dd,hr,mi = newdt.year,newdt.month, newdt.day, newdt.hour, newdt.minute
            
                #rmdpr.GetIndexedPolicy(yy,mm,dd,hr,mi,goal,theta=thetaVal)
                #rmdpr.saMdp.DisplayPolicy()
                #plt.title('MDP Policy with goal (%d,%d)'%(goal[0],goal[1]))
                #plt.savefig('SAmdp_execution_%s.png'%(str(dt)))
                rtc = RomsTimeConversion()
                s_indx = rtc.GetRomsIndexFromDateTime(yy,mm,dd,newdt)
                
                rmrrp.RunSwitchingMRRPforNhours(yy,mm,dd,hr,mi,start,goal,200,lineType='c.-',simul_end=simul_end,num_hops=250)
                rmrrpPr.UpdateWithResultOfRun(DescStr='MRRP_%04d%02d%02d_%02d%02d'%(yy,mm,dd,hr,mi), \
                            start=start,goal=goal,Risk=rmrrp.totalRisk,Time=rmrrp.totalTime,numHops=rmrrp.totNumHops,
                            pathLen=rmrrp.totPathLength,CollisionReason=rmrrp.CollisionReason,distFromGoal=rmrrp.totalDistFromGoal,
                            isSuccess=rmrrp.isSuccess)
                
                rsarp.RunSwitchingSARPforNhours(yy,mm,dd,hr,mi,start,goal,200,posNoise=posNoise1,curNoise=curNoise1,lineType='y.-',simul_end=simul_end,num_hops=250)
                rsarpPr.UpdateWithResultOfRun(DescStr='SARP_%04d%02d%02d_%02d%02d_%.3f_%.3f'%(yy,mm,dd,hr,mi,posNoise,curNoise1), \
                            start=start,goal=goal,Risk=rsarp.totalRisk,Time=rsarp.totalTime,numHops=rsarp.totNumHops,
                            pathLen=rsarp.totPathLength,CollisionReason=rsarp.CollisionReason,distFromGoal=rsarp.totalDistFromGoal,
                            isSuccess=rsarp.isSuccess)
                
                rmdprGp.RunSwitchingMDPforNhours(yy,mm,dd,hr,mi,start,goal,200,posNoise=posNoise,curNoise=curNoise1,lineType='m.-',simul_end=simul_end,num_hops=250)
                rmdprGpPr.UpdateWithResultOfRun(DescStr='GPMDP_%04d%02d%02d_%02d%02d_%.3f_%.3f'%(yy,mm,dd,hr,mi,posNoise,curNoise1), \
                            start=start,goal=goal,Risk=rmdprGp.totalRisk,Time=rmdprGp.totalTime,numHops=rmdprGp.totNumHops,
                            pathLen=rmdprGp.totPathLength,CollisionReason=rmdprGp.CollisionReason,distFromGoal=rmdprGp.totalDistFromGoal,
                            isSuccess=rmdprGp.isSuccess)
                
                rmdpr.RunSwitchingMDPforNhours(yy,mm,dd,hr,mi,start,goal,200,posNoise=posNoise1,curNoise=curNoise1,lineType='r.-',simul_end=simul_end,num_hops=250)
                rmdprPr.UpdateWithResultOfRun(DescStr='SAMDP_%04d%02d%02d_%02d%02d_%.3f_%.3f'%(yy,mm,dd,hr,mi,posNoise,curNoise1), \
                            start=start,goal=goal,Risk=rmdpr.totalRisk,Time=rmdpr.totalTime,numHops=rmdpr.totNumHops,
                            pathLen=rmdpr.totPathLength,CollisionReason=rmdpr.CollisionReason,distFromGoal=rmdpr.totalDistFromGoal,
                            isSuccess=rmdpr.isSuccess)
                
#totSwGP,avgSwGP = rmdprGpPr.ComputeTotalsAndAverages()
totSwMDP,avgSwMDP = rmdprPr.ComputeTotalsAndAverages()
totSwMR,avgSwMR = rmrrpPr.ComputeTotalsAndAverages()
totSwSARP,avgSwSARP = rsarpPr.ComputeTotalsAndAverages()

# Save results...
plannerResults = shelve.open('GPMDP_FNMDP_SARP_RMRRP_LowHops.shelve')
plannerResults['rmdprPr'] = rmdprPr.Result
plannerResults['rmdprGpPr'] = rmdprGpPr.Result
plannerResults['rsarpPr'] = rsarpPr.Result
plannerResults['rmrrpPr'] = rmrrpPr.Result

FNMDPwith, FNMDPperp, FNMDPagainst = ComputeAverageVsCurrents( rmdprPr ); SaveToCsv( rmdprPr, 'FNMDP_Runs.csv' )
GPMDPwith, GPMDPperp, GPMDPagainst = ComputeAverageVsCurrents( rmdprGpPr ); SaveToCsv( rmdprGpPr, 'GP_MDP_Runs.csv' )
MRRPwith, MRRPperp, MRRPagainst = ComputeAverageVsCurrents( rmrrpPr ); SaveToCsv( rmrrpPr, 'Mrrp_Runs.csv' )
SARPwith, SARPperp, SARPagainst = ComputeAverageVsCurrents(rsarpPr ); SaveToCsv( rsarpPr, 'SARP_Runs.csv')

plannerResults.close()

#plt.figure(); rmdpr.saMdp.gm.PlotNewRiskMapFig(); rmdpr.saMdp.gm.PlotCurrentField(s_indx)
#rmdpr.saMdp.SimulateAndPlotMDP_PolicyExecution(start,goal,s_indx,False,'r-')
        
