import sys
import gpplib
from gpplib.Replanner import *
from gpplib.Utils import RomsTimeConversion
import datetime

conf = gpplib.Utils.GppConfig()
rtc  = RomsTimeConversion()

yy,mm,dd,numDays = 2012,9,17,2
nHrsHence = 0.0 # How many hours ahead or behind we want to plot these currents.
rp = Replanner(conf.myDataDir+'RiskMap.shelf',conf.myDataDir+'roms/')
rp.gm.gVel = 0.3
u,v,time1,depth,lat,lon = rp.gm.GetRomsData(yy,mm,dd,numDays,True,True)
plt.figure(); #rp.gm.PlotNewRiskMapFig(); 
rp.gm.PlotCurrentField(rtc.GetRomsIndexNhoursFromNow(yy,mm,dd, nHrsHence))
timeOfPlottedCurrents=datetime.datetime.today()+datetime.timedelta(hours=nHrsHence)
plt.title('Roms currents %s PST'%(timeOfPlottedCurrents.strftime('%A %d/%m/%y %H:%M:%S')))
