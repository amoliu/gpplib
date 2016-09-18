''' This class will attempt to provide the glider with an alternate location to aim for so that it gets closer to the 
waypoint it was originally aiming for.
'''
from matplotlib import pyplot as plt
import sys
import numpy as np
import math, random
import time, datetime

from gpplib import *
from gpplib.Utils import *
from gpplib.LatLonConversions import *
from gpplib.GenGliderModelUsingRoms import GliderModel
from gpplib.MapTools import *
from gpplib.GliderFileTools import *


class PseudoWayPtGenerator(object):
    ''' Pseudo waypoint generator class which allows us to select a waypoint, 
        and then it reverse calculates a location to aim for such that we get to the 
        desired location.
    '''
    def __init__(self,riskMap='RiskMap.shelf',romsDataDir='/roms/',**kwargs):
        ''' Initialize the pseudo waypoint generator
        
        Args:
            riskMap     (str): path to and name of shelf containing the risk map etc.
            
            romsDataDir (str): directory containing the ROMS data used for simulations. 
        
        Keyword Args:
            use_realtime_data (bool): Flag that indicates if we should be using real-time data for 
                                simulations or if we will be passed either a datetime or 
                                date and time. True if we will use real-time. False if not.
            
            use_datetime (datetime): Datetime object that indicates the date and time of the simulation.
            
            yy,mm,dd,hr,mi (int): Year, Month, Day, Hour and Minute to start simulation at if not via a datetime.
            
            no_comms_timeout_secs (int): No. of seconds of no communications due to which the glider will 
                                        resurface (>300).
            
            roms_yy, roms_mm, roms_dd (int): Roms data file if we want to explicitly specify one.
            
            glider_vel (float) : Velocity of the glider to be used in simulations (0<glider_vel<2)
            
            max_dive_depth (float) : Maximum depth the glider will be diving to.
            max_climb_depth (float) : Maximum depth the glider will be climbing to.
        '''
        self.gm = GliderModel(riskMap,romsDataDir)
        self.rtc = RomsTimeConversion()
        self.ll_conv = LLConvert()
        self.er=EarthRadius(33.55)
        self.dc = DistCalculator(self.er.R)
        
        # We have not yet loaded the ROMS data.
        self.romsDataLoaded = False
        # Don't perform a full-simulation by default
        self.perform_full_simulation = False
        # Don't treat going off the map as a collision
        self.hold_vals_off_map = True
        # Maximum dive depth 
        self.max_dive_depth = 80.
        
        self.no_comms_timeout_secs = 12*3600
        # Take care of figuring out the time.        
        self.use_realtime_data = True
        self.TestKwArgs(**kwargs)
        
        
    def TestKwArgs(self,**kwargs):
        if kwargs.has_key('use_realtime_data'):
            use_realtime_data = self.use_realtime_data
            if use_real_time_data:
                self.use_real_time_data = True
                self.dt = datetime.datetime.utcnow()
            else:
                self.use_real_time_data = False
                # Since we are not using real-time data you better pass
                # that data to me.
                if kwargs.has_key('use_datetime'): # We have been passed a datetime object.
                    dt = kwargs['use_datetime']
                    self.dt = dt
                elif kwargs.has_key('yy'):
                    yy,mm,dd = kwargs['yy'],kwargs['mm'],kwargs['dd'] # We have been passed the date
                    hr,mi    = kwargs['hr'],kwargs['mi']
                    self.dt = datetime.datetime(yy,mm,dd,hr,mi) # we assume we were passed date and time in UTC
                else: 
                    self.dt = None
        
        if kwargs.has_key('no_comms_timeout_secs'):
            no_comms_timeout_secs = kwargs['no_comms_timeout_secs']
            if(no_comms_timeout_secs<=299):
                self.no_comms_timeout_secs = no_comms_timeout_secs
            else:
                raise
            
        if kwargs.has_key('roms_yy'):
            roms_yy, roms_mm, roms_dd, roms_numDays = kwargs['roms_yy'], kwargs['roms_mm'], kwargs['roms_dd'], kwargs['roms_numDays']
            roms_dt = datetime.datetime(roms_yy,roms_mm,roms_dd,0,0) # Auto-test ROMS date
            self.u,self.v,self.time1,self.depth,self.lat,self.lon=self.gm.GetRomsData(roms_yy,roms_mm,roms_dd,roms_numDays,True,True)
            self.romsDataLoaded = True
            
        if kwargs.has_key('glider_vel'):
            glider_vel = kwargs['glider_vel']
            if glider_vel<=0 or glider_vel>=2:
                print 'Sorry, gliders are not that quick yet... Ignoring this entry!'
            else:
                self.gm.gVel = glider_vel
                
        if kwargs.has_key('glider_vel_nom'):
            glider_vel_nom = kwargs['glider_vel_nom']
            if glider_vel_nom<=0 or glider_vel_nom>=2:
                print 'Sorry, gliders are not that quick yet... Ignoring this entry!'
            else:
                self.gm.gVelNom = glider_vel_nom
        
        if kwargs.has_key('max_dive_depth'):
            max_dive_depth = kwargs['max_dive_depth']
            if max_dive_depth>95:
                max_dive_depth = 95
            if max_dive_depth<5:
                max_dive_depth = 5        
            self.max_dive_depth = max_dive_depth
            
        if kwargs.has_key('max_climb_depth'):
            max_climb_depth = kwargs['max_climb_depth']
            if max_climb_depth>0:
                max_climb_depth=0
            if max_climb_depth<30:
                max_climb_depth = 30
            self.max_climb_depth = max_climb_depth
            self.gm.MinDepth = max_climb_depth
            
        if kwargs.has_key('perform_full_simulation'):
            if kwargs['perform_full_simulation']:
                self.perform_full_simulation = True
            else:
                self.perform_full_simulation = False
                
        if kwargs.has_key('hold_vals_off_map'):
            if kwargs['hold_vals_off_map']:
                self.hold_vals_off_map = True
            else:
                self.hold_vals_off_map = False
        
        
    def SimulateDive(self,start,goal,startT,**kwargs):
        ''' Simulate a dive given a start in (lat,lon), goal in (lat,lon) and a starting time.
        '''
        self.TestKwArgs(**kwargs) # First, set any keyword args that may have been passed in.
        plot_figure = False
        
        line_color,line_width = 'r-',2.5
        if kwargs.has_key('line_color'):
            line_color = kwargs['line_color']
        if kwargs.has_key('line_width'):
            line_width = kwargs['line_width']    
        
        
        if kwargs.has_key('plot_figure'):
            if kwargs['plot_figure']:
                plot_figure=True
                plt.figure()
                self.gm.PlotNewRiskMapFig()
                #plt.figure(); 
                #plt.imshow(self.gm.riskMapArray,origin='lower')
                #goalx,goaly = self.gm.GetPxPyFromLatLon(goal[0],goal[1])
                goalx,goaly = self.gm.GetXYfromLatLon(goal[0],goal[1])
                if kwargs.has_key('goal_marker'):
                    plt.plot(goalx,goaly,kwargs['goal_marker'])
                if kwargs.has_key('plot_currents'):
                    if kwargs['plot_currents']:
                        self.gm.PlotCurrentField(startT)
        
        self.gm.InitSim(start[0],start[1],goal[0],goal[1],self.max_dive_depth,startT, \
                   self.perform_full_simulation,self.hold_vals_off_map)
        xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist = \
            self.gm.SimulateDive_R(self.no_comms_timeout_secs/3600.)
        
        
        diveTime = self.gm.t_prime-startT
        self.diveTime,self.latArray,self.lonArray,self.depthArray,self.tArray,self.possibleCollision,self.totalDist = \
                diveTime, latArray, lonArray, depthArray, tArray, possibleCollision, totalDist
        
        if plot_figure:
            if possibleCollision == False:
                tempX,tempY = self.gm.GetXYfromLatLon(np.array(latArray),np.array(lonArray))
                x_sims,y_sims = tempX[-1:],tempY[-1:]
                plt.plot(tempX,tempY,line_color)
            else:
                tempX,tempY = self.gm.GetXYfromLatLon(np.array(latArray),np.array(lonArray))
                plt.plot(tempX,tempY,'r.-' )
                x_sims,y_sims = 0,0
        
        if self.gm.doneSimulating:
            print 'Surfaced due to waypoint at %.4f, %.4f'%(latFin,lonFin)
        else:
            print 'Surfaced due to no-comms in time %.2f hrs'%(diveTime)
        
        return latFin,lonFin,self.gm.doneSimulating
    
    def GetPseudoWayPt(self,start,goal,startT):
        latFin, lonFin, doneSimulating = self.SimulateDive(start, goal, startT)
        goalLat, goalLon = goal
        
        pLat = 2*goalLat - latFin
        pLon = 2*goalLon - lonFin
        return pLat, pLon, doneSimulating
    
    def IteratePseudoWptCalculation(self,start,goal,startT,numTimes=2):
        pGoal = goal
        goalLat, goalLon = goal
        p1Lat,p1Lon = goal
        closest = float('inf')
        for i in range(0,numTimes):
            print 'Iter %d/%d'%(i+1,numTimes)
            pLat,pLon, doneSimulating = self.GetPseudoWayPt(start, pGoal, startT)
            pLatFin, pLonFin,doneSimulating = self.SimulateDive(start, (pLat,pLon), startT,plot_figure=True,line_color='g',goal_marker='b.')
            deltaLat, deltaLon = goalLat-pLatFin, goalLon-pLonFin
            dist2goal = self.dc.GetDistBetweenLocs(goalLat,goalLon,pLatFin,pLonFin)
            if dist2goal<closest and doneSimulating:
                p1Lat,p1Lon = pLat, pLon
                closest = dist2goal
            pGoal = (goalLat + deltaLat, goalLon + deltaLon)
        return p1Lat, p1Lon
    
    def GetPseudoWptForStartTimeRange(self,start,goal,startT1,startT2,numTimes=2):
        if startT1>startT2:
            print 'startT1 (%.1f) should be less than startT2 (%.1f)'%(startT1,startT2)
        
        pLats,pLons,errs = [], [], []
        for startT in range(startT1,startT2):
            pLat,pLon = self.IteratePseudoWptCalculation(start, goal, startT, numTimes)
            pLatFin, pLonFin,doneSimulating = self.SimulateDive(start, (pLat,pLon), startT)
            dist2goal = self.dc.GetDistBetweenLocs(goalLat,goalLon,pLatFin,pLonFin)
            pLats.append(pLat); pLons.append(pLon); errs.append(dist2goal)
        
        return pLats,pLons,errs


'''

goto_file_num = 26
conf = GppConfig()
yy,mm,dd = 2012,7,18
start_dt = datetime.datetime.utcnow()


pwptg = PseudoWayPtGenerator(conf.myDataDir+'RiskMap.shelf',conf.myDataDir+'roms', \
                            roms_yy=yy,roms_mm=mm,roms_dd=dd)

pwptg.no_comms_timeout_secs = 6 * 3600.

start_wlat, start_wlon = 3330.291,-11824.928 #3329.157, -11829.444 #3329.670, -11825.695#3340.2302, -11821.1875 #3333.73,-11821.670974 # util.WebbToDecimalDeg(3333.73,-11821.670974)
startLat,startLon = pwptg.ll_conv.WebbToDecimalDeg(start_wlat, start_wlon)

goal_wlat,goal_wlon =  3328.218, -11825.861 #3333.9917, -11828.2000 # 3336.8625, -11825.3125
goalLat,goalLon = pwptg.ll_conv.WebbToDecimalDeg(goal_wlat,goal_wlon)
#goalLat,goalLon = 33.5185, -118.4866 #33.5582,-118.4906 #
print 'Goal is %f,%f'%(goalLat,goalLon)
startT=pwptg.rtc.GetRomsIndexFromDateTime(yy,mm,dd,start_dt)


latFin,lonFin, doneSimulating = pwptg.SimulateDive((startLat,startLon), (goalLat,goalLon), startT, plot_figure=True,goal_marker='g^')
print 'Without pseudo waypt. distance between Goal and Final location is: %.1f'%(pwptg.dc.GetDistBetweenLocs(goalLat,goalLon,latFin,lonFin))
pLat,pLon,doneSimulating = pwptg.GetPseudoWayPt((startLat,startLon),(goalLat,goalLon),startT)
latFin,lonFin,doneSimulating = pwptg.SimulateDive((startLat,startLon),(pLat,pLon),startT,plot_figure=True,line_color='g',goal_marker='b.')
print 'Dist between Goal and Final location is: %.1f'%(pwptg.dc.GetDistBetweenLocs(goalLat,goalLon,latFin,lonFin))

num_iter = 15
plt.figure()
latFin,lonFin,doneSimulating = pwptg.SimulateDive((startLat,startLon), (goalLat,goalLon), startT, plot_figure=True,goal_marker='g^')
print 'Without pseudo waypt. distance between Goal and Final location is: %.1f'%(pwptg.dc.GetDistBetweenLocs(goalLat,goalLon,latFin,lonFin))
pLat,pLon = pwptg.IteratePseudoWptCalculation((startLat,startLon),(goalLat,goalLon), startT, num_iter)
latFin,lonFin,doneSimulating = pwptg.SimulateDive((startLat,startLon),(pLat,pLon),startT,plot_figure=True,line_color='g',goal_marker='b.')
print 'After %d iterations, Dist between Goal and Final location is: %.1f'%(num_iter,pwptg.dc.GetDistBetweenLocs(goalLat,goalLon,latFin,lonFin))
print pLat,pLon

# Create a GOTO_LXX.MA file
new_goto_beh = GotoListFromGotoLfileGliderBehavior()
gldrEnums = GliderWhenEnums()
new_goto_beh.SetNumLegsToRun(gldrEnums.num_legs_to_run_enums['TRAVERSE_LIST_ONCE'])
new_goto_beh.SetStartWhen(gldrEnums.start_when_enums['BAW_IMMEDIATELY'])
new_goto_beh.SetStopWhen(gldrEnums.stop_when_enums['BAW_WHEN_WPT_DIST'])
new_goto_beh.SetInitialWaypoint(gldrEnums.initial_wpt_enums['CLOSEST'])
w_lat,w_lon = [],[]
wlat, wlon = pwptg.ll_conv.DecimalDegToWebb(pLat,pLon)
w_lat.append(wlat); w_lon.append(wlon)
new_goto_beh.SetWaypointListInWebbCoods(w_lat,w_lon)
AutoGenerateGotoLLfile(new_goto_beh,goto_file_num)

# Upload the file to the server.
gliderName = 'rusalka'
goto_file_name = 'GOTO_L%02d.MA'%(goto_file_num)
ggmail = GliderGMail('usc.glider','cinaps123')
dockServerDirectory = '/var/opt/gmc/gliders/%s/to-glider/'%(gliderName)     
gftp = GliderFTP(dockServerDirectory)
if gftp.DoesFileExist(goto_file_name):
    gftp.deleteFile(goto_file_name)
gftp.SaveFile(goto_file_name,goto_file_name)
gftp.Close()

f2 = open(goto_file_name,'r')
msg = 'Pseudo-WaypointGenerator.py auto-generated this file. (For use with VALSTART.MI).\n'
for line in f2.readlines():
    msg+=line
f2.close()
ggmail.mail('arvind.pereira@gmail.com','%s generated for glider: %s '%(goto_file_name,gliderName),msg,goto_file_name)
#ggmail.mail('valerio.ortenzi@googlemail.com','%s generated for glider: %s '%(goto_file_name,gliderName),msg,goto_file_name)
'''
    
'''
# Now, let us try to get the best pseudo-waypoint over a windowed average.
 
startT1, startT2 = startT-1, startT+5
num_iter = 5
plt.figure()
latFin,lonFin,doneSimulating = pwptg.SimulateDive((startLat,startLon), (goalLat,goalLon), startT, plot_figure=True,goal_marker='g^')
print 'Without pseudo waypt. distance between Goal and Final location is: %.1f'%(pwptg.dc.GetDistBetweenLocs(goalLat,goalLon,latFin,lonFin))
pLats,pLons,errs = pwptg.GetPseudoWptForStartTimeRange((startLat,startLon), (goalLat,goalLon), startT1, startT2, num_iter )
print zip(pLats,pLons,errs)

print 'Now simulating the average of these (%.5f,%.5f)'%(pLat,pLon)
latFin,lonFin,doneSimulating = pwptg.SimulateDive((startLat,startLon),(pLat,pLon),startT,plot_figure=True,line_color='y',goal_marker='b.')
print 'Using avg.case Pseudo-wpt, dist. between Goal and Final location is: %.1f'%(pwptg.dc.GetDistBetweenLocs(goalLat,goalLon,latFin,lonFin))
'''


