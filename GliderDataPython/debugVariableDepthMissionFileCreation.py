''' Demo program for Mission file creation (from scratch). We also create a deep-dive Yo file at the 
same time and link to it.
'''
import gpplib
from gpplib.Utils import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.LatLonConversions import *
from gpplib.GliderFileTools import *
import datetime
import pytz

''' These are the important parameters for the mission file '''
yo_file_num = 83
goto_ll_num = 83 # 26-PWptGenerator, 27-MER, 28-MDP, 29-HoldingPattern
surf_file_num = 10    # Surfac<N>.ma file to be called. Has no effect here.
do_deep_dive = False   # Should we be diving deep here??? 
no_comms_time = 5 #12.5
surf_every_time= 3.0
yy,mm,dd,hr,mi = 2012,8,23,10,45 # Date/Time in time-zone specified
tz1=pytz.timezone('US/Pacific')  # here.
#mission_file_name = 'MERC2PFD.MI'  # MER-Catalina-To_P.Fermin_StayDeep
#mission_file_name = 'R_MER_%02d.MI'%(goto_ll_num) #'MERPF2CD.MI'  # MDP-Catalina-To_P.Fermin_StayDeep
#mission_file_name = 'H_MDP_%02d.MI'%(goto_ll_num) #'MERPF2CD.MI'  # MDP-Catalina-To_P.Fermin_StayDeep
#mission_file_name = 'A_HLD_%02d.MI'%(goto_ll_num) #'MERPF2CD.MI'  # MDP-Catalina-To_P.Fermin_StayDeep
mission_file_name = 'RGPMDP%02d.MI'%(goto_ll_num) #'MERPF2CD.MI'  # MDP-Catalina-To_P.Fermin_StayDeep
mission_file_name = 'HFXMDP%02d.MI'%(goto_ll_num) #'MERPF2CD.MI'  # MDP-Catalina-To_P.Fermin_StayDeep
mission_file_name = 'RYMDP%02d.MI'%(goto_ll_num)
gliderName = 'rusalka'
#gliderName = 'he-ha-pe'
#gliderName='sim_039'

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
gldr_beh_list.SetSensorInitialization( u_use_current_correction=0 ); msg+='\nInternal current correction turned off.'
#gldr_beh_list.SetSensorInitialization(u_use_current_correction=0,m_water_vx=0.0,m_water_vy=0.0)
''' Turn off the Freewave console if no carrier-detect in 15 seconds '''
no_carrier_timeout = 15.0
gldr_beh_list.SetSensorInitialization( c_console_on=1, u_console_reqd_cd_off_time=no_carrier_timeout ); msg+='\nFW console will turn off in %.1fsec if no carrier-detected'%(no_carrier_timeout)
gldr_beh_list.SaveMissionFile( mission_file_name )
# Create our own .MA file from scratch.
new_yo_beh = YoFileGliderBehavior()
gldrEnums=GliderWhenEnums()
if do_deep_dive:
    new_yo_beh.ConvertToStayDeepYo()

#new_yo_beh.SetTargetDepthForClimb(29)
new_yo_beh.SetTargetDepthForDive(80)

AutoGenerateYoFile(new_yo_beh,yo_file_num)

#today = datetime.datetime.utcnow()
#today_tz = today.replace(tzinfo=pytz.utc)
ggmail = GliderGMail('usc.glider','cinaps123')

dockServerDirectory = '/var/opt/gmc/gliders/%s/to-glider/'%(gliderName)     

gftp = GliderFTP(dockServerDirectory)
#if gftp.DoesFileExist(mission_file_name):
try:
    gftp.deleteFile(mission_file_name)
except:
    pass
gftp.SaveFile(mission_file_name,mission_file_name)

ggmail.mail('arvind.pereira@gmail.com','Mission File autogenerated. %s for glider: %s.'%(mission_file_name, gliderName),msg,mission_file_name)
ggmail.mail('ryan.smith@qut.edu.au','Mission File autogenerated. %s for glider: %s.'%(mission_file_name, gliderName),msg,mission_file_name)
#ggmail.mail('mragan@usc.edu','Mission File autogenerated. %s.'%(mission_file_name),msg,mission_file_name)
yofile = 'YO%02d.MA'%(yo_file_num)

try: #if gftp.DoesFileExist(yofile):
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
ggmail.mail('ryan.smith@qut.edu.au','YO%02d.MA generated for glider: %s '%(yo_file_num,gliderName),msg,yofile)

#ggmail.mail('mragan@usc.edu','YO%02d.MA generated'%(yo_file_num),msg,yofile)
#ggmail.mail('valerio.ortenzi@googlemail.com','GOTO_L%02d.MA generated (start=%.5f,%.5f)'%(goto_ll_file_num,startLat,startLon),msg,gotoLfile)    

