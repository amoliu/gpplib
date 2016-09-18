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

This mission file is specifically for running Expt. 3 where the gliders start off from 3329.557,-11819.777
and go toward the goal which is at: 3329.905, -11830.342

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
yy,mm,dd = 2012,7,31
yy,mm,dd = 2012,8,16
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


goal_wLat, goal_wLon = 3329.905, -11830.342 # Expt 3. Goal: (Aug 1, 2012)


goal_wLat, goal_wLon = 3330.315, -11819.695

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
start_wLat,start_wLon = 3329.905, -11830.342 # First run...


start_wLat, start_wLon = 3330.866, -11828.899 # Rusalka at 1st waypoint Aug 16, 2012 (8:34 pm)

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
        
gliderName = 'rusalka'
gotoLfile = 'GOTO_L%02d.MA'%(goto_ll_file_num)
#gliderName = 'he-ha-pe' # HeHaPe started off on the night of Jul 25, 2012.
'''
dockServerDirectory = '/var/opt/gmc/gliders/%s/to-glider/'%(gliderName)     
gftp = GliderFTP(dockServerDirectory)

try:
    gftp.deleteFile(gotoLfile)
except:
    pass
gftp.SaveFile(gotoLfile,gotoLfile)
gftp.Close()
'''
f2 = open('GOTO_L%02d.MA'%(goto_ll_file_num))
msg = ''
for line in f2.readlines():
    msg+=line
msg += original_waypoint_list    

f2.close()
ggmail.mail('arvind.pereira@gmail.com','GOTO_L%02d.MA generated (start=%.5f,%.5f)'%(goto_ll_file_num,startLat,startLon),msg,gotoLfile)
#ggmail.mail('valerio.ortenzi@googlemail.com','GOTO_L%02d.MA generated (start=%.5f,%.5f)'%(goto_ll_file_num,startLat,startLon),msg,gotoLfile)    


