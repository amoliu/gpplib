import UseAgg
import gpplib
from gpplib.MDP_class import *
from gpplib.Replanner import *
from gpplib.SA_Replanner import *
from gpplib.StateActionMDP import *
from gpplib.Utils import *

s_yy,s_mm,s_dd,numDays = 2011,1,1,2
e_yy,e_mm,e_dd = 2011,6,30

pngDir = 'pngs_policies'
try:
    os.mkdir(pngDir)
except OSError as (errno,strerror):
    pass

conf = GppConfig()
dr = DateRange(s_yy,s_mm,s_dd,e_yy,e_mm,e_dd)
mdp = MDP(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir)
rp = Replanner(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir)
samdp = SA_MDP(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir)
sarp = SA_Replanner(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir)

#mdp.GetTransitionModelFromShelf(yy,mm,dd,numDays,None,None,'gliderModels')
u,v,time1,depth,lat,lon = mdp.GetRomsData(s_yy,s_mm,s_dd,numDays)

curNoiseVar = [0.01, 0.025, 0.05, 0.1, 0.15, 0.2, 0.32, 0.5]
tourLocs = [(1,6),(5,1),(8,1)]
posNoise = 0.1

'''
Compute MDP policy for that day with given amount of noise in simulation.
'''
for (yy,mm,dd) in dr.DateList:
    for j in range(0,len(curNoiseVar)):
        for goal in tourLocs:
            policyTable = shelve.open('PolicyTable_%04d%02d%02d_%d.shelve'%(yy,mm,dd,numDays))
            mdp.GetTransitionModelFromShelf(yy,mm,dd,numDays,posNoise,curNoiseVar[j],conf.myDataDir+'NoisyGliderModels2')
            mdp.SetGoalAndInitTerminalStates(goal)
            keyForGoalAndNoise = 'Pol_G_%d_%d_PN_%.3f_RN_%.3f'%(goal[0],goal[1],posNoise,curNoiseVar[j])
            mdp_key = 'MDP_%s'%(keyForGoalAndNoise); 
            if policyTable.has_key(mdp_key):
                print 'Found this policy!'
                if policyTable[mdp_key].has_key('U'):
                    mdp.mdp['U'] = policyTable[mdp_key]['U']
                if policyTable[mdp_key].has_key('polTree'):
                    mdp.pol_tree = policyTable[mdp_key]['polTree']
                policyTable.close()
            else:
                print 'Doing Value Iteration for Goal (%d,%d) with PN=%.3f, RN=%.3f'%(goal[0],goal[1],posNoise,curNoiseVar[j])
                mdp.doValueIteration(0,50)
                Xpolicy,Ypolicy = mdp.DisplayPolicy()
                plt.title('MDP Policy with goal (%d,%d), posStdDev=%.3f, curStdDev=%.3f.'%(goal[0],goal[1],posNoise,curNoiseVar[j]))
                plt.savefig('%s/MDP_Policy_Goal_%04d%02d%02d_%d_%d_%.3f_RN_%.3f.png'%(pngDir,yy,mm,dd,goal[0],goal[1],posNoise,curNoiseVar[j]))
                plt.close()
                policyForKey={}
                policyForKey['U'] = mdp.mdp['U']
                policyForKey['polTree'] = mdp.pol_tree
                policyTable[mdp_key] = policyForKey
                policyTable.close()
            
            # Repeat for the Replanner.
            policyTable = shelve.open('PolicyTable_%04d%02d%02d_%d.shelve'%(yy,mm,dd,numDays))
            rp.GetTransitionModelFromShelf(yy,mm,dd,numDays,posNoise,curNoiseVar[j],conf.myDataDir+'NoisyGliderModels2')
            rp_key = 'RP_%s'%(keyForGoalAndNoise)
            if policyTable.has_key(rp_key):
                print 'Found this Replanner policy!'
                if policyTable[rp_key].has_key('sp_mst'):
                    rp.sp_mst = policyTable[rp_key]['sp_mst']
                if policyTable[rp_key].has_key('dist'):
                    rp.dist = policyTable[rp_key]['dist']
                policyTable.close()
            else:
                print 'Finding Shortest Paths for Goal (%d,%d) with PN=%.3f, RN=%.3f'%(goal[0],goal[1],posNoise,curNoiseVar[j])
                rp.CreateExpRiskGraph()
                sp_mst, dist = rp.GetShortestPathMST(goal)
                rp.PlotMRpaths(goal)
                plt.title('RP Policy with goal (%d,%d), posStdDev=%.3f, curStdDev=%.3f.'%(goal[0],goal[1],posNoise,curNoiseVar[j]))
                plt.savefig('%s/RP_Policy_Goal_%04d%02d%02d_%d_%d_%.3f_RN_%.3f.png'%(pngDir,yy,mm,dd,goal[0],goal[1],posNoise,curNoiseVar[j]))
                plt.close()
                policyForKey={}
                policyForKey['dist'] = rp.dist
                policyForKey['sp_mst'] = rp.sp_mst
                policyTable.close()
            
''' Either way, we have the policies in the table!
'''

                