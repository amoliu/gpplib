''' Simple script that generates figures with the ROMS currents plotted overlaid on the map such that we 
see the errors between successive predictions '''
import sys
import gpplib
from gpplib.Replanner import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.Utils import RomsTimeConversion
import datetime
from gpplib.Utils import DateRange
import os


plotsDir = 'current_plots'
try:
    os.mkdir(plotsDir)
except:
    pass


def PlotCurrentsForDayAndHour(yy,mm,dd,hr):
    conf=gpplib.Utils.GppConfig()
    rtc = RomsTimeConversion()
    gm1 = GliderModel(conf.myDataDir+'RiskMap3.shelf',conf.myDataDir+'roms/'); gm1.gVel = 0.18; gm1.depth=90.
    gm2 = GliderModel(conf.myDataDir+'RiskMap3.shelf',conf.myDataDir+'roms/'); gm2.gVel = 0.18; gm2.depth=90.
    gm3 = GliderModel(conf.myDataDir+'RiskMap3.shelf',conf.myDataDir+'roms/'); gm3.gVel = 0.18; gm3.depth=90.
    
    
    dt1 = datetime.datetime(yy,mm,dd,hr,0) - datetime.timedelta(hours=48); yy1,mm1,dd1,hr1 = dt1.year,dt1.month,dt1.day,dt1.hour
    dt2 = datetime.datetime(yy,mm,dd,hr,0) - datetime.timedelta(hours=24); yy2,mm2,dd2,hr2 = dt2.year,dt2.month,dt2.day,dt2.hour
    dt3 = datetime.datetime(yy,mm,dd,hr,0)
    
    plt.figure(); gm1.PlotNewRiskMapFig()
    u,v,time1,depth,lat,lon = gm1.GetRomsData(yy1,mm1,dd1,3,True,True)
    u,v,time1,depth,lat,lon = gm2.GetRomsData(yy2,mm2,dd2,3,True,True)
    u,v,time1,depth,lat,lon = gm3.GetRomsData(yy,mm,dd,3,True,True)

    # Find the same time in all three data files and index into it.
    gm1.PlotCurrentField(rtc.GetRomsIndexFromDateTime(yy1,mm1,dd1,dt3),arrow_color='y')
    gm2.PlotCurrentField(rtc.GetRomsIndexFromDateTime(yy2,mm2,dd2,dt3),arrow_color='r')
    gm3.PlotCurrentField(rtc.GetRomsIndexFromDateTime(yy,mm,dd,dt3),arrow_color='k')


yy,mm,dd,numDays = 2012,7,30,2
nHrsHence = 12 # How many hours ahead or behind we want to plot these currents.
PlotCurrentsForDayAndHour(yy,mm,dd,nHrsHence)
timeOfPlottedCurrents = datetime.datetime(yy,mm,dd,nHrsHence,0)
plt.title('Roms currents %s PST'%(timeOfPlottedCurrents.strftime('%A %Y-%m-%d %H:%M:%S')))
plt.savefig('%s/RomsCurrents_%s.png'%(plotsDir,timeOfPlottedCurrents.strftime('%H:%M:%S_%Y-%m-%d')))
