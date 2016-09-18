from gpplib.GliderFileTools import *
import random
from sets import Set
import gpplib
from gpplib.Utils import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.StateActionMDP import *
from gpplib.LatLonConversions import *
from gpplib.PseudoWayptGenerator import *
from gpplib.StateActionMDP2 import *
from gpplib.SA_Replanner2 import *
import datetime
import ftplib
import simplekml


class SwitchingMDP_Planner:
    
    def __init__(self,riskMapShelf='RiskMap.shelf',romsDataDir='roms',gliderModelDir='NoisyGliderModels', **kwargs):
        self.conf = GppConfig()
        self.riskMapShelf = riskMapShelf
        self.romsDataDir = romsDataDir
        self.gliderModelDir = gliderModelDir
        self.pngDir = 'smdp_pngs'
        self.posNoise = 0.01
        self.latGoal = (-1,-1) # Fictitious location which is off the map
        self.lastStart = (-2,-2) # Another fictitious location
        self.StopExecutionOnError = False
        self.LastTransModelLoaded = None
        self.LastPolicyLoaded = None
        self.LastCurrentDataLoaded = None
        
        try:
            os.mkdir(self.pngDir)
        except OSError as (errno, strerror):
            pass
        self.PolicyTableLoaded = False
        
        self.saMdp = SA_MDP2(riskMapShelf,romsDataDir)
        self.saReplanner = SA_Replanner2(riskMapShelf,romsDataDir)
        


'''

conf = GppConfig()

# Start date
s_yy, s_mm, s_dd = 2012, 8, 17 ; s_hr, s_mi = 0, 0
e_yy, e_mm, e_dd = 2012, 8, 23 ; e_hr, e_mi = 23,59

start_wlat, start_wlon = 3330.291, -11824.928
goal_wlat, goal_wlon   = 3328.218, -11825.861

dr = DateRange( s_yy, s_mm, s_dd, e_yy, e_mm, e_dd )
rtc = RomsTimeConversion()
pwptg = PseudoWayPtGenerator( conf.myDataDir+'RiskMap3.shelf', conf.myDataDir+'roms', \
                            roms_yy=s_yy, roms_mm=s_mm, roms_dd=s_dd )

start_dt = datetime.datetime(s_yy,s_mm,s_dd,s_hr,s_mi)
startT  = pwptg.rtc.GetRomsIndexFromDateTime(yy,mm,dd,start_dt)

done = False
while ( not done ):
    pass
'''