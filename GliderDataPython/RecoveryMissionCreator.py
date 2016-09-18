''' 
@author: Arvind A de Menezes Pereira.

RecoveryMissionCreator.py is a new program which is capable of creating
a box of given dimensions around a given point. It also accepts an UTC
timeout. This is basically a mission to run a holding pattern for
pickup, or just to make the gliders wait for some time before we give
them something new to do.

'''
import gpplib
from gpplib.Utils import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.LatLonConversions import *
from gpplib.GliderFileTools import *
import datetime
import pytz
from gpplib.MapTools import *

''' These are the important parameters for the mission file '''

sendToDockserver = True

yo_file_num = 10
goto_ll_num = 99 # 26-PWptGenerator, 27-MER, 28-MDP
surf_file_num = 10    # Surfac<N>.ma file to be called. Has no effect here.
do_deep_dive = False   # Should we be diving deep here??? 
no_comms_time = 1.0 #12.5
surf_every_time= 8.0
yy,mm,dd,hr,mi = 2013,8,19,11,0 # Date/Time in time-zone specified
tz1=pytz.timezone('US/Pacific')  # here.
mission_file_name = 'REC1HR.MI' #'RECOVER.MI'#%(goto_ll_num) #'MERPF2CD.MI'  # MDP-Catalina-To_P.Fermin_StayDeep
#gliderName = 'unit_294'
#gliderName = 'unit_260'
gliderName = 'rusalka'
#gliderName = 'he-ha-pe'
#gliderName = 'sim_039'

'''wLat0,wLon0 = 3328.458,-11829.116   # Location of pickup spot
wLat0,wLon0 = 3329.491,-11829.495   # Location of stayput hold
wLat0,wLon0 = 3330.861, -11820.281  # Stayput location on Fri, Aug 17
wLat0,wLon0 = 3330.938, -11844.198  # Stayput location on Mon 5:57, Aug 20.
wLat0,wLon0 = 3328.459, -11829.615 # Stayput location for recovery on Aug 23, 2012
'''
wLat0,wLon0 = 3328.458, -11829.115 # ecohabt1.mi location for test mission on Aug 28, 2012
llconv = LLConvert()
#lat0,lon0 = 33.5643, -118.3078#33.5082,-118.1020 # llconv.WebbToDecimalDeg(wLat0,wLon0)
lat0,lon0 = llconv.WebbToDecimalDeg(wLat0,wLon0)

''' --------- Create the box --------- '''
''' Code to write out a goto_lXY.ma file. Here we are going to write out to GOTO_L16.MA
'''
goto_ll_file_num = goto_ll_num # Works with Hold missions for Rusalka and HeHaPe
# Create our own .MA file from scratch.
rec_edge = 500. # 2 km (How big a square do we want?)

er = EarthRadius(lat0)
dc = DistCalculator(er.R)

# Do a simple linearization 
lat2m = dc.GetDistBetweenLocs(lat0-0.5,lon0,lat0+0.5,lon0) # Dist along y-axis for a degree change in latitude
lon2m = dc.GetDistBetweenLocs(lat0,lon0-0.5,lat0,lon0+0.5) # Dist along x-axis for a degree change in longitude

m2lat = 1./lat2m
m2lon = 1./lon2m

lat,lon = [], []
edges = [(-rec_edge/2.,-rec_edge/2.),(-rec_edge/2.,rec_edge/2.),(rec_edge/2.,rec_edge/2.),(rec_edge/2.,-rec_edge/2.)]
for e1,e2 in edges:
    lat.append(lat0+e2*m2lat)
    lon.append(lon0+e1*m2lon)
    
w_lat, w_lon = [], []
for (lat1,lon1) in zip(lat,lon):
    wlat, wlon = llconv.DecimalDegToWebb(lat1,lon1)
    w_lat.append(wlat); w_lon.append(wlon)


new_goto_beh = GotoListFromGotoLfileGliderBehavior()

gldrEnums=GliderWhenEnums()
#new_goto_beh.SetNumLegsToRun(gldrEnums.num_legs_to_run_enums['LOOP_FOREVER'])  # Use this to loop forever.
new_goto_beh.SetNumLegsToRun(gldrEnums.num_legs_to_run_enums['TRAVERSE_LIST_ONCE'])
new_goto_beh.SetStartWhen(gldrEnums.start_when_enums['BAW_IMMEDIATELY'])
new_goto_beh.SetStopWhen(gldrEnums.stop_when_enums['BAW_WHEN_WPT_DIST'])
new_goto_beh.SetInitialWaypoint(gldrEnums.initial_wpt_enums['CLOSEST'])

new_goto_beh.SetWaypointListInWebbCoods(w_lat,w_lon)
AutoGenerateGotoLLfile(new_goto_beh,goto_ll_file_num)

''' Might want to go to http://cinaps.usc.edu/gliders/waypoints.php to test the output GOTO_L16.MA file.
'''
ggmail = GliderGMail('usc.glider','cinaps123')
        

dockServerDirectory = '/var/opt/gmc/gliders/%s/to-glider/'%(gliderName)     
gotoLfile = 'GOTO_L%02d.MA'%(goto_ll_file_num)

if sendToDockserver:
    gftp = GliderFTP(dockServerDirectory)

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
f2.close()
ggmail.mail('arvind.pereira@gmail.com','GOTO_L%02d.MA generated for glider %s, (start=%.5f,%.5f)'%(goto_ll_file_num,gliderName,w_lat[0],w_lon[0]),msg,gotoLfile)
#ggmail.mail('subbaray@usc.edu','GOTO_L%02d.MA generated for glider %s, (start=%.5f,%.5f)'%(goto_ll_file_num,gliderName,w_lat[0],w_lon[0]),msg,gotoLfile)
#ggmail.mail('cwahl@mbari.org','GOTO_L%02d.MA generated for glider %s, (start=%.5f,%.5f)'%(goto_ll_file_num,gliderName,w_lat[0],w_lon[0]),msg,gotoLfile)
#ggmail.mail('dariod@sccwrp.org','GOTO_L%02d.MA generated for glider %s, (start=%.5f,%.5f)'%(goto_ll_file_num,gliderName,w_lat[0],w_lon[0]),msg,gotoLfile)



''' Now create the Mission file and the Yo file '''

msg = 'Calls -> YO%02d.MA, GOTO_L%02d.MA and SURFAC%02d.MA\n'%(yo_file_num, goto_ll_num,surf_file_num)

''' Mission file creation begins... '''

gldr_beh_list = GliderBehaviorList()
gldrEnums = GliderWhenEnums()

''' Abort-End Behaviors '''
abend_beh = AbortEndGliderBehavior()
gldr_beh_list.Append( abend_beh )

''' Surfacing Behaviors
'''
surf_if_yo_complete = SurfaceGliderBehavior(start_when=gldrEnums.start_when_enums['BAW_PITCH_IDLE'], \
                    gps_wait_time = 300, keystroke_wait_time = 180, \
                    force_iridium_use = gldrEnums.force_iridium_use_enums['FORCE_IRIDIUM_USE'] )

surf_if_no_comms_for_N_hrs = SurfaceGliderBehavior(start_when=gldrEnums.start_when_enums['BAW_NOCOMM_SECS'], \
                    end_action=gldrEnums.end_action_enums['WAIT_FOR_CTRL-C_OR_RESUME'], \
                    when_secs=(no_comms_time*60*60) )

surf_at_every_wpt = SurfaceGliderBehavior(start_when=gldrEnums.start_when_enums['BAW_WHEN_HIT_WAYPOINT'], \
                    end_action=gldrEnums.end_action_enums['WAIT_FOR_CTRL-C_OR_RESUME'])

surf_every_N_hrs= SurfaceGliderBehavior(start_when=gldrEnums.start_when_enums['BAW_EVERY_SECS'], \
                    when_secs=(3*60*60) )

surf_for_science = SurfaceGliderBehavior(start_when=gldrEnums.start_when_enums['BAW_SCI_SURFACE'], \
                    report_all=False, keystroke_wait_time=15 )

surf_when_mission_done = SurfaceGliderBehavior(start_when=gldrEnums.start_when_enums['BAW_HEADING_IDLE'], \
                    end_action=gldrEnums.end_action_enums['QUIT'], \
                    keystroke_wait_time=300)

# Now for the tricky one: UTC time
# Let us assume that we want to pick up the glider at 10:00 am PST on July 18, 2012

temp_pickup_date=tz1.localize(datetime.datetime(yy,mm,dd,hr,mi))
pickup_date = temp_pickup_date.astimezone(tz1)
#pickup_date=datetime.datetime(yy,mm,dd,hr,mi,tzinfo=pytz.timezone('US/Pacific'))
pd_utc = pickup_date.astimezone(pytz.utc)
surf_when_utc = SurfaceGliderBehavior(start_when=gldrEnums.start_when_enums['BAW_WHEN_UTC_TIME'],
                when_utc_year=pd_utc.year, when_utc_month=pd_utc.month, when_utc_day=pd_utc.day,
                when_utc_hour=pd_utc.hour, when_utc_min=pd_utc.minute, when_utc_on_surface=True )

''' Add all the surfacing behaviors from above '''
gldr_beh_list.Append(surf_if_yo_complete);
gldr_beh_list.Append(surf_if_no_comms_for_N_hrs); msg+= '\nNO-Comms Time -> %.2f hours.'%(no_comms_time)
gldr_beh_list.Append(surf_at_every_wpt)
#gldr_beh_list.Append(surf_every_N_hrs); msg+='\nSURF every -> %.2f hours \n'%(surf_every_time)
gldr_beh_list.Append(surf_for_science)
gldr_beh_list.Append(surf_when_utc); msg+='\nSurface at UTC -> %s UTC\n'%(str(pd_utc))
gldr_beh_list.Append(surf_when_mission_done)

''' Now for a Yo-behavior '''
yo_behavior = YoGliderBehavior(args_from_file=yo_file_num, start_when=gldrEnums.start_when_enums['BAW_PITCH_IDLE'])
gldr_beh_list.Append(yo_behavior)

''' Goto-List behavior '''
goto_ll_behavior = GotoListGliderBehavior(args_from_file=goto_ll_num)
gldr_beh_list.Append(goto_ll_behavior)

''' Sample all science sensors only on downcast '''
sample_beh = SampleGliderBehavior()
gldr_beh_list.Append(sample_beh)

''' Prepare to dive '''
prepare_to_dive = PrepareToDiveGliderBehavior()
gldr_beh_list.Append(prepare_to_dive)

''' Turn most input sensors off '''
sensors_in_behavior = InputSensorsGliderBehavior()
gldr_beh_list.Append(sensors_in_behavior)

''' Turn off the water_velocity m/s '''
#gldr_beh_list.SetSensorInitialization( u_use_current_correction=0 ); msg+='\nInternal current correction turned off.'

#gldr_beh_list.SetSensorInitialization(u_use_current_correction=0,m_water_vx=0.0,m_water_vy=0.0)
''' Turn off the Freewave console if no carrier-detect in 15 seconds '''
no_carrier_timeout = 15.0
gldr_beh_list.SetSensorInitialization( u_use_current_correction=0, u_use_ctd_depth_for_flying=1, c_console_on=1, u_console_reqd_cd_off_time=no_carrier_timeout )
#gldr_beh_list.SetSensorInitialization( c_console_on=1, u_console_reqd_cd_off_time=no_carrier_timeout ); 
msg+='\nFW console will turn off in %.1fsec if no carrier-detected'%(no_carrier_timeout)
gldr_beh_list.SaveMissionFile( mission_file_name )
# Create our own .MA file from scratch.doc
new_yo_beh = YoFileGliderBehavior()
gldrEnums=GliderWhenEnums()
if do_deep_dive:
    new_yo_beh.ConvertToStayDeepYo()
AutoGenerateYoFile(new_yo_beh,yo_file_num)

#today = datetime.datetime.utcnow()
#today_tz = today.replace(tzinfo=pytz.utc)
ggmail = GliderGMail('usc.glider','cinaps123')
dockServerDirectory = '/var/opt/gmc/gliders/%s/to-glider/'%(gliderName)     

if sendToDockserver:
    gftp = GliderFTP(dockServerDirectory)
    try:
        gftp.deleteFile(mission_file_name)
    except:
        pass
    gftp.SaveFile(mission_file_name,mission_file_name)
ggmail.mail('arvind.pereira@gmail.com','Mission File autogenerated. %s for glider: %s.'%(mission_file_name, gliderName),msg,mission_file_name)
#ggmail.mail('subbaray@usc.edu','Mission File autogenerated. %s.'%(mission_file_name),msg,mission_file_name)
#ggmail.mail('cwahl@mbari.org','Mission File autogenerated. %s.'%(mission_file_name),msg,mission_file_name)
#ggmail.mail('dariod@sccwrp.org','Mission File autogenerated. %s.'%(mission_file_name),msg,mission_file_name)
yofile = 'YO%02d.MA'%(yo_file_num)
#if gftp.DoesFileExist(yofile):
if sendToDockserver:
    try:
        gftp.deleteFile(yofile)
    except:
        pass
    gftp.SaveFile(yofile,yofile)
    gftp.Close()

f2 = open('YO%02d.MA'%(yo_file_num))
msg = ''
for line in f2.readlines():
    msg+=line
f2.close()
ggmail.mail('arvind.pereira@gmail.com','YO%02d.MA generated for glider: %s '%(yo_file_num,gliderName),msg,yofile)
#ggmail.mail('subbaray@usc.edu','YO%02d.MA generated for glider: %s '%(yo_file_num,gliderName),msg,yofile)
#ggmail.mail('cwahl@mbari.org','YO%02d.MA generated for glider: %s '%(yo_file_num,gliderName),msg,yofile)
#ggmail.mail('dariod@sccwrp.org','YO%02d.MA generated for glider: %s '%(yo_file_num,gliderName),msg,yofile)

