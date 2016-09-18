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
from gpplib.GliderFileTools import *
import random
from sets import Set
import gpplib
from gpplib.Utils import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.SA_Replanner import *
from gpplib.LatLonConversions import *
import datetime
import ftplib


goto_ll_file_num = 26 # GOTO_L25.MA

''' Code for a simple planner. Here we use a Min-Expected-Risk planner.
'''
def GetPathFromStartToGoal(start,goal):
    sp_mst,dist = sarp.GetShortestPathMST(goal)
    path_to_goal=sp_mst['(%d,%d)'%(start[0],start[1])]['(%d,%d)'%(goal[0],goal[1])]
    return path_to_goal


conf = GppConfig()

dt = datetime.datetime.today() + datetime.timedelta(hours=2)
yy,mm,dd = 2012,7,14 #dt.year, dt.month, dt.day
numDays = 1

# Create our own .MA file from scratch.
new_goto_beh = GotoListFromGotoLfileGliderBehavior()
gldrEnums=GliderWhenEnums()
new_goto_beh.SetNumLegsToRun(gldrEnums.num_legs_to_run_enums['TRAVERSE_LIST_ONCE'])
new_goto_beh.SetStartWhen(gldrEnums.start_when_enums['BAW_IMMEDIATELY'])
new_goto_beh.SetStopWhen(gldrEnums.stop_when_enums['BAW_WHEN_WPT_DIST'])
new_goto_beh.SetInitialWaypoint(gldrEnums.initial_wpt_enums['CLOSEST'])



sarp = SA_Replanner(conf.myDataDir+'RiskMap.shelf',conf.myDataDir+'roms/',1.5)
sarp.GetTransitionModelFromShelf(yy,mm,dd,numDays,0.01,0.01,conf.myDataDir+'NoisyGliderModels4')
u,v,time1,depth,lat,lon = sarp.GetRomsData(yy,mm,dd,numDays,True,True)
sarp.gm.GetRomsData(yy,mm,dd,numDays,True,True)
sarp.CreateExpRiskGraph() # Run a Min-Exp-Risk replanner

# Start location
util = LLConvert()


# Catalina (GOAL) is at:  33.508150, -118.434300
goalLat,goalLon = 33.508150, -118.434300
goalX,goalY = sarp.gm.GetXYfromLatLon(goalLat,goalLon)


# Pt. Fermin (GOAL) is at: 33.6745, -118.362235
#goalLat, goalLon = 33.6745, -118.362235
#goalX,goalY = sarp.gm.GetXYfromLatLon(goalLat,goalLon)

# Un-comment when we have the real glider surfacing location.

start_wLat,start_wLon = 3331.670, -11826.515
startLat,startLon = util.WebbToDecimalDeg(start_wLat, start_wLon)

startLat, startLon =  33.670, -118.353

#startLat, startLon = 33.50815, -118.4343

startX, startY = sarp.gm.GetXYfromLatLon(startLat,startLon)

start = (int(startX+0.5),int(startY+0.5))
goal = (int(goalX+0.5),int(goalY+0.5))
print 'Start is: (%d,%d)'%(start[0],start[1])
print 'Goal is: (%d,%d)'%(goal[0],goal[1])
sp_mst,dist = sarp.GetShortestPathMST(goal)
# Run the planner
path_to_goal = GetPathFromStartToGoal(start,goal)

llconv = LLConvert()
w_lat,w_lon = [],[]
for loc in path_to_goal:
    x,y = sarp.gm.GetXYfromNodeStr(loc)
    lat,lon = sarp.gm.GetLatLonfromXY(x,y)
    wlat, wlon = llconv.DecimalDegToWebb(lat,lon)
    w_lat.append(wlat); w_lon.append(wlon)
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
dockServerDirectory = '/var/opt/gmc/gliders/%s/to-glider/'%(gliderName)     
gftp = GliderFTP(dockServerDirectory)
gotoLfile = 'GOTO_L%02d.MA'%(goto_ll_file_num)
if gftp.DoesFileExist(gotoLfile):
    gftp.deleteFile(gotoLfile)
gftp.SaveFile(gotoLfile,gotoLfile)
gftp.Close()

f2 = open('GOTO_L%02d.MA'%(goto_ll_file_num))
msg = ''
for line in f2.readlines():
    msg+=line
f2.close()
ggmail.mail('arvind.pereira@gmail.com','GOTO_L%02d.MA generated (start=%.5f,%.5f)'%(goto_ll_file_num,startLat,startLon),msg,gotoLfile)
#ggmail.mail('valerio.ortenzi@googlemail.com','GOTO_L%02d.MA generated (start=%.5f,%.5f)'%(goto_ll_file_num,startLat,startLon),msg,gotoLfile)    


