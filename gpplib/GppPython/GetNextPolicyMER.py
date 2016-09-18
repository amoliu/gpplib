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
'''
import random
import datetime
import ftplib

from sets import Set
import gpplib
from gpplib.Utils import *
from gpplib.GliderFileTools import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.PseudoWayptGenerator import *
from gpplib.SA_Replanner import *
from gpplib.LatLonConversions import *


class SA_Replanner2( SA_Replanner ):
    ''' Sub-class of SA_Replanner dealing with the new type of Risk-map
    '''
    def __init__(self,shelfName='RiskMap3.shelf',sfcst_directory='./',dMax=1.5):
        super(SA_Replanner2,self).__init__(shelfName,sfcst_directory,dMax)
        
        
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
        """
        self.posNoise = posNoise; self.currentNoise = currentNoise
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
        self.gm.FinalLocs = gmShelf['FinalLocs']
        self.gm.TracksInModel = gmShelf['TracksInModel']
        self.gModel = {}
        self.gModel['TransModel'] = gmShelf['TransModel']
        gmShelf.close()
        

        

goto_ll_file_num = 27 # GOTO_L27.MA for MER.


conf = GppConfig()

dt = datetime.datetime.today() + datetime.timedelta(hours=0)
yy,mm,dd = 2012,7,21 #dt.year, dt.month, dt.day
yy,mm,dd = 2012,7,24 # Recovery day...
yy,mm,dd = 2012,7,25 # HeHaPe launch day.
yy,mm,dd = 2012,7,26 # Rusalka, HeHaPe rendezvous start day
yy,mm,dd = 2012,7,27 # Multi-glider test... HeHaPe running MER.
yy,mm,dd = 2012,7,28
yy,mm,dd = 2012,7,29
yy,mm,dd = 2012,7,30
yy,mm,dd = 2012,7,31
numDays = 0

# Create our own .MA file from scratch.
new_goto_beh = GotoListFromGotoLfileGliderBehavior()
gldrEnums=GliderWhenEnums()
new_goto_beh.SetNumLegsToRun(gldrEnums.num_legs_to_run_enums['TRAVERSE_LIST_ONCE'])
new_goto_beh.SetStartWhen(gldrEnums.start_when_enums['BAW_IMMEDIATELY'])
new_goto_beh.SetStopWhen(gldrEnums.stop_when_enums['BAW_WHEN_WPT_DIST'])
new_goto_beh.SetInitialWaypoint(gldrEnums.initial_wpt_enums['CLOSEST'])



sarp = SA_Replanner2(conf.myDataDir+'RiskMap3.shelf',conf.myDataDir+'roms/',1.5)
sarp.GetTransitionModelFromShelf(yy,mm,dd,numDays,0.01,0.01,conf.myDataDir+'NoisyGliderModels4')
u,v,time1,depth,lat,lon = sarp.GetRomsData(yy,mm,dd,numDays,True,True)
sarp.gm.GetRomsData(yy,mm,dd,numDays,True,True)
sarp.CreateExpRiskGraph() # Run a Min-Exp-Risk replanner

# Start location
util = LLConvert()


# Catalina (GOAL) is at:  33.508150, -118.434300
goal_wLat,goal_wLon = 3332.519, -11836.481

# Just a try
goal_wLat,goal_wLon = 3328.228, -11819.370 # Original goal on SCB_Box3.png (Thurs evening)

goal_wLat, goal_wLon = 3328.5779, -11829.4717
#goal_wLat,goal_wLon = 3328.228, -11819.370 # Original goal on SCB_Box3.png (Thurs evening)
goal_wLat, goal_wLon = 3328.063, -11828.583 # Pickup Jul 27, 2012 ----- Interrupted MDP run ------


goal_wLat, goal_wLon = 3329.485, -11819.777 # Expt 2. Goal: (Jul 30, 2012)

#goal_wLat, goal_wLon = 

goalLat, goalLon = util.WebbToDecimalDeg(goal_wLat,goal_wLon)
#goalLat, goalLon = 33.469001, -118.475650 # Midnight of the 25th. Recovery.
#goalLat,goalLon = 33.508150, -118.434300
#goalLat, goalLon = 33.520, -118.333 # HeHaPe goal July 25th (probably)
#goalLat, goalLon = 33.4354, -118.331214 # Rendezvous goal on July 26th for both HeHaPe and Rusalka.

#goalLat, goalLon = 33.4871, -118.6727 # MER on HeHaPe (Expt. 1)

goalX,goalY = sarp.gm.GetXYfromLatLon(goalLat,goalLon)


# Pt. Fermin (GOAL) is at: 33.6745, -118.362235
#goalLat, goalLon = 33.6745, -118.362235
#goalX,goalY = sarp.gm.GetXYfromLatLon(goalLat,goalLon)

# Un-comment when we have the real glider surfacing location.

#start_wLat,start_wLon = 3331.670, -11826.515
start_wLat,start_wLon = 3328.783, -11826.374 # First run...

start_wLat,start_wLon = 3331.071, -11836.262 # Original start on SCB_Box3.png (Thurs evening)
start_wLat,start_wLon = 3332.119, -11828.799 # Replanned start for SCB_Box3.png (Fri evening)
start_wLat,start_wLon = 3330.971, -11821.832 # Replanned start for SCB_Box3.png (Sat evening)

start_wlat, start_wlon = 3332.161, -11820.698

start_wLat,start_wLon = 3331.989, -11829.262 # Wednesday mid-night. 00 hrs.
# ----- Pickup Jul 27, 2012 --------
start_wLat, start_wLon = 3333.275, -11828.740
start_wLat, start_wLon = 3331.918, -11830.826

start_wLat, start_wLon = 3330.073, -11831.336 # Wed July 25th Glider collect.

start_wLat, start_wLon = 3331.396, -11829.324  # Thurs July 26th, Rusalka Rendezvous mission
start_wLat, start_wLon = 3331.916, -11822.124   # Thurs July 26th, HeHaPe Rendezvous mission
start_wLat, start_wLon = 3329.487, -11823.674
start_wLat, start_wLon = 3330.562, -11826.737


start_wLat, start_wLon = 3331.5620, -11844.1030
start_wLat, start_wLon = 3331.298, -11843.497 # Test waypoint 8:05 am PST

start_wLat, start_wLon = 3331.2930,-11843.4930 # Expt 2. HeHaPe running MER

start_wLat, start_wLon = 3330.489, -11841.750 # Expt 2: HeHaPe call in at 2:16 PST

start_wLat, start_wLon = 3329.294, -11839.145 # Expt 2: HeHaPe call in at 19:00 PST

start_wLat, start_wLon = 3329.285, -11838.493  # Expt 2: HeHaPe call in at 19:57 PST

start_wLat, start_wLon = 3330.348, -11836.221  # Expt 2: HeHaPe call in at 00:01 PST

start_wLat, start_wLon=  3330.967, -11834.190  # Expt 2: HeHaPe call in at 02:43 PST
start_wLat, start_wLon = 3331.485, -11833.248 # Expt 2: Hehape call in at 04:43 PST
start_wLat, start_wLon = 3330.496, -11831.554 # Expt 2: HeHaPe call in at 09:06 PST
start_wLat, start_wLon = 3330.458, -11829.856 # Expt 2: HeHaPe call in at 11:12 PST
start_wLat, start_wLon = 3329.573, -11826.025 # Expt 2: HeHaPe call in at 15:56 PST

start_wLat, start_wLon = 3328.352, -11821.830 # Expt 2: HeHaPe call in at 1:00am PST (8/1/2012)

startLat,startLon = util.WebbToDecimalDeg(start_wLat, start_wLon)
#startLat, startLon = 33.54317,-118.359547   # Thurs July 26th, HeHaPe Rendezvous mission (Used instead of real location.)

# --------------- Real Experiments with 2 gliders --------- HeHaPe H_MER_27.MI --------
#startLat, startLon  = 33.452367, -118.331455 # Start (assumed) on Fri July 27, 2012.


#startLat, startLon =  33.670, -118.353

#startLat, startLon = 33.50815, -118.4343
''' Code for a simple planner. Here we use a Min-Expected-Risk planner.
'''
def GetPathFromStartToGoal(start,goal,sarp):
    sp_mst,dist = sarp.GetShortestPathMST(goal)
    path_to_goal=sp_mst['(%d,%d)'%(start[0],start[1])]['(%d,%d)'%(goal[0],goal[1])]
    return path_to_goal


def GetPathFromPathString(pathToGoal,sarp):
    pathX, pathY= [], []
    for node_str in pathToGoal:
        pX,pY=sarp.GetXYfromNodeStr(node_str)
        pathX.append(pX); pathY.append(pY)
    return pathX, pathY

startX, startY = sarp.gm.GetXYfromLatLon(startLat,startLon)

start = (int(startX+0.5),int(startY+0.5))
goal = (int(goalX+0.5),int(goalY+0.5))
print 'Start is: (%d,%d)'%(start[0],start[1])
print 'Goal is: (%d,%d)'%(goal[0],goal[1])
sp_mst,dist = sarp.GetShortestPathMST(goal)
# Run the planner
path_to_goal = GetPathFromStartToGoal(start,goal,sarp)
pathX,pathY = GetPathFromPathString(path_to_goal,sarp)

#from GetNewRiskObsMaps2 import gfmrp
#gfmrp.CreateGraphOfLowRiskPatches()

#goalLat1, goalLon1 = gfmrp.riskMapLat[pathX[1],pathY[1]], gfmrp.riskMapLon[pathX[1],pathY[1]]
'''
goalLat1,goalLon1 = sarp.gm.GetLatLonfromXY(pathX[1],pathY[1])

# We will modify the first waypoint so that it is a pseudo waypoint
start_dt = datetime.datetime.utcnow()
pwptg = PseudoWayPtGenerator(conf.myDataDir+'RiskMap3.shelf',conf.myDataDir+'roms', \
                            roms_yy=yy,roms_mm=mm,roms_dd=dd,roms_numDays=2,glider_vel=0.15,glider_vel_nom=0.27)
pwptg.no_comms_timeout_secs = 5*3600.
startT=pwptg.rtc.GetRomsIndexFromDateTime(yy,mm,dd,start_dt)
latFin,lonFin, doneSimulating = pwptg.SimulateDive((startLat,startLon), (goalLat1,goalLon1), startT, plot_figure=True,goal_marker='g^')
print 'Without pseudo waypt. distance between Goal and Final location is: %.1f'%(pwptg.dc.GetDistBetweenLocs(goalLat1,goalLon1,latFin,lonFin))
pLat,pLon,doneSimulating = pwptg.GetPseudoWayPt((startLat,startLon),(goalLat1,goalLon1),startT)
latFin,lonFin,doneSimulating = pwptg.SimulateDive((startLat,startLon),(pLat,pLon),startT,plot_figure=True,line_color='g',goal_marker='b.')
print 'Dist between Goal and Final location is: %.1f'%(pwptg.dc.GetDistBetweenLocs(goalLat1,goalLon1,latFin,lonFin))

num_iter = 2
latFin,lonFin,doneSimulating = pwptg.SimulateDive((startLat,startLon), (goalLat1,goalLon1), startT, plot_figure=False,goal_marker='g^')
print 'Without pseudo waypt. distance between Goal and Final location is: %.1f'%(pwptg.dc.GetDistBetweenLocs(goalLat1,goalLon1,latFin,lonFin))
pLat,pLon = pwptg.IteratePseudoWptCalculation((startLat,startLon),(goalLat1,goalLon1), startT, num_iter)
latFin,lonFin,doneSimulating = pwptg.SimulateDive((startLat,startLon),(pLat,pLon),startT,plot_figure=False,line_color='g',goal_marker='b.')
print 'After %d iterations, Dist between Goal and Final location is: %.1f'%(num_iter,pwptg.dc.GetDistBetweenLocs(goalLat1,goalLon1,latFin,lonFin))
print pLat,pLon
'''

original_waypoint_list = '\n#Original waypoint list:\n'
llconv = LLConvert()
w_lat,w_lon = [],[]
for idx,loc in enumerate(path_to_goal):
    x,y = sarp.gm.GetXYfromNodeStr(loc)
    lat,lon = sarp.gm.GetLatLonfromXY(x,y)
    original_waypoint_list += '\n# '+loc+' %.6f,%.6f'%(lat,lon)
    #if idx==1:
    #    lat,lon=pLat,pLon
    #    print 'Pseudo waypoint (%f,%f) inserted at waypoint %d'%(pLat,pLon,idx)
    #    original_waypoint_list += '\n# Pseudowpt:'+loc+' %.6f,%.6f'%(lat,lon)
    wlat, wlon = llconv.DecimalDegToWebb(lat,lon)
    w_lat.append(wlat); w_lon.append(wlon)
    
#w_lat=w_lat[1:2]; w_lon=w_lon[1:2]
if len(w_lat)>1:
    w_lat=w_lat[1:]; w_lon=w_lon[1:]
new_goto_beh.SetWaypointListInWebbCoods(w_lat,w_lon)
AutoGenerateGotoLLfile(new_goto_beh,goto_ll_file_num)

rtc = RomsTimeConversion()
nHrsHence = 0.0
plt.figure(); sarp.gm.PlotNewRiskMapFig(); sarp.gm.PlotCurrentField(rtc.GetRomsIndexNhoursFromNow(yy,mm,dd, nHrsHence))
totRiskMER = 0
numFailsMER = 0
s_indx = rtc.GetRomsIndexNhoursFromNow(yy,mm,dd, nHrsHence)
for i in range(s_indx,s_indx+5):
    tempRiskMER,landedMER=sarp.SimulateAndPlotMR_PolicyExecution(start,goal,sp_mst,i,newFig=False)
    if landedMER != True:
        totRiskMER+=tempRiskMER
    else:
        numFailsMER+=1

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
        
gliderName = 'he-ha-pe'
#gliderName = 'he-ha-pe' # HeHaPe started off on the night of Jul 25, 2012.
dockServerDirectory = '/var/opt/gmc/gliders/%s/to-glider/'%(gliderName)     
gftp = GliderFTP(dockServerDirectory)
gotoLfile = 'GOTO_L%02d.MA'%(goto_ll_file_num)
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
msg += original_waypoint_list    

f2.close()
ggmail.mail('arvind.pereira@gmail.com','GOTO_L%02d.MA generated (start=%.5f,%.5f)'%(goto_ll_file_num,startLat,startLon),msg,gotoLfile)
#ggmail.mail('valerio.ortenzi@googlemail.com','GOTO_L%02d.MA generated (start=%.5f,%.5f)'%(goto_ll_file_num,startLat,startLon),msg,gotoLfile)    


