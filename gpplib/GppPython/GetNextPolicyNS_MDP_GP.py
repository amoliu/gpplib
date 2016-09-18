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
import UseAgg
from gpplib.GliderFileTools import *
import random
from sets import Set
import gpplib
from gpplib.Utils import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.StateAction_NonStationaryMDP import *
from gpplib.Memoized_StateAction_NonStationaryMDP import *
from gpplib.LatLonConversions import *
from gpplib.PseudoWayptGenerator import *
import datetime
import ftplib

            
        
    
gliderName = 'rusalka'
#gliderName = 'he-ha-pe'
goto_ll_file_num = 28 # GOTO_L28.MA for MDP
''' Code for a simple planner. Here we use a Min-Expected-Risk planner.
'''
conf = GppConfig()
dt = datetime.datetime.today() + datetime.timedelta(hours=2)
yy,mm,dd = 2013,8,18 #dt.year, dt.month, dt.day
numDays = 0
posNoise = 0.001 #0.01, 0.01
s_indx,e_indx = 0, 48
saNS_Mdp = SA_NS_MDP2(conf.myDataDir+'RiskMap3.shelf',conf.romsDataDir)
saNS_Mdp.GetTransitionModelFromShelf(yy, mm, dd, s_indx, e_indx, posNoise, conf.myDataDir+'gliderModelNS/' )
saNS_Mdp.GetRomsData(yy,mm,dd,numDays,True,True)
util = LLConvert()

#start_wLat, start_wLon = 3331.872, -11831.907  # Rusalka at 15th waypoint 01:45 am

#start_wLat, start_wLon = 3328.036, -11825.499
#start_wLat, start_wLon = 3328.659, -11820.043 # Expt starts at 19:10 tuesday. Aug 13, 2013.
#start_wLat, start_wLon = 3326.589, -11820.968                   # Change here.
#start_wLat, start_wLon = 3326.916, -11819.640 
#start_wLat, start_wLon = 3329.270, -11819.685 # Still used 8/13/2013
#start_wLat, start_wLon = 3330.4184,-11820.0820 # Pre-computing...
#
#start_wLat, start_wLon = 3331.218, -11820.589 # New transition models. 22:49. 8/14/2013.
#start_wLat, start_wLon = 3332.061, -11822.773 #02:10. 8/15/2013.
#start_wLat, start_wLon = 3332.340, -11826.740 # 9:49. 8/15/2013. (8/14/2013 data.)
#start_wLat, start_wLon = 3332.340, -11826.884 # 9:49. 8/15/2013. (8/14/2013 data.)
#start_wLat, start_wLon = 3332.705, -11829.013
#start_wLat, start_wLon = 3331.452, -11830.492
#start_wLat, start_wLon = 3329.965, -11831.427
#start_wLat, start_wLon = 3331.246, -11833.510
#start_wLat, start_wLon = 3331.341, -11834.706
#---------------------------------------------
# Experiment 2 to 33.5065, -118.3329
start_wLat, start_wLon = 3332.410, -11837.015 # 16:20, Aug 16 2013. (Using Aug 16 data).
start_wLat, start_wLon = 3332.444, -11834.871
start_wLat, start_wLon = 3330.171, -11832.378
start_wLat, start_wLon = 3331.152, -11829.367
start_wLat, start_wLon = 3332.443, -11828.616 # Using Aug 17 data.
start_wLat, start_wLon = 3333.839, -11828.290 # Resumed.
start_wLat, start_wLon = 3330.335, -11827.788 # Not used... We missed it, here.
#start_wLat, start_wLon = 

#start_wLat, start_wLon =  # Pre-computing with 8/15/2013 data.

startLat,startLon = util.WebbToDecimalDeg(start_wLat, start_wLon)
#startLat, startLon = 33.47, -118.42
#startLat,startLon = 33.508150, -118.434300

# -------------- Real Experiment with 2 gliders ------ Rusalka R_MDP_28.MI --------
#startLat, startLon  = 33.452367, -118.331455 # Start (assumed) on Fri July 27, 2012.
startX, startY = saNS_Mdp.gm.GetXYfromLatLon(startLat,startLon)

#goal_wLat,goal_wLon = 3328.228, -11819.370 # A_MDP_28.MI #3332.519, -11836.481
#goal_wLat,goal_wLon = 3332.494, -11836.914 # Goal for Expt 1, Aug 13, 2013
#goalLat, goalLon = util.WebbToDecimalDeg(goal_wLat,goal_wLon)

goalLat, goalLon = 33.5065, -118.3329 # Goal for Expt 2, Aug 16, 2013




#goalLat,goalLon = 33.56060, -118.5902 # Original Goal
#goalLat, goalLon = 33.471143, -118.360319 # Goal on return journey (Monday morning)
#goalLat, goalLon = 33.4871, -118.6727 # Expt1 : MDP on Rusalka
#goalLat, goalLon = 
goalX,goalY = saNS_Mdp.gm.GetXYfromLatLon(goalLat,goalLon)

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
rtc = RomsTimeConversion()
nHrsHence = 0.0
s_indx = rtc.GetRomsIndexNhoursFromNow(yy,mm,dd, nHrsHence)

print 's_indx = %d'%(s_indx)

#s_indx = 20
thetaVal = {'w_r':-1.,'w_g':100.}
saNS_Mdp.GetIndexedPolicy(yy,mm,dd,numDays,goal,theta=thetaVal)
saNS_Mdp.DisplayPolicyAtTimeT( s_indx )
plt.title('SA NS MDP Policy with goal (%d,%d)'%(goal[0],goal[1]))
plt.savefig('SA_NS_mdp_execution_%s.png'%(str(dt)))
saNS_Mdp.GetRomsData(yy, mm, dd, numDays, True, True)


plt.figure(); saNS_Mdp.gm.PlotNewRiskMapFig(); saNS_Mdp.gm.PlotCurrentField( s_indx ) #rtc.GetRomsIndexNhoursFromNow(yy,mm,dd, nHrsHence))
for i in range(s_indx,s_indx+5):
    saNS_Mdp.SimulateAndPlotMDP_PolicyExecution(start, goal, i, False, 'r-')
plt.savefig('SAmdp_execution_%s.png'%(str(dt)))
bx,by = saNS_Mdp.GetPolicyAtCurrentNode(start,goal,s_indx)
# Convert to lat,lon
#lat,lon = saMdp.gm.GetLatLonfromXY(bx,by)
lat,lon = zip(*saNS_Mdp.PolicyToGoal)
latL,lonL = list(lat),list(lon)
# Find the next location to aim for.
print 'Next location is :(%.4f,%.4f) which is (%d,%d) on the graph.'%(latL[0],lonL[0],bx,by)


enable_Pwpt = False
original_waypoint_list = '\n#Original waypoint list:\n'
for lat, lon in saNS_Mdp.PolicyToGoal:
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
    for lat, lon in saNS_Mdp.PolicyToGoal:
        wlat, wlon = llconv.DecimalDegToWebb(lat,lon)
        w_lat.append(wlat); w_lon.append(wlon)
        
MaxNumWpts = 10
if len(w_lat)>MaxNumWpts: # Truncate...
    w_lat = w_lat[0:MaxNumWpts]; w_lon = w_lon[0:MaxNumWpts]
    
new_goto_beh.SetWaypointListInWebbCoods(w_lat,w_lon)
AutoGenerateGotoLLfile(new_goto_beh,goto_ll_file_num,'Mission file for MDP policy for Glider %s'%(gliderName))


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
        

gotoLfile = 'GOTO_L%02d.MA'%(goto_ll_file_num)

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
try:
    ggmail.mail('arvind.pereira@gmail.com','GOTO_L%02d.MA generated (start=%.5f,%.5f) for Glider %s'%(goto_ll_file_num,startLat,startLon,gliderName),msg,gotoLfile)
    #ggmail.mail('valerio.ortenzi@googlemail.com','GOTO_L%02d.MA generated (start=%.5f,%.5f)'%(goto_ll_file_num,startLat,startLon),msg,gotoLfile)    
except:
    pass

