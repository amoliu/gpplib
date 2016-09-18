import datetime
import pytz
import math

''' A few exceptions for when we have error conditions
'''
class GliderFileError(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(GliderFileError):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class DateError(GliderFileError):
    """ Exception raised for errors in the date.
    
    Attributes:
        expression -- Date expression in which the error occurred
        message -- explanation of the error
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
        
class BadBehavior(GliderFileError):
    """ Exception raised for errors in behavior.
    
    Attributes:
        expression -- Behavior expression in which the error occurred
        message -- explanation of the error
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
        
class BadSurfacingBehavior(GliderFileError):
    """ Exception raised for errors in behavior.
    
    Attributes:
        expression -- Behavior expression in which the error occurred
        message -- explanation of the error
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message




class GliderWhenEnums:
    def __init__(self):
        self.start_when_enums = { 'BAW_IMMEDIATELY':0, 'BAW_STK_IDLE':1, 'BAW_PITCH_IDLE':2, 
                            'BAW_HEADING_IDLE':3, 'BAW_UPDWN_IDLE':4, 'BAW_NEVER':5, 
                            'BAW_WHEN_SECS':6, 'BAW_WHEN_WPT_DIST':7, 'BAW_WHEN_HIT_WAYPOINT':8, 
                            'BAW_EVERY_SECS':9, 'BAW_EVERY_SECS_UPDWN_IDLE':10,
                            'BAW_SCI_SURFACE':11, 'BAW_NOCOMM_SECS':12, 'BAW_WHEN_UTC_TIME':13
                            }
        
        self.stop_when_enums = { 'BAW_COMPLETE': 0, 'BAW_STK_IDLE':1, 'BAW_PITCH_IDLE':2, 
                            'BAW_HEADING_IDLE':3, 'BAW_UPDWN_IDLE':4, 'BAW_NEVER':5, 
                            'BAW_WHEN_SECS':6, 'BAW_WHEN_WPT_DIST':7, 'BAW_WHEN_HIT_WAYPOINT':8, 
                            'BAW_EVERY_SECS':9, 'BAW_EVERY_SECS_UPDWN_IDLE':10,
                            'BAW_SCI_SURFACE':11, 'BAW_NOCOMM_SECS':12, 'BAW_WHEN_UTC_TIME':13
                           }
        
        self.start_when_enums_R = { '0':'BAW_IMMEDIATELY', '1':'BAW_STK_IDLE', '2':'BAW_PITCH_IDLE', 
                            '3':'BAW_HEADING_IDLE', '4':'BAW_UPDWN_IDLE', '5':'BAW_NEVER', 
                            '6':'BAW_WHEN_SECS', '7':'BAW_WHEN_WPT_DIST', '8':'BAW_WHEN_HIT_WAYPOINT', 
                            '9':'BAW_EVERY_SECS', '10':'BAW_EVERY_SECS_UPDWN_IDLE',
                            '11':'BAW_SCI_SURFACE', '12':'BAW_NOCOMM_SECS', '13':'BAW_WHEN_UTC_TIME'
                            }
        
        self.stop_when_enums_R = { '0':'BAW_COMPLETE', '1':'BAW_STK_IDLE', '2':'BAW_PITCH_IDLE', 
                            '3':'BAW_HEADING_IDLE', '4':'BAW_UPDWN_IDLE', '5':'BAW_NEVER', 
                            '6':'BAW_WHEN_SECS', '7':'BAW_WHEN_WPT_DIST', '8':'BAW_WHEN_HIT_WAYPOINT', 
                            '9':'BAW_EVERY_SECS', '10':'BAW_EVERY_SECS_UPDWN_IDLE',
                            '11':'BAW_SCI_SURFACE', '12':'BAW_NOCOMM_SECS', '13':'BAW_WHEN_UTC_TIME'
                           }
        self.end_action_enums = { 'QUIT':0, 'WAIT_FOR_CTRL-C_OR_RESUME':1, 'RESUME':2 }
        self.end_action_enums_R = { '0':'QUIT', '1':'WAIT_FOR_CTRL-C_OR_RESUME', '2':'RESUME'}
        
        self.initial_wpt_enums = { 'CLOSEST':-2, 'ONE_AFTER_LAST_WPT_ACHIEVED':-1 }
        
        self.initial_wpt_enums_R = { '-2':'CLOSEST', '-1':'ONE_AFTER_LAST_WPT_ACHIEVED' }
        
        self.num_legs_to_run_enums = { 'TRAVERSE_LIST_ONCE':-2, 'LOOP_FOREVER':-1, 'ILLEGAL':0, 'EXACTLY_THIS_MANY_WPTS':'1-N' }
        self.num_legs_to_run_enums_R = { '-2':'TRAVERSE_LIST_ONCE', '-1':'LOOP_FOREVER', '0':'ILLEGAL' }
        
        self.force_iridium_use_enums = { 'DO_NOT_FORCE_IRIDIUM_USE':0, 'FORCE_IRIDIUM_USE':1 }
        self.force_iridium_use_enums_R = { '0':'DO_NOT_FORCE_IRIDIUM_USE', '1':'FORCE_IRIDIUM_USE' }
        
        self.use_pitch_enums = { 'BATTPOS':1, 'SETONCE':2, 'SERVO':3 }
        self.use_pitch_enums_R = { '1':'BATTPOS', '2':'SETONCE', '3':'SERVO' }
        
        self.use_current_correction = { 'CALCULATE_BUT_DONT_USE_M_WATER_VX/Y':0, 'USE_M_WATER_VX/Y_TO_NAVIGATE_AND_AIM':1 }
        self.use_current_correction_R = { '0':'CALCULATE_BUT_DONT_USE_M_WATER_VX/Y', '1':'USE_M_WATER_VX/Y_TO_NAVIGATE_AND_AIM' }

        self.c_console_on_enums = {'POWER_CONSOLE_OFF':0, 'AUTO_ON_AUTO_OFF_UW_NOCD':1, 'ALWAYS_ON':2 }
        self.c_console_on_enums_R = { '0':'POWER_CONSOLE_OFF', '1':'AUTO_ON_AUTO_OFF_UW_NOCD', '2':'ALWAYS_ON' }


class GliderBehaviorList(list):
    ''' This is a list of behaviors which typically makes up a mission file.
    '''
    def __init__(self,headerCommentUpdate=None):
        super(GliderBehaviorList,self).__init__()
        self.SensorInitializationList = GliderSensor()
        if (headerCommentUpdate!=None):
            self.headerComments = headerCommentUpdate
        else:
            self.headerComments =  '# Auto-generated Mission file for Slocum Gliders.'
        self.headerCommentBackup = self.headerComments
        
    def SetSensorInitialization(self,**kwargs):
        ''' Set the sensor initialization
        
            Comms related initialization:
            sensor: c_console_on(bool)              2.0  # in  0 power it off
                                             #     1 power on automatically at surface
                                             #       power off automatically when underwater AND
                                             #       no carrier for U_CONSOLE_REQD_CD_OFF_TIME secs
                                             #     2 power on regardless

            sensor: u_console_reqd_cd_off_time(sec)   15.0 # in, how long without CD before powering off
                                             #     modem if C_CONSOLE_ON == 1
            sensor: m_console_on(bool)              1.0  # out, power state of RF modem
            sensor: m_console_cd(bool)              1.0  # out, state of RF modem carrier detect

            sensor: u_console_off_if_mission_iridium(bool) 1.0 #! visible = True
                                             # in, if non-zero causes the freewave
                                             # to be powered off during a mission if a
                                             # carrier isn't detected.
        
        '''
        gldrEnums = GliderWhenEnums()
        if kwargs.has_key('u_use_current_correction'):
            u_use_current_corr = kwargs['u_use_current_correction']
            self.SensorInitializationList.AddOrUpdateSensorArg('u_use_current_correction', 'nodim', '%d'%(u_use_current_corr), '%s'%(gldrEnums.use_current_correction_R['%d'%(u_use_current_corr)]))
        if kwargs.has_key('u_use_ctd_depth_for_flying'):
            u_use_ctd_depth_for_flying = kwargs['u_use_ctd_depth_for_flying']
            self.SensorInitializationList.AddOrUpdateSensorArg('u_use_ctd_depth_for_flying', 'bool', '%d'%(u_use_ctd_depth_for_flying), '! visible = True, true=> use ctd measurement for m_depth. Use if ocean_pressure broken.')
        if kwargs.has_key('m_water_vx'):
            m_water_vx = kwargs['m_water_vx']
            self.SensorInitializationList.AddOrUpdateSensorArg('m_water_vx', 'm/s', '%.2f'%(m_water_vx), ' in/out. How fast the water is going. LMC coord.sys X-axis')
        if kwargs.has_key('m_water_vy'):
            m_water_vy = kwargs['m_water_vy']
            self.SensorInitializationList.AddOrUpdateSensorArg('m_water_vy', 'm/s', '%.2f'%(m_water_vy), ' in/out. How fast the water is going in LMC coord.sys Y-axis')
        if kwargs.has_key('x_prior_seg_water_vx'):
            x_prior_seg_water_vx = kwargs['x_prior_seg_water_vx']
            self.SensorInitializationList.AddOrUpdateSensorArg('x_prior_seg_water_vx', 'm/s', '%.2f'%(x_prior_seg_water_vx), ' in/out water speed used for navigation on prior segment')
        if kwargs.has_key('x_prior_seg_water_vy'):
            x_prior_seg_water_vy = kwargs['x_prior_seg_water_vy']
            self.SensorInitializationList.AddOrUpdateSensorArg('x_prior_seg_water_vy', 'm/s', '%.2f'%(x_prior_seg_water_vy), ' in/out water speed used for navigation on prior segment')
        if kwargs.has_key('c_console_on'):
            c_console_on = kwargs['c_console_on']
            if c_console_on<1 and c_console_on>2:
                print 'Ignoring c_console_on. Illegal value supplied.'%(c_console_on)
            else:
                self.SensorInitializationList.AddOrUpdateSensorArg('c_console_on', 'bool', '%d'%(c_console_on), \
                                    '%s'%(gldrEnums.c_console_on_enums_R['%d'%(c_console_on)]))
                if c_console_on ==1: # We need to also supply the u_console_reqd_cd_off_time
                    u_console_reqd_cd_off_time = kwargs['u_console_reqd_cd_off_time']
                    if u_console_reqd_cd_off_time<5:
                        u_console_reqd_cd_off_time = 15.0 # Wait 15 secs (some default value)
                    self.SensorInitializationList.AddOrUpdateSensorArg('u_console_reqd_cd_off_time', 'sec', '%.1f'%(u_console_reqd_cd_off_time), \
                        'in, how long without CD before powering off\n\t\t\t\t\t# modem if C_CONSOLE_ON == 1')
    
    def Append(self,beh):
        ''' Only allow Glider behaviors to be appended to this list.
        '''
        if isinstance(beh,GliderBehavior):
            self.append(beh)
        else:
            raise BadBehavior
    
    def GetFirstBehaviorWithOptionalArgValPair(self,behavior,beh_arg=None,beh_val=None):
        ''' Does a linear search through the list and finds a K-V pair that matches
        the behavior and beh_arg, beh_val provided.
        
            Args:
                behavior (str) : behavior name which you are looking for.
                beh_arg (str) : behavior argument which you are looking for.
                beh_val (str) : value for the beh_arg which you are looking for.
        '''
        for beh in self:
            if beh.behavior==behavior:
                if beh_arg==None: # you're probably not looking for a specific behavior;
                    return beh    # Here's is the first one I found.
                if beh.beh_args.has_key(beh_arg) and beh_val==None:
                    return beh
                if beh.beh_args.has_key(beh_arg) and beh.beh_vals.has_key(beh_val):
                    return beh
        # Didn't find anything that matched your description.
        return None
        
    def UpdateHeaderCommentsWithBehaviorListContents(self):
        ''' Perform self-introspection to find all the behaviors we contain and update our comments to reflect this.
        '''
        headerCommentStr = ''
        gldrEnums = GliderWhenEnums()
        
        

    def SaveMissionFile(self,outFile,headerComments=''):
        ''' Stores back a mission file from a list of GliderBehaviors '''
        if headerComments!='':
            self.headerComments = headerComments
            self.headerCommentBackup = self.headerComments
        
        self.headerComments+= ' Filename: %s\n'%(outFile)
        today = datetime.datetime.utcnow()
        today.replace(tzinfo=pytz.utc)
        self.headerComments+='# Created by GPPLIB at %s  (c) Arvind Pereira.'%(str(today))
        
        f2 = open(outFile,'w')
        f2.write(self.headerComments)
        f2.write('\n\n%s'%(self.SensorInitializationList.GetSensorOutputString()))
        f2.write('\n\n')
        for beh in self:
            f2.write(beh.GetBehaviorOutputString())
            f2.write('\n\n')
        f2.close()
        

class GliderBehavior(object):
    ''' Base class for glider behaviors. All the other behaviors are specializations of this type.
    '''
    def __init__(self):
        self.behavior = ''
        self.pre_behavior_comment =''
        self.beh_args = {}
        self.beh_dims = {}
        self.beh_vals = {}
        self.beh_comments = {}
        self.verbose = False
        
    def SetBehName(self,name):
        self.behavior = name
        
    def SetPreBehComment(self,comment):
        self.pre_behavior_comment = comment
        
    def AddBehArg(self,arg,dim,val,comments):
        self.beh_args[arg]=arg
        self.beh_dims[arg]=dim
        self.beh_vals[arg]=val
        self.beh_comments[arg]= comments
    
    def AddOrUpdateBehArg(self,arg,dim,val,comments):
        if self.beh_args.has_key(arg):
            self.beh_dims[arg]= dim
            self.beh_vals[arg]= val
            self.beh_comments[arg]= comments
        else:
            self.AddBehArg(arg, dim, val, comments)
            
    def GetBehaviorOutputString(self):
        outputStr ='# %s\n'%(self.pre_behavior_comment)
        outputStr += 'behavior: %s'%(self.behavior)
        for arg in self.beh_args.keys():
            outputStr+='\n\tb_arg: %s(%s) %s # %s'%(self.beh_args[arg],self.beh_dims[arg],self.beh_vals[arg],self.beh_comments[arg])
        if self.verbose:
            print outputStr
        
        return outputStr
    

class GliderSensor(object):
    ''' Base class for glider sensors inputs in mission files.
    '''
    def __init__(self):
        self.sensor = ''
        self.pre_sensor_comment =''
        self.sensor_args = {}
        self.sensor_dims = {}
        self.sensor_vals = {}
        self.sensor_comments = {}
        self.verbose = False
        self.is_empty = True
    
        
    def SetPreSensorComment(self,comment):
        self.pre_sensor_comment = comment
        
    def AddSensorArg(self,arg,dim,val,comments):
        self.sensor_args[arg]=arg
        self.sensor_dims[arg]=dim
        self.sensor_vals[arg]=val
        self.sensor_comments[arg]= comments
        self.is_empty = False
    
    def AddOrUpdateSensorArg(self,arg,dim,val,comments):
        if self.sensor_args.has_key(arg):
            self.sensor_dims[arg]= dim
            self.sensor_vals[arg]= val
            self.sensor_comments[arg]= comments
        else:
            self.AddSensorArg(arg, dim, val, comments)
        self.is_empty = False
            
    def GetSensorOutputString(self):
        if self.is_empty:
            outputStr=''
        else:
            outputStr ='# %s\n'%(self.pre_sensor_comment)
            for arg in self.sensor_args.keys():
                outputStr+='\nsensor: %s(%s) %s # %s'%(self.sensor_args[arg],self.sensor_dims[arg],self.sensor_vals[arg],self.sensor_comments[arg])
            if self.verbose:
                print outputStr
        return outputStr
    
    
''' Speciailzed instances of the GliderBehavior class '''

class YoGliderBehavior(GliderBehavior):    
    ''' GliderBehavior for doing the Yo-Yo's
    '''
    def __init__(self, **kwargs ):
        super(YoGliderBehavior,self).__init__()
        self.SetBehName('yo')
        gldrEnums = GliderWhenEnums()
        if kwargs.has_key('args_from_file'):
            self.AddOrUpdateBehArg('args_from_file', 'enum', '%d'%(kwargs['args_from_file']), 'read from mafiles/yo%02d.ma'%(kwargs['args_from_file']))
        else:
            self.AddBehArg('args_from_file','enum','10','read from mafiles/yo10.ma')
        
        if kwargs.has_key('start_when'):
            start_when=kwargs['start_when']
            if start_when<0 or start_when==3 or start_when>4: # Only [0, 1, 2, 4] are allowed
                start_when=gldrEnums.start_when_enums['BAW_PITCH_IDLE']
        else:
            start_when=gldrEnums.start_when_enums['BAW_PITCH_IDLE']
        self.AddBehArg('start_when', 'enum', '%d'%(start_when), '%s'%(gldrEnums.start_when_enums_R['%d'%(start_when)]))        
        
        if kwargs.has_key('end_action'):
            end_action=kwargs['end_action']
            if end_action!=0 and end_action!=2:
                end_action=gldrEnums.end_action_enums['RESUME']
        else:
            end_action=gldrEnums.end_action_enums['RESUME']
        self.AddOrUpdateBehArg('end_action', 'enum', '%d'%(end_action), '%s'%(gldrEnums.end_action_enums_R['%d'%(end_action)]))
    
 
class SampleGliderBehavior(GliderBehavior):
    ''' Sampling GliderBehavior '''
    def __init__(self,**kwargs):
        super(SampleGliderBehavior,self).__init__()
        self.SetBehName('sample')
        if kwargs.has_key('intersample_time'):
            intersample_time=kwargs['intersample_time']
        else:
            intersample_time = 0
        self.AddOrUpdateBehArg('intersample_time', 's', '%d'%(intersample_time), 'if < 0 then off, if =0 then full-speed.')
        if kwargs.has_key('state_to_sample'):
            state_to_sample=kwargs['state_to_sample']
        else:
            state_to_sample = 1
        self.AddOrUpdateBehArg('state_to_sample', 'enum', state_to_sample, ' 1 for diving, 4 climbing, 5 diving/climbing')
    
    
class AbortEndGliderBehavior(GliderBehavior):
    ''' These GliderBehaviors govern the abort and end mission parameters.
    GliderBehavior: abend
                                               # MS_ABORT_OVERDEPTH
    b_arg: overdepth(m)                10000.0 # <0 disables,
                                               # clipped to F_MAX_WORKING_DEPTH
    b_arg: overdepth_sample_time(sec)     15.0     #! simple=False
                                                   # how often to check

                                               # MS_ABORT_OVERTIME
    b_arg: overtime(sec)                  -1.0 # < 0 disables

                                               # MS_ABORT_UNDERVOLTS
    b_arg: undervolts(volts)              10.0 # < 0 disables
    b_arg: undervolts_sample_time(sec)    60.0     #! simple=False
                                                   # how often to check

                                               # MS_ABORT_SAMEDEPTH
    b_arg: samedepth_for(sec)             1800.0   #! simple=False
                                                   # <0 disables
    b_arg: samedepth_for_sample_time(sec)   30.0   #! simple=False
                                                   # how often to check

                                               # MS_ABORT_STALLED
    b_arg: stalled_for(sec)             1800.0     #! simple=False
                                                   # <0 disables
    b_arg: stalled_for_sample_time(sec) 1800.0     #! simple=False
                                                   # how often to check

                                               # MS_ABORT_NO_TICKLE
    b_arg: no_cop_tickle_for(sec)      48600.0     #! simple=False
                                                   # secs, abort mission if watchdog
                                               # not tickled this often, <0 disables
    b_arg: no_cop_tickle_percent(%)       -1.0     #! simple=False
                                                   # 0-100, <0 disables
                                               # Abort this % of time before
                                               # hardware, i.e. for 12.5%
                                               #  hardware 2hr   15min before
                                               #          16hr    2hr  before
            # Note: no_cop_tickle_percent only used on RevE boards or later
            # If non-zero and hardware supports COP timeout readback...
            #            causes no_cop_tickle_for(sec) to be IGNORED
            # On old boards, no_cop_tickle_percent(%) is IGNORED and
            #       control reverts to no_cop_tickle_for(sec)

                                             # MS_ABORT_ENG_PRESSURE, thermal only
    b_arg: eng_pressure_mul(nodim)      0.90       #! simple=False
                                                   # abort if M_THERMAL_ACC_PRES < 
                                             #   (eng_pressure_mul * F_THERMAL_REQD_ACC_PRES)

    b_arg: eng_pressure_sample_time(sec)  15.0     #! simple=False
                                                   # how often to measure, <0 disables

    b_arg: max_wpt_distance(m)          -1.0 # MS_ABORT_WPT_TOOFAR
                                             # Maximum allowable distance to a waypoint
                                             # < 0 disables

    b_arg: chk_sensor_reasonableness(bool) 1       #! simple=False
                                                   # MS_ABORT_UNREASONABLE_SETTINGS
                                             # 0 disables check

    b_arg: reqd_spare_heap(bytes)      50000       #! simple=False
                                                   # MS_ABORT_NO_HEAP if M_SPARE_HEAP is less than this
                                              # <0 disables check
                                              ####################################################
                                              # NOTE - VALUE OF REQD_SPARE_HEAP IN LASTGASP.MI
                                              # SHOULD BE MAINTAINED LOWER THAN THIS NUMBER SO
                                              # IF A MISSION ABORTS WITH MS_ABORT_NO_HEAP AND WE
                                              # SEQUENCE TO LASTGASP.MI, THAT IN TURN WILL NOT
                                              # ITSELF LIKEWISE DO A HEAP ABORT
                                              ####################################################

    b_arg: leakdetect_sample_time(sec)  60.0       #! simple=False
                                                   # MS_ABORT_LEAK, M_LEAK is non-zero
                                              # <0 disables check

    b_arg: vacuum_min(inHg)              4.0  # MS_ABORT_VACUUM, M_VACUUM out of limits
    b_arg: vacuum_max(inHg)             12.0
    b_arg: vacuum_sample_time(sec)     120.0  # <0 disables check
    b_arg: oil_volume_sample_time(sec) 180.0       #! simple=False
                                                   # how often to measure, <0 disables check
    b_arg: max_allowable_busy_cpu_cycles(cycles) 75 #! simple=False
                                                   # aborts if M_DEVICE_DRIVERS_CALLED_ABNORMALLY
                                                     # is true for this many cycles in a row
                                                     # <= 0 disables the abort, 75 = ~5min assuming
                                                     # a 4 second cycle time.

    b_arg: remaining_charge_min(%)             10.0  # MS_ABORT_CHARGE_MIN out of limits
    b_arg: remaining_charge_sample_time(sec) 60.0  #! simple=False
    '''
    def __init__(self,**kwargs):
        super(AbortEndGliderBehavior,self).__init__()
        self.SetBehName('abend')
        self.AddBehArg('overdepth_sample_time', 's', '40.0', 'how often to check.')
        self.AddBehArg('overtime', 's', '-1.0', '< 0 disables')
        self.AddBehArg('samedepth_for_sample_time', 's', '40.0', 'how often to check.')
        # Some more GliderBehaviors which are not always used.
        '''
        self.AddBehArg('overdepth','m','-1.0','<0 disables, clipped to F_MAX_WORKING_DEPTH')
        self.AddBehArg('undervolts', 'V', '-1.0', '<0 disables')
        self.AddBehArg('undervolts_sample_time', 's', '40.0', 'how often to check')
        self.AddBehArg('samedepth_for','s', '-1.0', '<0 disables')
        self.AddBehArg('samedepth_for_sample_time','s','40.0','how often to check')
        '''
        if kwargs.has_key('overdepth_sample_time'):
            SetOverDepthSampleTime(kwargs['overdepth_sample_time'])
        if kwargs.has_key('overtime'):
            SetOverTime(kwargs['overtime'])
        if kwargs.has_key('samedepth_for_sample_time'):
            SetSameDepthSampleTime(kwargs['samedepth_for_sample_time'])
        if kwargs.has_key('overdepth'):
            self.AddOrUpdateBehArg('overdepth', 'm', '%.1f'%(kwargs['overdepth']), '<0 disables, clipped to F_MAX_WORKING_DEPTH')
        if kwargs.has_key('undervolts'):
            self.AddOrUpdateBehArg('undervolts', 'V', '%.1f'%(kwargs['undervolts']), '<0 disables')        
        if kwargs.has_key('undervolts_sample_time'):
            self.AddOrUpdateBehArg('undervolts_sample_time','s','%.1f'%(kwargs['undervolts_sample_time']),'how often to check')
        if kwargs.has_key('samedepth_for'):
            self.AddOrUpdateBehArg('samedepth_for', 's', '%.1f'%(kwargs['same_depth_for']), '<0 disables')        
        
    def SetOverDepthSampleTime(self,sampleTime=40.0):
        self.AddOrUpdateBehArg('overdepth_sample_time', 's', '%.2f'%(sampleTime), 'how often to check.')
    
    def SetOvertime(self,overTime=-1.0):
        self.AddOrUpdateBehArg('overtime', 's', '%.1f'%(overTime), '<0 disables')

    def SetSameDepthSampleTime(self,sampleTime=40.0):
        self.AddOrUpdateBehArg('samedepth_for_sample_time', 's', '%.1f'%(sampleTime), 'how often to check.')
        
        
        
class SurfaceGliderBehavior(GliderBehavior):
    ''' All possible Surface GliderBehaviors
    GliderBehavior: surface
        b_arg: args_from_file(enum) -1   # >= 0 enables reading from mafiles/surfac<N>.ma
        b_arg: start_when(enum)     12   # See doco above
        b_arg: when_secs(sec)     1200   # How long between surfacing, only if start_when==6,9, or 12
        b_arg: when_wpt_dist(m)  10   # how close to waypoint before surface, only if start_when==7
        b_arg: end_action(enum) 1     # 0-quit, 1-wait for ^C quit/resume, 2-resume, 3-drift til "end_wpt_dist"
                                      # 4-wait for ^C once  5-wait for ^C quit on timeout
        b_arg: report_all(bool) 0     # T->report all sensors once, F->just gps
        b_arg: gps_wait_time(sec) 300 # how long to wait for gps
        b_arg: keystroke_wait_time(sec) 300   # how long to wait for control-C
        b_arg: end_wpt_dist(m) 0     # end_action == 3   ==> stop when m_dist_to_wpt > this arg
    
                                         # Arguments for climb_to when going to surface
        b_arg: c_use_bpump(enum)      2
        b_arg: c_bpump_value(X)  1000.0
        b_arg: c_use_pitch(enum)      3  # servo on pitch
        b_arg: c_pitch_value(X)  0.4363  # 25 degrees
    
        b_arg: printout_cycle_time(sec) 60.0 # How often to print dialog
    
                                       # iridium related stuff
        b_arg: gps_postfix_wait_time(sec) 60.0  # How long to wait after initial
                                                # gps fix before turning the iridium
                                                # on (which disables the gps).  It will
                                                # wait the shorter of this time or until
                                                # all the water velocity calculations are
                                                # complete.
    
        b_arg: force_iridium_use(nodim)  0.0 #  Only for test.  non-zero values are set
                                             # into C_IRIDIUM_ON.  Used to force the
                                             # use of the iridium even if freewave is
                                             # present.
    
        b_arg: min_time_between_gps_fixes(sec)  300.0 # The irdium will be hung up this often
                                         # to get gps fixes.  It will call back however.
                                         # Primarily for use in hold missions to get
                                         # periodic gps fixes to tell how far the glider
                                         # has drifted.
    
        b_arg: sensor_input_wait_time(sec)  10.0 # Time limit to wait for input sensors at surface.
    
                                           # For when_utc
        b_arg: when_utc_min(min)        -1 # 0-59, -1 any minute
        b_arg: when_utc_hour(hour)      -1 # 0-23, -1 any hour
        b_arg: when_utc_day(day)        -1 # 1-31, -1 any day
        b_arg: when_utc_month(month)    -1 # 1-12, -1 any month
        b_arg: when_utc_on_surface(bool) 0 # If true, adjust when_utc_month/day/hour/min 
                                           # to get glider on surface by this time. 
    
        b_arg: strobe_on(bool)         0  # GliderBehavior arguement to control the strobe light
    '''
    def __init__(self,**kwargs):
        super(SurfaceGliderBehavior,self).__init__()
        self.SetBehName('surface')
        self.AddBehArg('args_from_file', 'enum', 10, '>= 0 enables reading from mafiles/surfac<N>.ma')
        self.InitializeWithSurfaceType(**kwargs)
        '''
        self.AddBehArg('args_from_file', 'enum', -1, '>= 0 enables reading from mafiles/surfac<N>.ma')
        self.AddBehArg('start_when', 'enum', 12, 'See doco above')
        self.AddBehArg('when_secs', 'sec', 1200, 'How long between surfacing, only if start_when==6,9 or 12')
        self.AddBehArg('when_wpt_dist', 'm', 10, 'How close to waypoint before surface, only if start_when==7')
        self.AddBehArg('end_action', 'enum', 1, '0-quit, 1-wait for ^C quit/resume, 2-resume, 3-drift till "end_wpt_dist",\n\t\t\t# 4-wait for ^C once 5-wait for ^C quit on timeout')
        self.AddBehArg('report_all', 'bool', 0, 'T->report all sensors once, F->just gps')
        self.AddBehArg('gps_wait_time', 'sec', 300, 'How long to wait for GPS')
        self.AddBehArg('keystroke_wait_time', 'sec', 300, 'How long to wait for ^C')
        self.AddBehArg('end_wpt_dist', 'm', 0, 'end_action==3 ==> stop when m_dist_to_wpt > this arg')
        # Arguments for climb_to when going to the surface
        self.AddBehArg('c_use_bpump', 'enum', 2, 'Whether to use the Buoyancy pump during climb_to surface')
        self.AddBehArg('c_bpump_value', 'X', 1000.0, '')
        self.AddBehArg('c_use_pitch', 'enum', 3, 'servo on pitch')
        self.AddBehArg('c_pitch_value', 'X', 0.4363, '25 degrees in radians')
        self.AddBehArg('printout_cycle_time', 'sec', 60.0, 'How often to print dialog')
        # Iridium related stuff
        self.AddBehArg('gps_postfix_wait_time', 'sec', 60.0, \
            'How long to wait after initial\n\t\t\t# gps fix before turning the iridium on\n\t\t\t# (which disables the gps). Will wait the shorter of this\n\t\t\t# time or until all water velocity calculations are complete.')
        self.AddBehArg('force_iridium_use', 'nodim', 0.0, \
            'Used to force the use of the iridium even if freewave is present. Important - Always enable for communication testing missions.')
        self.AddBehArg('min_time_between_gps_fixes', 'sec', 300.0, \
            'The iridium will be hung up this often to get gps fixes.\n\t\t\t# It will call back however. Primarily for use in hold missions to get \n\t\t\t# periodic gps fixes to tell the glider how far it has drifted.')
        self.AddBehArg('sensor_input_wait_time', 'sec', 10.0, 'Time limit to wait for input sensors at surface.')
        self.AddOrUpdateBehArg('when_utc_min', 'min', -1, '0-59, -1 any minute')
        self.AddOrUpdateBehArg('when_utc_hour', 'hour', -1, '0-23, -1 any hour')
        self.AddOrUpdateBehArg('when_utc_day', 'day', -1, '1-31, -1 any day')
        self.AddOrUpdateBehArg('when_utc_month','month',-1,'1-12, -1 any month')
        self.AddOrUpdateBehArg('when_utc_on_surface', 'bool', 0, ' If true, adjust when_utc_month/day/hour/min to get glider on surface by this time.')
        self.AddBehArg('strobe_on', 'bool', 0, 'GliderBehavior argument to control the strobe light')
        '''
        
    def SetUtcSurfaceTimeWithValidation(self,enableUtcBeh,yy,mm,dd,hr,mi):
        ''' Enable UTC surface GliderBehavior.
        Please supply this function with the UTC date and time you want the glider
        to surface at. This is useful for recovery missions.
        
        '''
        if enableUtcBeh: # Do some date validation.
            try:
                utc_dt = datetime.datetime(yy,mm,dd,hr,mi,0)
            except ValueError:
                raise
            if utc_dt <= datetime.datetime.today():
                print 'It appears that you  are trying to use a date that is in the past. Are you sure about this?'
                raise
        else:
            yy, mm, dd, hr, mi = 0, -1, -1, -1, -1 # Disable UtcBeh.
            
        self.SetUtcSurfaceTimeWithoutValidation(enableUtcBeh, yy, mm, dd, hr, mi)
        
    def SetUtcSurfaceTimeWithoutValidation(self,enableUtcBeh,yy,mm,dd,hr,mi):
        ''' Enable UTC surface GliderBehavior.
        Please supply this function with the UTC date and time you want the glider
        to surface at. This is useful for recovery missions. We recommend using
        SetUtcSurfaceTimeWithValidation instead of this function to ensure that
        your UTC datetime is validated.
        
        This function will set these values directly.
        
        '''
        self.AddOrUpdateBehArg('when_utc_min', 'min', mi, '0-59, -1 any minute')
        self.AddOrUpdateBehArg('when_utc_hour', 'hour', hr, '0-23, -1 any hour')
        self.AddOrUpdateBehArg('when_utc_day', 'day', dd, '1-31, -1 any day')
        self.AddOrUpdateBehArg('when_utc_month','month',mm,'1-12, -1 any month')
        self.AddOrUpdateBehArg('when_utc_on_surface', 'bool', enableUtcBeh, ' If true, adjust when_utc_month/day/hour/min to get glider on surface by this time.')
        
    
    def InitializeWithSurfaceType(self, **kwargs ):
        ''' Initialize with surface type tells us what the surfacing type should be like.
        
        '''
        gldrEnums=GliderWhenEnums()
        end_action, gps_wait_time, keystroke_wait_time, force_iridium_use, report_all = \
           gldrEnums.end_action_enums['WAIT_FOR_CTRL-C_OR_RESUME'], 300, 300, \
           gldrEnums.force_iridium_use_enums['FORCE_IRIDIUM_USE'], False
        
        self.AddOrUpdateBehArg('end_action', 'enum', end_action, gldrEnums.end_action_enums_R['%d'%(end_action)])
        self.AddOrUpdateBehArg('gps_wait_time', 'sec', '%d'%(gps_wait_time), \
                                    'Wait %d secs at surface  for GPS'%(gps_wait_time))
        self.AddOrUpdateBehArg('keystroke_wait_time', 'sec', '%d'%(keystroke_wait_time), \
                                    'Wait %d secs at surface for keystroke'%(keystroke_wait_time))
        self.AddOrUpdateBehArg('force_iridium_use', 'nodim', '%d'%(force_iridium_use), \
                                   '%s'%(gldrEnums.force_iridium_use_enums_R['%d'%(force_iridium_use)]))
        self.AddOrUpdateBehArg('report_all', 'bool', '%d'%(report_all), 'T->report all sensors once, F->just GPS')
        
        when_utc_on_surface, when_utc_min, when_utc_hour, when_utc_day, when_utc_month, when_utc_year = \
                        None, None, None, None, None, None
        try:
            surfacingType = kwargs['start_when']
        except KeyError:
            raise
        
        if kwargs.has_key('args_from_file'):
            self.AddOrUpdateBehArg('args_from_file', 'enum', '%d'%(kwargs['args_from_file']), 'read from mafiles/surfac%02d.ma'%(kwargs['args_from_file']))
        
        if kwargs.has_key('end_action'):
            end_action = int(kwargs['end_action'])
            self.AddOrUpdateBehArg('end_action', 'enum', end_action, gldrEnums.end_action_enums_R['%d'%(end_action)])
            
        if kwargs.has_key('gps_wait_time'):
            gps_wait_time = int(kwargs['gps_wait_time'])
            self.AddOrUpdateBehArg('gps_wait_time', 'sec', '%d'%(kwargs['gps_wait_time']), \
                                    'Wait %d secs at surface  for GPS'%(kwargs['gps_wait_time']))
        
        if kwargs.has_key('keystroke_wait_time'):
            keystroke_wait_time = int(kwargs['keystroke_wait_time'])
            self.AddOrUpdateBehArg('keystroke_wait_time', 'sec', '%d'%(kwargs['keystroke_wait_time']), \
                                    'Wait %d secs at surface for keystroke'%(kwargs['keystroke_wait_time']))
        
        if kwargs.has_key('force_iridium_use'):
            force_iridium_use = kwargs['force_iridium_use']
            self.AddOrUpdateBehArg('force_iridium_use', 'nodim', kwargs['force_iridium_use'], \
                                   '%s'%(gldrEnums.force_iridium_use_enums_R['%d'%(force_iridium_use)]))
        
        if kwargs.has_key('report_all'):
            if(kwargs['report_all']):
                self.AddOrUpdateBehArg('report_all', 'bool', '%d'%(kwargs['report_all']), 'True-> report all sensors once')
            else:
                self.AddOrUpdateBehArg('report_all', 'bool', '%d'%(kwargs['report_all']), 'False-> report just GPS')
        try:
            if( surfacingType == gldrEnums.start_when_enums['BAW_PITCH_IDLE']):
                self.AddOrUpdateBehArg('start_when', 'enum', surfacingType, 'BAW_PITCH_IDLE')
                
                pre_comment = 'Come up briefly if "yo" finishes\n# This happens if a bad altimeter hit causes a dive and climb to\n# complete in same cycle. We surface and hopefully yo restarts'
                self.SetPreBehComment(pre_comment)
            elif( surfacingType == gldrEnums.start_when_enums['BAW_HEADING_IDLE']):
                self.AddOrUpdateBehArg('start_when', 'enum', surfacingType, 'BAW_HEADING_IDLE')
                # Default end_action = QUIT
                
                self.AddOrUpdateBehArg('end_action', 'enum', end_action, gldrEnums.end_action_enums_R['%d'%(end_action)])
                self.SetPreBehComment('Come up when mission done\n# This is determined by no one steering in x-y plane (no waypoints)')
            elif( surfacingType == gldrEnums.start_when_enums['BAW_NOCOMM_SECS']):
                when_secs = kwargs['when_secs']
                self.AddOrUpdateBehArg('when_secs', 'sec', '%d'%(when_secs), 'No-Comms limit is %d sec (or %.2f hours)'%(when_secs,when_secs/3600.))
                self.AddOrUpdateBehArg('start_when', 'enum', surfacingType, 'BAW_NOCOMM_SECS')
                self.SetPreBehComment('Come up if haven\'t had comms for more than %d seconds (or %.2f hours)'%(when_secs,when_secs/3600.))
            elif( surfacingType == gldrEnums.start_when_enums['BAW_WHEN_HIT_WAYPOINT']):
                self.AddOrUpdateBehArg('start_when', 'enum', surfacingType, 'BAW_WHEN_HIT_WAYPOINT')
                self.SetPreBehComment('Come up every way point')
                if kwargs.has_key('when_wpt_dist'):
                    self.AddOrUpdateBehArg('when_wpt_dist', 'm', '%d'%(when_wpt_dist), 'How close to waypoint before surfacing.')
                else:
                    self.AddOrUpdateBehArg('when_wpt_dist', 'm', '10', 'How close to waypoint before surfacing.')
            elif( surfacingType == gldrEnums.start_when_enums['BAW_SCI_SURFACE']):
                self.AddOrUpdateBehArg('start_when', 'enum', surfacingType, 'BAW_SCI_SURFACE')
                self.SetPreBehComment('Come up when requested by science')
            elif( surfacingType == gldrEnums.start_when_enums['BAW_EVERY_SECS']):
                when_secs = kwargs['when_secs']
                self.AddOrUpdateBehArg('when_secs', 'sec', '%d'%(when_secs), 'Come to the surface every %d sec (or %.2f hours)'%(when_secs,when_secs/3600.))
                self.AddOrUpdateBehArg('start_when', 'enum', surfacingType, 'BAW_EVERY_SECS')
                self.SetPreBehComment('Come up every N seconds')
            elif( surfacingType == gldrEnums.start_when_enums['BAW_WHEN_UTC_TIME']):
                if kwargs.has_key('when_utc_on_surface'):
                    when_utc_on_surface = (0,1)[kwargs['when_utc_on_surface']==True] # Force 0, 1
                else:
                    when_utc_on_surface = 1 # If we've specified a time, it makes sense to enable it, right?
                ''' Require that the user set all of the utc values, so don't test for has_key '''
                when_utc_year = kwargs['when_utc_year']
                when_utc_month = kwargs['when_utc_month']
                when_utc_day = kwargs['when_utc_day']
                when_utc_hour = kwargs['when_utc_hour']
                when_utc_min = kwargs['when_utc_min']                
                self.SetUtcSurfaceTimeWithValidation(when_utc_on_surface, when_utc_year, when_utc_month, \
                                                     when_utc_day, when_utc_hour, when_utc_min)
                self.AddOrUpdateBehArg('start_when', 'enum', surfacingType, 'BAW_WHEN_UTC_TIME')
                fmt = '%Y-%m-%d %H:%M:%S %Z%z'
                self.SetPreBehComment('Come up at UTC datetime: %04d-%02d-%02d, %02d:%02d'%(when_utc_year,when_utc_month, \
                                                                    when_utc_day, when_utc_hour, when_utc_min))
            else:
                print 'ILLEGAL SURFACING TYPE!'
                raise BadSurfacingBehavior(surfacingType,'ILLEGAL SURFACING TYPE!')
        except:
            raise
    
    
class PrepareToDiveGliderBehavior(GliderBehavior):
    ''' What to do when preparing to dive...
    '''
    
    def __init__(self,**kwargs):
        super(PrepareToDiveGliderBehavior,self).__init__()
        gldrEnums = GliderWhenEnums()
        self.SetBehName('prepare_to_dive')
        if kwargs.has_key('start_when'):
            start_when=kwargs['start_when']
            if start_when<0 or start_when>2:
                start_when=gldrEnums.start_when_enums['BAW_IMMEDIATELY']
        else:
            start_when=gldrEnums.start_when_enums['BAW_IMMEDIATELY']
        self.AddOrUpdateBehArg('start_when', 'enum', '%d'%(start_when), '%s'%(gldrEnums.start_when_enums_R['%d'%(start_when)]))
        if kwargs.has_key('wait_time'):
            wait_time = kwargs['wait_time']
        else:
            wait_time = 720
        self.AddOrUpdateBehArg('wait_time', 's', '%d'%(wait_time), 'Wait %d minutes for gps'%(int(wait_time/60)))
        
        

class InputSensorsGliderBehavior(GliderBehavior):
    ''' What the behavior for input sensors should be during this mission.
    '''
    def __init__(self,**kwargs):
        super(InputSensorsGliderBehavior,self).__init__()
        self.SetBehName('sensors_in')
        self.SetPreBehComment('Turn-most input sensors off')
        
        

class GotoListGliderBehavior(GliderBehavior):
    ''' GOTO_LIST GliderBehavior documentation from masterdata
    GliderBehavior: goto_list
    b_arg: args_from_file(enum) -1   # >= 0 enables reading from mafiles/goto_l<N>.ma
    b_arg: start_when(enum)      0   # See doco above

    b_arg: num_waypoints(nodim)  0   # Number of valid waypoints in list
                                     # maximum of 8 (this can be increased at compile-time)
    b_arg: num_legs_to_run(nodim) -1 # Number of waypoints to sequence thru
                                     #  1-N    exactly this many waypoints
                                     #  0      illegal
                                     # -1      loop forever
                                     # -2      traverse list once (stop at last in list)
                                     # <-2     illegal

    b_arg: initial_wpt(enum)      -2 # Which waypoint to head for first
                                     #  0 to N-1 the waypoint in the list
                                     # -1 ==> one after last one achieved
                                     # -2 ==> closest
    # Stopping condition applied to all of waypoints in the list
    b_arg: list_stop_when(enum)  7   # See doco above
    b_arg: list_when_wpt_dist(m) 10.  # used if list_stop_when == 7

    # When GliderBehavior is complete, either quit or stay active waiting for new mafile
    b_arg: end_action(enum)  0    # 0-quit, 6-wait for ^F (re-read mafiles)

    # The waypoints
    b_arg: wpt_units_0(enum) 0        # 0 LMC, 1 UTM, 2 LAT/LONG
    b_arg: wpt_x_0(X)        0        # The waypoint (east or lon)
    b_arg: wpt_y_0(X)        0        #              (north or lat)
    '''
    def __init__(self,**kwargs):
        super(GotoListGliderBehavior,self).__init__()
        self.SetBehName('goto_list')
        gldrEnums = GliderWhenEnums()
        '''
        self.AddBehArg('args_from_file', 'enum', -1, '>= 0 enables reading from mafiles/goto_l<N>.ma')
        self.AddBehArg('start_when', 'enum', 12, 'See doco above')
        self.AddBehArg('when_secs', 'sec', 1200, 'How long between surfacing, only if start_when==6,9 or 12')
        self.AddBehArg('when_wpt_dist', 'm', 10, 'How close to waypoint before surface, only if start_when==7')
        self.AddBehArg('end_action', 'enum', 1, '0-quit, 1-wait for ^C quit/resume, 2-resume, 3-drift till "end_wpt_dist",\n\t\t\t# 4-wait for ^C once 5-wait for ^C quit on timeout')
        self.AddBehArg('report_all', 'bool', 0, 'T->report all sensors once, F->just gps')
        self.AddBehArg('gps_wait_time', 'sec', 300, 'How long to wait for GPS')
        self.AddBehArg('keystroke_wait_time', 'sec', 300, 'How long to wait for ^C')
        self.AddBehArg('end_wpt_dist', 'm', 0, 'end_action==3 ==> stop when m_dist_to_wpt > this arg')
        '''
        if kwargs.has_key('args_from_file'):
            args_from_file = kwargs['args_from_file']
        else:
            args_from_file = 10
        self.AddOrUpdateBehArg('args_from_file', 'enum','%d'%(args_from_file), 'read waypoint list from mafiles/goto_l%02d.ma'%(args_from_file))
  
        start_when=0
        if kwargs.has_key('start_when'):
            start_when = kwargs['start_when']
            if start_when<0 or start_when>2:
                start_when = 0
        self.AddOrUpdateBehArg('start_when', 'enum', '%d'%(start_when), '%s'%(gldrEnums.start_when_enums_R['%d'%(start_when)]))
        


class GotoListFromGotoLfileGliderBehavior(GliderBehavior):
    ''' A class that holds the data from a goto-list file.
    Can also write out a goto list file.
   
    Here's the goto-list documentation from the Masterdata file:
    
    b_arg: args_from_file(enum) -1                 #! ignore=True
                                                   # >= 0 enables reading from mafiles/goto_l.ma
    b_arg: start_when(enum)      0   # See doco above

    b_arg: num_waypoints(nodim)  0                 #! min = 1; max = 8
                                                   # Number of valid waypoints in list
                                     # maximum of 8 (this can be increased at compile-time)
    b_arg: num_legs_to_run(nodim) -1               #! min = -2
                                                   # Number of waypoints to sequence thru:
                                     #  1-N    exactly this many waypoints
                                     #  0      illegal
                                     # -1      loop forever
                                     # -2      traverse list once (stop at last in list)
                                     # <-2     illegal

    b_arg: initial_wpt(enum)      -2               #! min = -2; max = 7
                                                   # Which waypoint to head for first
                                     #  0 to N-1 the waypoint in the list
                                     # -1 ==> one after last one achieved
                                     # -2 ==> closest


    # Stopping condition applied to all of waypoints in the list
    b_arg: list_stop_when(enum)  7                 #! choices = stop_when([1, 2, 5, 7])
                                                   # See doco above
    b_arg: list_when_wpt_dist(m) 10.               #! min = 10.0
                                                   # used if list_stop_when == 7

    # When GliderBehavior is complete, either quit or stay active waiting for new mafile
    b_arg: end_action(enum)  0                     #! choices = end_action([0, 6])
                                                   # 0-quit, 6-wait for ^F (re-read mafiles)

    '''
    def __init__(self):
        super(GotoListFromGotoLfileGliderBehavior,self).__init__()
        self.SetBehName('goto_list')
        self.WptLatList, self.WptLonList = [], []
        #import pdb; pdb.set_trace()
        self.AddOrUpdateBehArg('num_legs_to_run', 'nodim', '1', 'No. of wpts to seq. thru.\n\t\t\t# 1-N=>exactly this many, 0=>illegal, -1=>loop forever, \n\t\t\t# -2=>traverse list once (stop at last in list)')
        self.AddOrUpdateBehArg('start_when','enum','0',' See doco above')
        self.AddOrUpdateBehArg('num_waypoints', 'nodim', '0', 'min=1; max=8; No. of valid waypoints in list.')
        self.AddOrUpdateBehArg('initial_wpt', 'enum', '-2', 'min=-2,max=7,Which waypt to head for first(0..N-1)\n\t\t\t# -1=> one after last achieved, -2=> closest')
        self.AddOrUpdateBehArg('list_stop_when', 'enum', '7', ' 7=BAW_WHEN_WPT_DIST')

    def InitGotoListFromGeneralGliderBehavior(self,gen_beh, useMasterDataComments=True ):
        ''' This function allows us to specialize the General GliderBehavior as
        a GotoList (from within a GOTO_LXX.ma file) GliderBehavior.
        '''
        for arg in self.beh_args:
            if gen_beh.beh_args.has_key(arg):
                self.beh_vals[arg] = gen_beh.beh_vals[arg]
                if not useMasterDataComments:
                    self.beh_comments[arg] = gen_beh.beh_comments[arg]
        
    def ReUpdateWhenComments(self):
        gldrEnums=GliderWhenEnums()
        if self.beh_args.has_key('start_when'):
            self.beh_comments['start_when'] = gldrEnums.start_when_enums_R[self.beh_vals['start_when']]
        if self.beh_args.has_key('list_stop_when'):
            self.beh_comments['list_stop_when'] = gldrEnums.stop_when_enums_R[self.beh_vals['list_stop_when']]
        if self.beh_args.has_key('initial_wpt'):
            if gldrEnums.initial_wpt_enums_R.has_key(self.beh_vals['initial_wpt']):
                self.beh_comments['initial_wpt'] = gldrEnums.initial_wpt_enums_R[self.beh_vals['initial_wpt']]
        if self.beh_args.has_key('num_legs_to_run'):
            if gldrEnums.num_legs_to_run_enums_R.has_key(self.beh_vals['num_legs_to_run']):
                self.beh_comments['num_legs_to_run'] = gldrEnums.num_legs_to_run_enums_R[self.beh_vals['num_legs_to_run']]
        
    def SetWaypointListInWebbCoods(self,WptLatListInWebbCoods,WptLonListInWebbCoods,comments=''):
        '''    Set WaypointList in WebbCoods
        '''
        self.WptLatList, self.WptLonList = WptLatListInWebbCoods, WptLonListInWebbCoods
        self.AddOrUpdateBehArg('num_waypoints', 'nodim', '%d'%(len(WptLatListInWebbCoods)), comments)
        self.ReUpdateWhenComments()
    
    def GetBehaviorOutputString(self):
        outputStr = ''
        for arg in self.beh_args.keys():
            outputStr+='\n\tb_arg: %s(%s) %s # %s'%(self.beh_args[arg],self.beh_dims[arg],self.beh_vals[arg],self.beh_comments[arg])
        if self.verbose:
            print outputStr
        return outputStr
    
    def SetStartWhen(self,start_when):
        ''' Args:
                start_when (int) : start_when parameter for the start_when behavior.
                Options are: 0 - BAW_IMMEDIATELY, 
        '''
        gldrEnums=GliderWhenEnums()
        print 'Setting start_when to: %d which is %s'%(start_when,gldrEnums.start_when_enums_R['%d'%(start_when)])
        self.AddOrUpdateBehArg('start_when', 'enum', '%d'%(start_when),'')
        self.ReUpdateWhenComments()
        
    def SetStopWhen(self,list_stop_when):
        ''' Args:
                list_stop_when (int) : start_when parameter for the start_when behavior.
                Options are: 0 - BAW_IMMEDIATELY, 
        '''
        gldrEnums=GliderWhenEnums()
        print 'Setting list_stop_when to: %d which is %s'%(list_stop_when,gldrEnums.stop_when_enums_R['%d'%(list_stop_when)])
        self.AddOrUpdateBehArg('list_stop_when', 'nodim', '%d'%(list_stop_when),'')
        self.ReUpdateWhenComments()
        
    def SetNumLegsToRun(self,num_legs_to_run):
        gldrEnums=GliderWhenEnums()
        print 'Setting list_stop_when to: %d which is %s'%(num_legs_to_run,gldrEnums.num_legs_to_run_enums_R['%d'%(num_legs_to_run)])
        self.AddOrUpdateBehArg('num_legs_to_run', 'nodim', '%d'%(num_legs_to_run),'')
        self.ReUpdateWhenComments()

    def SetInitialWaypoint(self,initial_wpt):
        gldrEnums=GliderWhenEnums()
        print 'Setting initial_wpt to: %d which is %s'%(initial_wpt,gldrEnums.initial_wpt_enums_R['%d'%(initial_wpt)])
        self.AddOrUpdateBehArg('initial_wpt', 'nodim', '%d'%(initial_wpt),'')
        self.ReUpdateWhenComments()
        

class GotoWayPoint(GliderBehavior):
    '''
    GliderBehavior: goto_wpt                             #! visible = False
    b_arg: start_when(enum) 0                      #! choices=start_when([0, 1, 2, 4])
    b_arg: stop_when(enum)  2                      #! choices=stop_when([1, 2, 5, 7])

    b_arg: when_wpt_dist(m) 0                      #! min = 5.0
                                                   # stop_when == 7   ==> stop when m_dist_to_wpt < this arg

    b_arg: wpt_units(enum)  0                      #! choices=wpt_units
    b_arg: wpt_x(X)         0     # The waypoint (east or lon)
    b_arg: wpt_y(X)         0     #              (north or lat)
                                  # These only used for UTM waypoints
    b_arg: utm_zd(byte)   19.0   #     UTM Zone as digit (see coord_sys.h)
    b_arg: utm_zc(byte)   19.0   # (T) UTM Zone as char (see coord_sys.h)

    b_arg: end_action(enum) 0                      #! choices=end_action([0, 1, 2, 3, 4, 5])

    '''
    def __init__(self):
        super(GliderBehavior,self).__init__()
        self.SetBehName('goto_wpt')
        self.AddBehArg('start_when', 'enum', '0', 'choices=start_when([0, 1, 2, 4])')
        self.AddBehArg('stop_when', 'enum', '2', 'choices=stop_when([1, 2, 5, 7])')
        self.AddBehArg('when_wpt_dist', 'm', '0', 'min=5.0, stop_when == 7   ==> stop when m_dist_to_wpt < this arg')
        #self.AddBehArg('wpt_units', 'enum', '0', '! choices=wpt_units')
        #self.AddBehArg('wpt_x', 'X', '0', 'The waypoint (east or lon) UTM')
        #self.AddBehArg('wpt_y', 'X', '0', 'The waypoint (north or lat) UTM')
        self.AddBehArg('end_action', 'enum', '0', '! choices=end_action([0, 1, 2, 3, 4, 5])')



        

class YoFileGliderBehavior(GliderBehavior):
    '''
    GliderBehavior: yo
    b_arg: args_from_file(enum) -1                 #! ignore=True
                                                   # >= 0 enables reading from mafiles/yo.ma
    b_arg: start_when(enum)      2                 #! choices=start_when([0, 1, 2, 4])
    b_arg: start_diving(bool)    1   # T-> dive first, F->climb first
    b_arg: num_half_cycles_to_do(nodim) -1         #! min = -1
                                                   # Number of dive/climbs to perform
                                     # <0 is infinite, i.e. never finishes

    # arguments for dive_to
    b_arg: d_target_depth(m)     12                #! min = 3.0; max = 1000.0
    b_arg: d_target_altitude(m)   5                #! min = -1; max = 100.0
    b_arg: d_use_bpump(enum)      2                #! choices=use_bpump
    b_arg: d_bpump_value(X) -1000.0                #! min = -1000; max = 1000
    b_arg: d_use_pitch(enum)      3                #! choices=use_pitch 
    b_arg: d_pitch_value(X) -0.4538                #! min = -maxPitch; max = -minPitch
    b_arg: d_stop_when_hover_for(sec) 180.0        #! simple=False
    b_arg: d_stop_when_stalled_for(sec) 240.0      #! simple=False
    b_arg: d_speed_min(m/s)    -100.0                   #! simple = False; min = -100.0; max = 0.3
    b_arg: d_speed_max(m/s)    100.0                  #! simple = False; min = 0.05; max = 100.0
    b_arg: d_depth_rate_method(enum) 3             #! simple = False; choices = depth_rate_method
    b_arg: d_wait_for_pitch(bool) 1                #! simple = False
    b_arg: d_wait_for_ballast(sec) 100.0           #! simple = False
    b_arg: d_delta_bpump_speed(X) 50.0             #! simple = False; min = 10.0; max = 100.0
    b_arg: d_delta_bpump_ballast(X) 25.0           #! simple = False; min = 10.0; max = 100.0
    b_arg: d_time_ratio(X) 1.1                       #! simple = False; min = 0.0; max = 2.0
    b_arg: d_use_sc_model(bool)    0                  #! simple = False
   
    b_arg: d_max_thermal_charge_time(sec) 1200.0   #! simple = False
    b_arg: d_max_pumping_charge_time(sec) 300.0    #! simple = False
    b_arg: d_thr_reqd_pres_mul(nodim) 1.50         #! simple = False

    # arguments for climb_to
    b_arg: c_target_depth(m)      3                #! min = 3.0; max = 1000.0
    b_arg: c_target_altitude(m)  -1                #! simple = False
    b_arg: c_use_bpump(enum)      2                #! choices = use_bpump
    b_arg: c_bpump_value(X)  1000.0                #! min = -1000.0; max = 1000.0
    b_arg: c_use_pitch(enum)      3                #! choices = use_pitch
    b_arg: c_pitch_value(X)  0.4538                #! min = minPitch; max = maxPitch
    b_arg: c_stop_when_hover_for(sec) 180.0        #! simple=False
    b_arg: c_stop_when_stalled_for(sec) 240.0      #! simple=False
    b_arg: c_speed_min(m/s)    100.0              #! min = -0.3; max = 100.0
    b_arg: c_speed_max(m/s)    -100.0             #! min = -100.0; max = 0.05
    
    b_arg: end_action(enum)       2                #! choices = end_action([0, 2])
    '''
    def __init__(self,**kwargs):      
        super(YoFileGliderBehavior,self).__init__()
        gldrEnums = GliderWhenEnums()
        self.headerComments=''
        self.diveAngle, self.climbAngle = -26.0, 26.0
        self.d_target_depth, self.d_target_altitude = 90., 4.
        self.c_target_depth, self.c_target_altitude = 6., -1
        
        self.f_max_working_depth = 98.0
        self.f_max_inflection_depth = 30.0
        self.f_max_target_altitude = 100.0
        
        self.minPitchAngle, self.maxPitchAngle = -35., 35.
        self.minDiveAngle,self.maxDiveAngle = -self.maxPitchAngle, -self.minPitchAngle
        self.minClimbAngle, self.maxClimbAngle = self.minPitchAngle, self.maxPitchAngle
        
        self.SetBehName('yo')
        self.start_when = gldrEnums.start_when_enums['BAW_PITCH_IDLE']
        self.AddBehArg('start_when', 'enum', '%d'%(self.start_when), '%s'%(gldrEnums.start_when_enums_R['%d'%(self.start_when)]))
        self.AddBehArg('num_half_cycles_to_do', 'nodim', '-1', 'Number of dive/climbs to perform\n\t\t\t\t\t# <0 is infinite, i.e. never finishes')
        # Arguments for Dive To
        self.AddBehArg('d_target_depth', 'm', '%d'%(self.d_target_depth), 'Depth to aim for. (98m max for shallow water glider)')
        self.AddBehArg('d_target_altitude', 'm', '%d'%(self.d_target_altitude), 'Altitude to aim for. (How much higher above the bottom.)')
        self.AddBehArg('d_use_pitch', 'enum', '%d'%(gldrEnums.use_pitch_enums['SERVO']), ' 1:battpos  2:setonce  3:servo')
        self.AddBehArg('d_pitch_value', 'X', '%.4f'%(self.diveAngle*math.pi/180.), 'Dive Angle: %f deg'%(self.diveAngle))
        # Arguments for Climb To
        self.AddBehArg('c_target_depth', 'm', '%d'%(self.c_target_depth), 'Depth to aim for. (98m max for shallow water glider)')
        self.AddBehArg('c_target_altitude', 'm', '%d'%(self.c_target_altitude), 'Altitude to aim for. (when climbing we are usually aiming for -1)')
        self.AddBehArg('c_use_pitch', 'enum', '%d'%(gldrEnums.use_pitch_enums['SERVO']), ' 1:battpos  2:setonce  3:servo')
        self.AddBehArg('c_pitch_value', 'X', '%.4f'%(self.climbAngle*math.pi/180.), 'Climb Angle: %f deg'%(self.climbAngle))
        self.AddBehArg('end_action', 'enum', '%d'%(gldrEnums.end_action_enums['RESUME']), ' 0-quit, 2 resume')
        self.InitializeWithYoType(**kwargs)
        
    def InitializeWithYoType(self,**kwargs):
        gldrEnums = GliderWhenEnums()
        if kwargs.has_key('args_from_file'):
            args_from_file = kwargs['args_from_file']
            self.AddOrUpdateBehArg('args_from_file', 'enum', '%d'%(args_from_file), '>= 0 enables reading from mafiles/yo<N>.ma')
        
        if kwargs.has_key('d_target_depth'):
            d_target_depth = kwargs['d_target_depth']
            self.SetTargetDepthForDive(d_target_depth)
        
        if kwargs.has_key('d_target_altitude'):
            d_target_altitude = kwargs['d_target_altitude']
            self.SetTargetAltitudeForDive(d_target_altitude)
            
        if kwargs.has_key('c_target_depth'):
            c_target_depth = kwargs['c_target_depth']
            self.SetTargetAltitudeForClimb(c_target_depth)
        
        if kwargs.has_key('c_target_altitude'):
            c_target_altitude = kwargs['c_target_altitude']
            self.SetTargetAltitudeForClimb(c_target_altitude)
        
        if kwargs.has_key('d_pitch_value'):
            d_pitch_value = kwargs['d_pitch_value']
            diveAngle = d_pitch_value*180./math.pi
            self.SetDiveAngleToXdegrees(diveAngle)
                
        if kwargs.has_key('c_pitch_value'):
            c_pitch_value = kwargs['c_pitch_value']
            climbAngle = c_pitch_value*180./math.pi
            self.SetClimbAngleToXdegrees(climbAngle)
            
    def SetTargetDepthForDive(self,d_target_depth):
        if d_target_depth>=self.f_max_working_depth:
                d_target_depth = self.f_max_working_depth
        self.d_target_depth = d_target_depth
        self.AddOrUpdateBehArg('d_target_depth', 'm', '%d'%(d_target_depth), 'Depth to aim for. (98m max for shallow water glider)')
            
    def SetTargetAltitudeForDive(self,d_target_altitude):
        if d_target_altitude>=self.f_max_target_altitude:
                d_target_altitude = self.f_max_target_altitude
        self.d_target_altitude = d_target_altitude
        self.AddOrUpdateBehArg('d_target_altitude', 'm', '%d'%(d_target_altitude), \
                                   'Altitude to aim for. (How much higher above the bottom.)')
            
    def SetTargetDepthForClimb(self,c_target_depth):
        if c_target_depth>=self.f_max_inflection_depth:
            c_target_depth = self.f_max_inflection_depth
        self.c_target_depth = c_target_depth
        self.AddOrUpdateBehArg('c_target_depth', 'm', '%d'%(c_target_depth), \
                'Depth to aim for when at the top of the Yo. (30m max for shallow water glider)')     
        
    def SetTargetAltitudeForClimb(self,c_target_altitude):
        self.c_target_altitude = c_target_altitude
        self.AddOrUpdateBehArg('c_target_altitude', 'm', '%d'%(c_target_altitude), \
                        'Altitude to aim for. Usually -1 so we are aiming to get above water.')    
    
    def SetClimbAngleToXdegrees(self,climbAngle):
        if self.minClimbAngle< climbAngle< self.maxClimbAngle:
            self.climbAngle = climbAngle
            self.AddBehArg('c_pitch_value', 'X', '%.4f'%(self.climbAngle*math.pi/180.), \
                           'Climb Angle: %f deg'%(self.climbAngle))
        else:
            print 'Validation failed for climbAngle=%.2f deg. Valid range=(%.2f,%.2f)' \
                %(climbAngle,self.minClimbAngle,self.maxClimbAngle)
    
    def SetDiveAngleToXdegrees(self,diveAngle):
        if self.minDiveAngle<= diveAngle<= self.maxDiveAngle:
                self.diveAngle = diveAngle
                self.AddBehArg('d_pitch_value', 'X', '%.4f'%(self.diveAngle*math.pi/180.), \
                               'Dive Angle: %f deg'%(self.diveAngle))
        else:
            print 'Validation failed for diveAngle=%.2f deg. Valid range=(%.2f,%.2f)' \
                %(diveAngle,self.minDiveAngle,self.maxDiveAngle)
    
    def ConvertToStayDeepYo(self):
        ''' Need to set this parameter to ensure that this is a deep-dive yo-file.
            When the glider is climbing, it will not start deflecting downward
            as soon as it hits this depth.
        '''
        self.SetTargetDepthForClimb(25)
        
    
    def GetBehaviorOutputString(self):
        outputStr = ''
        for arg in self.beh_args.keys():
            outputStr+='\n\tb_arg: %s(%s) %s # %s'%(self.beh_args[arg],self.beh_dims[arg],self.beh_vals[arg],self.beh_comments[arg])
        if self.verbose:
            print outputStr
        return outputStr     
                
