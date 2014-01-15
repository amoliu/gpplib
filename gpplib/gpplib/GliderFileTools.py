'''
@author: Arvind Pereira
@summary: Utilities to read and write .mi and .ma files auto-magically!
'''
import gpplib.LatLonConversions
import re, os
import datetime
import pytz

from gpplib.GliderBehaviors import *

# Some documentation on b_args common to all GliderBehaviors
# NOTE: When you add these common b_args, put them at END of b_arg
#       list for GliderBehaviors.  They do not "naturally" belong there, but
#       it means you do not have to edit GliderBehaviors which typically have
#       hardwired b_arg positions in them

# NOTE: These are symbolically defined beh_args.h
# b_arg: START_WHEN     When the GliderBehavior should start, i.e. go from UNITIALIZED to ACTIVE
#    BAW_IMMEDIATELY    0   // immediately
#    BAW_STK_IDLE       1   // When stack is idle (nothing is being commanded)
#    BAW_PITCH_IDLE     2   // When pitch is idle(nothing is being commanded)
#    BAW_HEADING_IDLE   3   // When heading is idle(nothing is being commanded)
#    BAW_UPDWN_IDLE     4   // When bpump/threng is idle(nothing is being commanded)
#    BAW_NEVER          5   // Never stop
#    BAW_WHEN_SECS      6   // After GliderBehavior arg "when_secs", from prior END if cycling
#    BAW_WHEN_WPT_DIST  7   // When sensor(m_dist_to_wpt) < GliderBehavior arg "when_wpt_dist"
#    BAW_WHEN_HIT_WAYPOINT 8 // When X_HIT_A_WAYPOINT is set by goto_wpt GliderBehavior
#    BAW_EVERY_SECS     9   // After GliderBehavior arg "when_secs", from prior START if cycling
#    BAW_EVERY_SECS_UPDWN_IDLE 10  // After GliderBehavior arg "when_secs", from prior START AND
#                                  //       updown is idle, no one commanding vertical motion
#    BAW_SCI_SURFACE    11  // SCI_WANTS_SURFACE is non-zero
#    BAW_NOCOMM_SECS    12  // when have not had comms for WHEN_SECS secs
#    BAW_WHEN_UTC_TIME  13  // At a specific UTC time or UTC minute into the hour
#
# b_arg: STOP_WHEN
#   0   complete
#   1-N same as "start_when"

#start_when_enums = {'0':'BAW_IMMEDIATELY', '1':'BAW_STK_IDLE', '2':'BAW_PITCH_IDLE', 
#                    '3':'BAW_HEADING_IDLE', '4':'BAW_UPDWN_IDLE', '5':'BAW_NEVER', 
#                    '6':'BAW_WHEN_SECS', '7':'BAW_WHEN_WPT_DIST','8':'BAW_WHEN_HIT_WAYPOINT', 
#                    '9':'BAW_EVERY_SECS', '10':'BAW_EVERY_SECS_UPDWN_IDLE',
#                    '11':'BAW_SCI_SURFACE', '12':'BAW_NOCOMM_SECS', '13':'BAW_WHEN_UTC_TIME' }

      

def LoadMissionFile(fileName):
    '''
    @summary:  Load a Mission File.
    @params: fileName - string. Path + name of the mission file
    @return: GliderBehavior list. A list which contains all the GliderBehaviors found.
    '''
    fin = open(fileName,'r')
    lines = fin.readlines()
    
    beh_abend={}
    beh_surface={}
    beh_goto_list={}
    beh_yo={}
    beh_sample = {}
    beh_prepare_to_dive = {}
    beh_sensors_in = {}
  
    GliderBehavior_list = []  
    adding_beh = 0
    adding_bargs = 0
    new_beh = GliderBehavior()
    new_beh.SetBehName('Starting')
    # Parse the file
    for line in lines:
        m_beh = re.match('\s*behavior\s*:\s*([a-zA-Z\_0-9]+)\s*#*\s*([\s\w]*)', line)
        if m_beh:
            if(new_beh.behavior != 'Starting'):
                 GliderBehavior_list.append(new_beh)
            #print m_beh.group(1)
            new_beh = GliderBehavior()
            new_beh.SetBehName(m_beh.group(1))
        #m_barg = re.match('\s*b_arg\s*:\s*([\w\_]+)\(([\w]*)\)\s+([0-9\.\-]+)\s*#*([\s\w\_\^\-,]*)',line)
        m_barg = re.match('\s*b_arg\s*:\s*([\w\_]+)\(([\w]*)\)\s+([0-9\.\-]+)\s*#*([\s\w\^\-,\"\'\/<>\$\@]*)',line)
        if m_barg:
            #print '   b_arg='+m_barg.group(1)+', dim='+m_barg.group(2)+', arg='+m_barg.group(3)+', comments='+m_barg.group(4)
            new_beh.AddBehArg(m_barg.group(1), m_barg.group(2), m_barg.group(3), m_barg.group(4))
    if(new_beh.behavior != 'Starting'):
        GliderBehavior_list.append(new_beh)
    return GliderBehavior_list

def PrintGliderBehaviors(GliderBehavior_list):
    print 'Loaded GliderBehaviors from file are:'
    for beh in GliderBehavior_list:
        print beh.behavior
        for b_arg in beh.beh_args:
            print b_arg+'('+beh.beh_dims[b_arg]+') ='+beh.beh_vals[b_arg]+' # '+beh.beh_comments[b_arg]



def GetWptList(fileName):
    '''
    @summary:  GetWptList(fileName)
    @params: fileName - string. Path + name of the mission file
    @return: Waypoint list. A list which contains all the GliderBehaviors found.
    '''
    fin = open(fileName,'r')
    lines = fin.readlines()
    
    WptLatList, WptLonList = [], []
    # Parse the file
    for line in lines:
        m_wpt = re.match('\s*([\-0-9\.]+)\s+([\-0-9\.]+)\s*',line)
        if m_wpt:
            lon,lat = float(m_wpt.group(1)),float(m_wpt.group(2))
            WptLatList.append(lat)
            WptLonList.append(lon)
            print lat,lon
    
    return WptLatList,WptLonList


def GetYoFile(fileName):
    '''
    @summary: GetYoFile(fileName)
    @param: fileName(string) Path+name of the mission argument (ma) file
    @return: GliderBehavior list. A list which contains all the GliderBehaviors found.
    '''
    new_beh = GliderBehavior()
    new_beh.SetBehName('yo')

    fin  = open(fileName,'r')
    lines=fin.readlines()
    
    
    for line in lines:
        m_beh = re.match('\s*GliderBehavior_name\s*=\s*([a-zA-Z\_0-9]+)\s*#*\s*([\s\w]*)', line)
        if m_beh:
            if m_beh.group(1)!='yo':
                print 'Found an unusual GliderBehavior in Yo file.'
                raise BadGliderBehavior('%s'%(m_beh.group(1)),'Found an unusual GliderBehavior in Yo file')
            else:
                new_beh.SetBehName(m_beh.group(1))
        m_barg = re.match('\s*b_arg\s*:\s*([\w\_]+)\(([\w]*)\)\s+([0-9\.\-]+)\s*#*([\s\w\^\-,\"\'\/<>\$\@]*)',line)
        if m_barg:
            #print '   b_arg='+m_barg.group(1)+', dim='+m_barg.group(2)+', arg='+m_barg.group(3)+', comments='+m_barg.group(4)
            new_beh.AddBehArg(m_barg.group(1), m_barg.group(2), m_barg.group(3), m_barg.group(4))
        

    return new_beh

def GetGoto_Lfile(fileName):
    '''
    @summary: GetGoto_Lfile(fileName)
    @param: fileName(string) Path+name of the mission argument (ma) file
    @return: GliderBehavior list. A list which contains all the GliderBehaviors found.
             WptLatList - List latitudes of waypoints found in Webb coordinates
             WptLonList - List longitudes of waypoints found in Webb coordinates
    '''
    new_beh = GliderBehavior()
    new_beh.SetBehName('goto_list')
    
    fin  = open(fileName,'r')
    lines=fin.readlines()
    WptLatList, WptLonList = [], []    
    
    for line in lines:
        m_beh = re.match('\s*GliderBehavior_name\s*=\s*([a-zA-Z\_0-9]+)\s*#*\s*([\s\w]*)', line)
        if m_beh:
            if m_beh.group(1)!='goto_list':
                print 'Found an unusual GliderBehavior in Yo file.'
                raise BadGliderBehavior('%s'%(m_beh.group(1)),'Found an unusual GliderBehavior in Yo file')
            else:
                new_beh.SetBehName(m_beh.group(1))
        m_barg = re.match('\s*b_arg\s*:\s*([\w\_]+)\(([\w]*)\)\s+([0-9\.\-]+)\s*#*([\s\w\^\-,\"\'\/<>\$\@]*)',line)
        if m_barg:
            #print '   b_arg='+m_barg.group(1)+', dim='+m_barg.group(2)+', arg='+m_barg.group(3)+', comments='+m_barg.group(4)
            new_beh.AddBehArg(m_barg.group(1), m_barg.group(2), m_barg.group(3), m_barg.group(4))
        m_wpt = re.match('\s*([\-0-9\.]+)\s+([\-0-9\.]+)\s*',line)
        if m_wpt:
            lon,lat = float(m_wpt.group(1)),float(m_wpt.group(2))
            WptLatList.append(lat)
            WptLonList.append(lon)
            
    goto_beh = GotoListFromGotoLfileGliderBehavior()
    goto_beh.InitGotoListFromGeneralGliderBehavior(new_beh)
    goto_beh.SetWaypointListInWebbCoods(WptLatList, WptLonList)
    
    return goto_beh


def AutoGenerateMissionFileFromBehaviorList(behList,outFile,headerComments='# Auto-generated File. (c) Arvind Pereira.'):
    ''' Stores back a mission file from a list of GliderBehaviors '''
    f2 = open(outFile,'w')
    f2.write(headerComments)
    f2.write('\n\n')
    for beh in behList:
        f2.write(beh.GetBehaviorOutputString())
        f2.write('\n')
    f2.close()
    

def AutoGenerateGotoLLfile(goto_beh,LLfileNum,headerComments=None):
    ''' Stores a .ma file from a list of GliderBehaviors.
        Args: goto_beh(GliderBehavior) - the GliderBehavior we want for the goto_list
              LLfileNum(int) - output GOTO_LL file number. This should match up
                          with the file number that the glider uses.
    '''
    if headerComments == None:
        today = datetime.datetime.utcnow()
        today.replace(tzinfo=pytz.utc)
        headerComments = ' Auto-generated GOTO_L%02d.MA file, created by GPPLIB at %s  (c) Arvind Pereira.'%(LLfileNum,str(today))
    
    f2 = open('GOTO_L%02d.MA'%(LLfileNum),'w')
    f2.write('behavior_name=goto_list')
    f2.write('\n#')
    f2.write(headerComments)
    f2.write('\n\n')
    f2.write('<start:b_arg>\n')
    f2.write(goto_beh.GetBehaviorOutputString())
    f2.write('\n')
    f2.write('<end:b_arg>\n')
    f2.write('<start:waypoints>\n')
    for w_lon, w_lat in zip(goto_beh.WptLonList,goto_beh.WptLatList):
        f2.write('%.4f\t%.4f\n'%(w_lon,w_lat))
    f2.write('<end:waypoints>')
    f2.close()
    
    
def AutoGenerateYoFile( yo_beh, ToFileNum, headerComments=None ):
    ''' Stores a yoXY.ma file from a list of 
    '''
    if headerComments == None:
        today = datetime.datetime.utcnow()
        today.replace(tzinfo=pytz.utc)
        headerComments = ' Auto-generated YO%02d.MA file, created by GPPLIB at %s  (c) Arvind Pereira.'%(ToFileNum,str(today))
    
    f2 = open('YO%02d.MA'%(ToFileNum),'w')
    f2.write('behavior_name=yo\n')
    f2.write('\n#')
    f2.write(headerComments)
    f2.write('\n\n')
    f2.write('<start:b_arg>\n')
    f2.write(yo_beh.GetBehaviorOutputString())
    f2.write('\n')
    f2.write('<end:b_arg>\n\n')
    f2.close()

### Demo:
'''
MissionsDirectory = '/Users/arvind/Documents/data/20110810_GliderData/Rusalka_Flight/missions/'
MaFilesDirectory = '/Users/arvind/Documents/data/20110810_GliderData/Rusalka_Flight/mafiles/'
MissionFileName = 'ARV2RYAN.MI'   
GliderBehavior_list = LoadMissionFile(MissionsDirectory+MissionFileName)
for beh in GliderBehavior_list:
    if beh.GliderBehavior=='goto_list':
        WptLatList,WptLonList = GetWptList(MaFilesDirectory+'GOTO_L'+beh.beh_vals['args_from_file']+'.MA')
'''

