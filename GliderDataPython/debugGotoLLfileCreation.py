'''
 This file tests the GOTO_LXY.MA file creation aspects of GliderFileTools
'''
from gpplib.GliderFileTools import *
import random
from sets import Set
import gpplib
from gpplib.Utils import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.SA_Replanner import *
from gpplib.LatLonConversions import *

''' Code for a simple planner. Here we use a Min-Expected-Risk planner.
'''
def GetPathFromStartToGoal(start,goal):
    sp_mst,dist = sarp.GetShortestPathMST(goal)
    path_to_goal=sp_mst['(%d,%d)'%(start[0],start[1])]['(%d,%d)'%(goal[0],goal[1])]
    return path_to_goal

''' Come up with a sample plan... '''
conf = gpplib.Utils.GppConfig()
yy,mm,dd,numDays = 2011,2,1,2
start,goal=(0,6),(8,1)
    
sarp = SA_Replanner(conf.myDataDir+'RiskMap.shelf',conf.myDataDir+'roms/')
#sarp.GetTransitionModelFromShelf(yy,mm,dd,numDays,0.1,0.01,conf.myDataDir+'NoisyGliderModels2')
u,v,time1,depth,lat,lon = sarp.GetRomsData(yy,mm,dd,numDays)
#sarp.CreateExpRiskGraph() # Run a Min-Exp-Risk replanner
sarp.CreateMinRiskGraph()
path_to_goal = GetPathFromStartToGoal(start,goal)


''' Code to write out a goto_lXY.ma file. Here we are going to write out to GOTO_L16.MA
'''

# Create our own .MA file from scratch.
new_goto_beh = GotoListFromGotoLfileGliderBehavior()

gldrEnums=GliderWhenEnums()
new_goto_beh.SetNumLegsToRun(gldrEnums.num_legs_to_run_enums['TRAVERSE_LIST_ONCE'])
new_goto_beh.SetStartWhen(gldrEnums.start_when_enums['BAW_IMMEDIATELY'])
new_goto_beh.SetStopWhen(gldrEnums.stop_when_enums['BAW_WHEN_WPT_DIST'])
new_goto_beh.SetInitialWaypoint(gldrEnums.initial_wpt_enums['CLOSEST'])

llconv = LLConvert()
w_lat,w_lon = [],[]
for loc in path_to_goal:
    x,y = sarp.gm.GetXYfromNodeStr(loc)
    lat,lon = sarp.gm.GetLatLonfromXY(x,y)
    wlat, wlon = llconv.DecimalDegToWebb(lat,lon)
    w_lat.append(wlat); w_lon.append(wlon)
new_goto_beh.SetWaypointListInWebbCoods(w_lat,w_lon)
AutoGenerateGotoLLfile(new_goto_beh,16)

''' Might want to go to http://cinaps.usc.edu/gliders/waypoints.php to test the output GOTO_L16.MA file.
'''