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
from gpplib.Omniscient_NonStationaryMDP import *
from gpplib.Memoized_Omni_NonStationaryMDP import *
from gpplib.LatLonConversions import *
from gpplib.PseudoWayptGenerator import *
import datetime
import ftplib
import sys

def printUsage():
    print "Usage: PreComputePolicy_Omni_NS_MDP_GP.py yy mm dd goalLat goalLon"

if not len(sys.argv)==6:
    printUsage()
    sys.exit()
argv = sys.argv
yy,mm,dd = int(argv[1]),int(argv[2]),int(argv[3])
goalLat, goalLon = float(argv[4]), float(argv[5])

conf = GppConfig()

numDays = 0
posNoise = 0.001 #0.01, 0.01
s_indx,e_indx = 0, 24*9
saNS_Mdp = Omni_NS_MDP2(conf.myDataDir+'RiskMap3.shelf',conf.romsDataDir)
saNS_Mdp.GetTransitionModelFromShelf(yy, mm, dd, s_indx, e_indx, posNoise, conf.myDataDir+'gliderModelNS/' )
#saNS_Mdp.GetRomsData(yy,mm,dd,numDays,True,True)
util = LLConvert()

goalX,goalY = saNS_Mdp.gm.GetXYfromLatLon(goalLat,goalLon)
goal = (int(goalX+0.5),int(goalY+0.5))
print 'Goal is: (%d,%d)'%(goal[0],goal[1])

rtc = RomsTimeConversion()
nHrsHence = 0.0
dt = datetime.datetime(yy,mm,dd,0,0) + datetime.timedelta(hours=nHrsHence)
s_indx = rtc.GetRomsIndexFromDateTime(yy,mm,dd, dt)
print 's_indx = %d'%(s_indx)
thetaVal = {'w_r':-1.,'w_g':100.}
saNS_Mdp.GetIndexedPolicy(yy,mm,dd,numDays,goal,theta=thetaVal)
