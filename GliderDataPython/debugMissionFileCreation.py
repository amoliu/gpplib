''' Demo program for Mission file creation (from scratch).
'''
import gpplib
from gpplib.Utils import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.LatLonConversions import *
from gpplib.GliderFileTools import *
import datetime
import pytz

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

surf_if_no_comms_for_8_hrs = SurfaceGliderBehavior(start_when=gldrEnums.start_when_enums['BAW_NOCOMM_SECS'], \
                    end_action=gldrEnums.end_action_enums['WAIT_FOR_CTRL-C_OR_RESUME'], \
                    when_secs=(8*60*60) )

surf_at_every_wpt = SurfaceGliderBehavior(start_when=gldrEnums.start_when_enums['BAW_WHEN_HIT_WAYPOINT'], \
                    end_action=gldrEnums.end_action_enums['WAIT_FOR_CTRL-C_OR_RESUME'])

surf_every_3_hrs= SurfaceGliderBehavior(start_when=gldrEnums.start_when_enums['BAW_EVERY_SECS'], \
                    when_secs=(3*60*60) )

surf_for_science = SurfaceGliderBehavior(start_when=gldrEnums.start_when_enums['BAW_SCI_SURFACE'], \
                    report_all=False, keystroke_wait_time=15 )

surf_when_mission_done = SurfaceGliderBehavior(start_when=gldrEnums.start_when_enums['BAW_HEADING_IDLE'], \
                    end_action=gldrEnums.end_action_enums['QUIT'], \
                    keystroke_wait_time=300)

# Now for the tricky one: UTC time
# Let us assume that we want to pick up the glider at 10:00 am PST on July 18, 2012
yy,mm,dd,hr,mi = 2013,8,19,10,30
tz1=pytz.timezone('US/Pacific')
temp_pickup_date=tz1.localize(datetime.datetime(yy,mm,dd,hr,mi))
pickup_date = temp_pickup_date.astimezone(tz1)
#pickup_date=datetime.datetime(yy,mm,dd,hr,mi,tzinfo=pytz.timezone('US/Pacific'))
pd_utc = pickup_date.astimezone(pytz.utc)
surf_when_utc = SurfaceGliderBehavior(start_when=gldrEnums.start_when_enums['BAW_WHEN_UTC_TIME'],
                when_utc_year=pd_utc.year, when_utc_month=pd_utc.month, when_utc_day=pd_utc.day,
                when_utc_hour=pd_utc.hour, when_utc_min=pd_utc.minute, when_utc_on_surface=True )

''' Add all the surfacing behaviors from above '''
gldr_beh_list.Append(surf_if_yo_complete)
gldr_beh_list.Append(surf_if_no_comms_for_8_hrs)
gldr_beh_list.Append(surf_at_every_wpt)
#gldr_beh_list.Append(surf_every_3_hrs)
gldr_beh_list.Append(surf_for_science)
gldr_beh_list.Append(surf_when_utc)
gldr_beh_list.Append(surf_when_mission_done)

''' Now for a Yo-behavior '''
yo_behavior = YoGliderBehavior(args_from_file=10, start_when=gldrEnums.start_when_enums['BAW_PITCH_IDLE'])
gldr_beh_list.Append(yo_behavior)

''' Goto-List behavior '''
goto_ll_behavior = GotoListGliderBehavior(args_from_file=96)
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
gldr_beh_list.SetSensorInitialization( u_use_current_correction=0, u_use_ctd_depth_for_flying=1 )
#gldr_beh_list.SetSensorInitialization(u_use_current_correction=0,m_water_vx=0.0,m_water_vy=0.0)


gldr_beh_list.SaveMissionFile('RECOVER.MI')
#today = datetime.datetime.utcnow()
#today_tz = today.replace(tzinfo=pytz.utc)

