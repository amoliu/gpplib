'''
 This file tests the GOTO_LXY.MA file creation aspects of GliderFileTools
'''
from gpplib.GliderFileTools import *
import random
from sets import Set
import gpplib
from gpplib.Utils import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.SA_Replanner import *
from gpplib.LatLonConversions import *

''' Come up with a sample plan... '''
conf = gpplib.Utils.GppConfig()

''' Code to write out a goto_lXY.ma file. Here we are going to write out to GOTO_L16.MA
'''
# Create our own .MA file from scratch.
new_yo_beh = YoGliderBehavior()
gldrEnums=GliderWhenEnums()
#new_yo_beh.ConvertToStayDeepYo()
AutoGenerateYoFile(new_yo_beh,11)

''' Might want to go to http://cinaps.usc.edu/gliders/waypoints.php to test the output GOTO_L16.MA file.
'''