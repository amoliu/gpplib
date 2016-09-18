'''
 This file tests the Mission file reading aspects of GliderFileTools
'''
from gpplib.GliderFileTools import *
import random
from sets import Set
import gpplib
from gpplib.Utils import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.SA_Replanner import *
from gpplib.LatLonConversions import *

MaFilesDir = 'mafiles/'
MissionFilesDir = 'missions/'
TestMissionFile = 'GUMSTX1.MI'

''' Test reading a mission file and also find the waypoints included in it '''
goto_beh,WptLatList,WptLonList = None,[],[]
Behavior_list = LoadMissionFile(MissionFilesDir+TestMissionFile)
for beh in Behavior_list:
    print beh.GetBehaviorOutputString()
    if beh.behavior=='goto_list':
        print
        print '---------Goto_L file behaviors: Called file=GOTO_L'+beh.beh_vals['args_from_file']+'.MA -----'
        goto_beh = GetGoto_Lfile(MaFilesDir+'GOTO_L'+beh.beh_vals['args_from_file']+'.MA')
        print goto_beh.GetBehaviorOutputString()
        print '------- Waypoint List ----------'
        print zip(goto_beh.WptLatList, goto_beh.WptLonList)
        print '--------------------------------'
        print

    if beh.behavior=='yo':
        print
        print '---------Yo-file behaviors: Called file=YO'+beh.beh_vals['args_from_file']+'.MA -----'
        yo_beh = GetYoFile(MaFilesDir+'YO'+beh.beh_vals['args_from_file']+'.MA')
        print yo_beh.GetBehaviorOutputString()
        print '--------------------------------'


AutoGenerateMissionFileFromBehaviorList(Behavior_list,'Test.MI')
AutoGenerateGotoLLfile(goto_beh,15)
