''' 
@author: Arvind Pereira

@summary: 
This is a stand-alone program that is meant to allow us to generate a new mission file, given the surfacing location
of the glider.

@precondition:
Requires the ROMS data to be in the data/roms/ directory.This data should be either bearing the date of yesterday or today.
Also requires the transition models to be present in the data/NoisyTransitionModels4 directory.

It accepts the surfacing location of the glider, finds the next location in the file and generates a goto_ll file
for the glider.

Mission file for going from Catalina to Pt.Fermin is: MER_CTOPF.MI -> GOTO_L25.MA
Mission file for going from Pt.Fermin to Catalina is: MER_PFTOC.MI -> GOTO_L26.MA

GOTO files for MDP are : GOTO_L28.MA
GOTO files for MER are : GOTO_L27.MA
'''
from gpplib.GliderFileTools import *
import random
from sets import Set
import gpplib
from gpplib.Utils import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.StateActionMDP import *
from gpplib.LatLonConversions import *
from gpplib.PseudoWayptGenerator import *
from gpplib.Memoized_Switching_MDP import *
import datetime
import ftplib


#gliderName = 'rusalka'
gliderName = 'he-ha-pe'
#
#class SA_MDP2( SA_MDP ):
#    ''' Sub-class of SA_MDP dealing with the new type of Risk-map
#    '''
#    def __init__(self,shelfName='RiskMap3.shelf',sfcst_directory='./',dMax=1.5):
#        super(SA_MDP2,self).__init__(shelfName,sfcst_directory,dMax)
#        self.LastPolicyLoaded = ''
#        self.shelfName = shelfName
#                
#    def GetTransitionModelFromShelf(self,yy,mm,dd,numDays,posNoise=None,currentNoise=None,shelfDirectory='.'):
#        """ Loads up Transition models from the shelf for a given number of days, starting from a particular day, and a given amount of noise in position and/or a given amount of noise in the current predictions. We assume these models have been created earlier using ProduceTransitionModels.
#            
#            Args:
#                * yy (int): year
#                * mm (int): month
#                * dd (int): day
#                * numDays (int): number of days the model is being built over
#                * posNoise (float): Amount of std-deviation of the random noise used in picking the start location
#                * currentNoise (float): Amount of prediction noise in the ocean model
#                * shelfDirectory (str): Directory in which the Transition models are located.
#            
#            Updates:
#                * self.gm.FinalLocs: Stores the final locations 
#        """
#        self.posNoise = posNoise; 
#        self.currentNoise = currentNoise 
#        #import pdb; pdb.set_trace()
#        if posNoise==None and currentNoise==None:
#            gmShelf = shelve.open('%s/gliderModel3_%04d%02d%02d_%d.shelf'%(shelfDirectory,yy,mm,dd,numDays), writeback=False )
#        if posNoise!=None:
#            if currentNoise!=None:
#                gmShelf = shelve.open('%s/gliderModel3_%04d%02d%02d_%d_%.3f_RN_%.3f.shelf'%(shelfDirectory,yy,mm,dd,numDays,posNoise,currentNoise),writeback=False)
#            else:
#                gmShelf = shelve.open('%s/gliderModel3_%04d%02d%02d_%d_%.3f.shelf'%(shelfDirectory,yy,mm,dd,numDays,posNoise), writeback=False)
#        if posNoise==None and currentNoise!=None:
#            gmShelf=shelve.open('%s/gliderModel3_%04d%02d%02d_%d_RN_%.3f.shelf'%(shelfDirectory,yy,mm,dd,numDays,currentNoise), writeback=False)     
#        self.gm.TransModel = gmShelf['TransModel']
#        #if gmShelf.has_key('FinalLocs'):
#        self.gm.FinalLocs = gmShelf['FinalLocs']
#        #if gmShelf.has_key('TracksInModel'):
#        self.gm.TracksInModel = gmShelf['TracksInModel']
#        gmShelf.close()
#        # Now that we have loaded the new transition model, we better update our graph.
#        self.ReInitializeMDP()
#        
#    
#    def GetIndexedPolicy(self,yy,mm,dd,numDays,goal,**kwargs):
#        '''
#        Loads the policy corresponding to the goal, date, noise from shelf. 
#        (Need to create these before-hand using StoreAllPolicies.py)
#        Also need to ensure that all locations in this tour are also the same in StoreAllPolicies.py
#        
#        Args:
#            yy, mm, dd, numDays (int) : Self-explanatory
#            goal (tuple) : Goal in graph-coordinates
#        
#        Kwargs:
#            posNoise (float) : How much noise in start position to assume. defaults to 0.01
#            romsNoise (float): How much noise in ROMS predictions to assume. defaults to 0.01
#            
#            --- IMPORTANT ---- Always check to make sure that your risk-map is the right one!
#            Policy will have the shelf-name in it, but you've got to be careful in any case.
#        '''
#        if kwargs.has_key('posNoise'):
#            posNoise = kwargs['posNoise']
#        else:
#            posNoise = 0.01
#            
#        if kwargs.has_key('curNoise'):
#            romsNoise = kwargs['curNoise']
#        else:
#            romsNoise = 0.01
#        
#        if kwargs.has_key('theta'):
#            theta = kwargs['theta']
#        else:
#            theta = {'w_r':-1, 'w_g':10.}
#            self.theta = theta
#        
#        if kwargs.has_key('delta'):
#            delta = kwargs['delta']
#        else:
#            delta = 0.00001
#            
#        if kwargs.has_key('numIters'):
#            numIters = kwargs['numIters']
#        else:
#            numIters = 50
#            
#        if kwargs.has_key('gamma'):
#            gamma = kwargs['gamma']
#        else:
#            gamma = 1.0
#        self.gamma = gamma
#        
#        if kwargs.has_key('shelfDirectory'):
#            shelfDirectory=kwargs['shelfDirectory']
#        else:
#            shelfDirectory='.'
#        
#        policyStr = 'Pol_%s_%04d%02d%02d_%d_G_%d_%d_%.3f_%.3f_WR_%.3f_WG_%.3f'%(self.shelfName,yy,mm,dd,numDays, \
#                                                goal[0],goal[1],posNoise,curNoise,self.theta['w_r'],self.theta['w_g'])
#        if self.LastPolicyLoaded != policyStr:
#            policyTable = shelve.open('%s/PolicyTable_%04d%02d%02d_%d.shelve'%(shelfDirectory,yy,mm,dd,numDays))
#            keyForGoalAndNoise = 'G_%d_%d_PN_%.3f_RN_%.3f_WR_%.3f_WG_%.3f'%(goal[0],goal[1],posNoise,curNoise,self.theta['w_r'],self.theta['w_g'])
#            mdp_key = 'MDP_%s'%(keyForGoalAndNoise);
#            if policyTable.has_key(mdp_key):
#                print 'Loading policy for %s'%(policyStr)
#                if policyTable[mdp_key].has_key('U'):
#                        self.mdp['U'] = policyTable[mdp_key]['U']
#                if policyTable[mdp_key].has_key('polTree'):
#                        self.gm2 = policyTable[mdp_key]['polTree']
#                        
#                self.LastPolicyLoaded = policyStr
#            else:
#                print 'Policy not found. Doing Value iteration to find it.'
#                self.SetGoalAndRewardsAndInitTerminalStates(goal, theta)
#                self.doValueIteration(delta,numIters)
#                policyForKey={}
#                policyForKey['U'] = self.mdp['U']
#                policyForKey['polTree'] = self.gm2
#                policyTable[mdp_key] = policyForKey
#                self.LastPolicyLoaded = policyStr
#            policyTable.close()
    
            
        
    
        
goto_ll_file_num = 00 # GOTO_L28.MA for MDP
''' Code for a simple planner. Here we use a Min-Expected-Risk planner.
'''
conf = GppConfig()
dt = datetime.datetime.today() + datetime.timedelta(hours=2)
yy,mm,dd = 2013,8,15 #dt.year, dt.month, dt.day
numDays = 0
posNoise, curNoise = 0.01, 0.01 #0.01, 0.01
posNoise, curNoise = 0.01, 0.03 # Switched to higher noise at 19:22
saMdp = SA_MDP2(conf.myDataDir+'RiskMap3.shelf',conf.romsDataDir)
saMdp.GetTransitionModelFromShelf(yy, mm, dd, numDays, posNoise, curNoise, conf.myDataDir+'gliderModel3' )
saMdp.GetRomsData(yy,mm,dd,numDays,True,True)
util = LLConvert()

start_wLat,start_wLon = 3332.51, -11837.56  # 3328.218, -11825.861
start_wLat,start_wLon = 3332.119, -11828.799 # Replanned start for SCB_Box3.png (Fri evening)

start_wLat,start_wLon = 3332.156, -11820.797 # Started MDP plan with this waypoint. Currents = 0.01, 0.01
start_wLat,start_wLon = 3332.5461,-11826.8500 # First MDP plan switch. Currents = 0.01, 0.03
start_wLat, start_wLon = 3332.775, -11830.551 # Sunday afternoon re-tasking.

#--------- Now for the return journey
start_wLat, start_wLon = 3333.564, -11836.099 # Start on Monday morning
start_wLat, start_wLon = 3332.530, -11834.147 # Monday night
start_wLat, start_wLon = 3332.692, -11830.611 # Tuesday morning

start_wLat, start_wLon = 3332.530, -11834.147
start_wLat, start_wLon = 3332.802, -11830.611
start_wLat, start_wLon = 3327.198, -11821.707
start_wLat, start_wLon = 3328.328, -11823.463 # Saturday morning Jul 28, 2012
start_wLat, start_wLon = 3330.4184, -11826.850 # Saturday afternoon (expected) Jul 28, 2012
start_wLat, start_wLon = 3331.5620, -11844.1030


start_wLat, start_wLon = 3331.553, -11844.052 # Rusalka at the start, monday morning. Wpt 1
start_wLat, start_wLon = 3331.608, -11844.986 # Rusalka at 1st waypoint. 1:06 pm PST
start_wLat, start_wLon = 3332.242, -11843.067 # Rusalka at 2nd waypoint. 4:10 pm PST
start_wLat, start_wLon = 3332.812, -11841.145 # Rusalka at 3rd waypoint 7:02 pm PST
start_wLat, start_wLon=  3332.899, -11838.219  # Rusalka at 4th waypoint 12:02 am PST
start_wLat, start_wLon=  3331.219, -11836.214  # Rusalka at 5th waypoint 3:30 am PST
start_wLat, start_wLon = 3331.700, -11834.398  # Rusalka at 6th waypoint 6:30 am PST
start_wLat, start_wLon = 3330.799, -11831.594  # Rusalka at 7th waypoint 11:22 am
start_wLat, start_wLon = 3331.654, -11829.258  # Rusalka at 8th waypoint 13:40 pm PST
start_wLat, start_wLon = 3331.966, -11824.632 # Rusalka  at 9th waypoint 18:25 pm PST (Almost hit land here)... *Should disable PWpt
start_wLat, start_wLon = 3332.392, -11824.988 # Rusalka at 9th waypoint 18:35 pm PST (Using a dummy waypoint). Turned off pwpts.
start_wLat, start_wLon =  3332.748, -11821.887 # Rusalka at 10th waypoint 22:47 pm PST
start_wLat, start_wLon = 3331.639,-11819.775   # Rusalka at 11th waypoint 03:08 am PST

# ------------
start_wLat, start_wLon = 3329.904, -11819.583 # HeHaPe at 1st waypoint 9:50 am PST
start_wLat, start_wLon = 3329.629, -11819.402 # HeHaPe at 1st waypoint. 10:30 am PST.
start_wLat, start_wLon = 3328.527, -11821.518 # HeHaPe at 2nd waypoint. 15:15 pm PST.
start_wLat, start_wLon = 3326.944, -11822.223 # HeHaPe at 3rd waypoint  19:23 pm PST.
start_wLat, start_wLon = 3328.908, -11825.817 # HeHaPe at 4th  waypoint  01:13 am PST.


startLat,startLon = util.WebbToDecimalDeg(start_wLat, start_wLon)
#startLat,startLon = 33.508150, -118.434300

# -------------- Real Experiment with 2 gliders ------ Rusalka R_MDP_28.MI --------
#startLat, startLon  = 33.452367, -118.331455 # Start (assumed) on Fri July 27, 2012.
startX, startY = saMdp.gm.GetXYfromLatLon(startLat,startLon)


#goal_wLat,goal_wLon = 3328.228, -11819.370 # A_MDP_28.MI #3332.519, -11836.481
goal_wLat,goal_wLon = 3328.319, -11825.350 # Goal on return journey (Switched tuesday afternoon 7/24)

goal_wLat, goal_wLon = 3329.485, -11819.777 # Expt 2. Goal: (Jul 30, 2012)
goal_wLat, goal_wLon = 3329.905, -11830.342 # Expt 3. Goal: (Aug 1, 2012)
goalLat, goalLon = util.WebbToDecimalDeg(goal_wLat,goal_wLon)
#goalLat,goalLon = 33.56060, -118.5902 # Original Goal
#goalLat, goalLon = 33.471143, -118.360319 # Goal on return journey (Monday morning)
#goalLat, goalLon = 33.4871, -118.6727 # Expt1 : MDP on Rusalka
#goalLat, goalLon = 
goalX,goalY = saMdp.gm.GetXYfromLatLon(goalLat,goalLon)

start = (int(startX+0.5),int(startY+0.5))
goal = (int(goalX+0.5),int(goalY+0.5))
print 'Start is: (%d,%d)'%(start[0],start[1])
print 'Goal is: (%d,%d)'%(goal[0],goal[1])

# Create our own .MA file from scratch.
new_goto_beh = GotoListFromGotoLfileGliderBehavior()
gldrEnums=GliderWhenEnums()
new_goto_beh.SetNumLegsToRun(gldrEnums.num_legs_to_run_enums['TRAVERSE_LIST_ONCE'])
new_goto_beh.SetStartWhen(gldrEnums.start_when_enums['BAW_IMMEDIATELY'])
new_goto_beh.SetStopWhen(gldrEnums.stop_when_enums['BAW_WHEN_WPT_DIST'])
new_goto_beh.SetInitialWaypoint(gldrEnums.initial_wpt_enums['CLOSEST'])
'''
theta = {'w_r':-1, 'w_g':10.}
saMdp.SetGoalAndRewardsAndInitTerminalStates(goal, theta)
saMdp.doValueIteration(0.0001,50)
'''
thetaVal = {'w_r':-1.,'w_g':100.}
saMdp.GetIndexedPolicy(yy,mm,dd,numDays,goal,theta=thetaVal)
saMdp.DisplayPolicy()
plt.title('MDP Policy with goal (%d,%d)'%(goal[0],goal[1]))
plt.savefig('SAmdp_execution_%s.png'%(str(dt)))
saMdp.GetRomsData(yy, mm, dd, numDays, True, True)

rtc = RomsTimeConversion()
nHrsHence = 0.0
s_indx = rtc.GetRomsIndexNhoursFromNow(yy,mm,dd, nHrsHence)
plt.figure(); saMdp.gm.PlotNewRiskMapFig(); saMdp.gm.PlotCurrentField(rtc.GetRomsIndexNhoursFromNow(yy,mm,dd, nHrsHence))
for i in range(s_indx,s_indx+5):
    saMdp.SimulateAndPlotMDP_PolicyExecution(start, goal, i, False, 'r-')
plt.savefig('SAmdp_execution_%s.png'%(str(dt)))
bx,by = saMdp.GetPolicyAtCurrentNode(start,goal)
# Convert to lat,lon
#lat,lon = saMdp.gm.GetLatLonfromXY(bx,by)
lat,lon = zip(*saMdp.PolicyToGoal)
latL,lonL = list(lat),list(lon)
# Find the next location to aim for.
print 'Next location is :(%.4f,%.4f) which is (%d,%d) on the graph.'%(latL[0],lonL[0],bx,by)


enable_Pwpt = False
original_waypoint_list = '\n#Original waypoint list:\n'
for lat, lon in saMdp.PolicyToGoal:
    original_waypoint_list += '\n# %.6f,%.6f'%(lat,lon)


if enable_Pwpt:
    goalLat1, goalLon1 = latL[0],lonL[0]

    start_dt = datetime.datetime.utcnow()
    pwptg = PseudoWayPtGenerator(conf.myDataDir+'RiskMap3.shelf',conf.myDataDir+'roms', \
                                roms_yy=yy,roms_mm=mm,roms_dd=dd,roms_numDays=2)
    pwptg.no_comms_timeout_secs = 5*3600.
    startT=pwptg.rtc.GetRomsIndexFromDateTime(yy,mm,dd,start_dt)
    latFin,lonFin, doneSimulating = pwptg.SimulateDive((startLat,startLon), (goalLat1,goalLon1), startT, plot_figure=True,goal_marker='g^')
    print 'Without pseudo waypt. distance between Goal and Final location is: %.1f'%(pwptg.dc.GetDistBetweenLocs(goalLat1,goalLon1,latFin,lonFin))
    pLat,pLon,doneSimulating = pwptg.GetPseudoWayPt((startLat,startLon),(goalLat1,goalLon1),startT)
    latFin,lonFin,doneSimulating = pwptg.SimulateDive((startLat,startLon),(pLat,pLon),startT,plot_figure=True,line_color='g',goal_marker='b.')
    print 'Dist between Goal and Final location is: %.1f'%(pwptg.dc.GetDistBetweenLocs(goalLat1,goalLon1,latFin,lonFin))

    llconv = LLConvert()
    w_lat,w_lon = [],[]
    wlat,wlon = llconv.DecimalDegToWebb(pLat,pLon)
    w_lat.append(wlat); w_lon.append(wlon)
else:
    llconv = LLConvert()
    w_lat,w_lon = [],[]
    for lat, lon in saMdp.PolicyToGoal:
        wlat, wlon = llconv.DecimalDegToWebb(lat,lon)
        w_lat.append(wlat); w_lon.append(wlon)
    
new_goto_beh.SetWaypointListInWebbCoods(w_lat,w_lon)
AutoGenerateGotoLLfile(new_goto_beh,goto_ll_file_num,'Mission file for MDP policy being sent to %s'%(gliderName))


# Try to transfer the file over to the dockerver
'''
f = ftplib.FTP('10.1.1.20')
f.login('gpplibuser','gl1d3r')
f.cwd('%s'%(dockServerDirectory))
f2 = open('GOTO_L%02d.MA'%(goto_ll_file_num),'r')
f.delete('GOTO_L%02d.MA'%(goto_ll_file_num))
f.storlines('STOR GOTO_L%02d.MA'%(goto_ll_file_num),f2)
f.quit()
'''
ggmail = GliderGMail('usc.glider','cinaps123')
        

#gliderName = 'sim_039'
dockServerDirectory = '/var/opt/gmc/gliders/%s/to-glider/'%(gliderName)     
gftp = GliderFTP(dockServerDirectory)
gotoLfile = 'GOTO_L%02d.MA'%(goto_ll_file_num)
#if gftp.DoesFileExist(gotoLfile):
try:
    gftp.deleteFile(gotoLfile)
except:
    pass
gftp.SaveFile(gotoLfile,gotoLfile)
gftp.Close()

f2 = open('GOTO_L%02d.MA'%(goto_ll_file_num))
msg = ''
for line in f2.readlines():
    msg+=line
msg+= original_waypoint_list
f2.close()
ggmail.mail('arvind.pereira@gmail.com','GOTO_L%02d.MA generated (start=%.5f,%.5f)'%(goto_ll_file_num,startLat,startLon),msg,gotoLfile)
#ggmail.mail('valerio.ortenzi@googlemail.com','GOTO_L%02d.MA generated (start=%.5f,%.5f)'%(goto_ll_file_num,startLat,startLon),msg,gotoLfile)    


