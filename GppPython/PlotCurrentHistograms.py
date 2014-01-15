import numpy as np
import scipy.io as sio
import shelve
import math
import gpplib
from gpplib.GenGliderModelUsingRoms import GliderModel
from gpplib.Utils import DateRange
import matplotlib.pyplot as plt
import pylab as P

yy,mm,dd,numDays = 2011,1,1,1

conf = gpplib.GppConfig()
gm = GliderModel(conf.myDataDir+'RiskMap.shelf',conf.romsDataDir)

u,v,time1,depth,lat,lon = gm.GetRomsData(yy,mm,dd,numDays)
u2ma,v2ma = np.ma.masked_array(u,np.isnan(u)),np.ma.masked_array(v,np.isnan(v))
s = np.sqrt(u2ma**2+v2ma**2)
tAvgS = s.mean(axis=0)
dtAvgS = tAvgS[0:100].mean(axis=0)
dtAvgS.filled(np.nan)
#n, bins, patches = P.hist(dtAvgS, 100, normed=1, histtype='stepfilled')
n, bins, patches = P.hist(dtAvgS, 100, normed=1, histtype='stepfilled')
P.setp(patches, 'facecolor', 'g', 'alpha', 0.75)
meanCur = dtAvgS.mean(axis=0).mean(axis=0)
print meanCur
plt.title('Histogram of ROMS currents on %04d-%02d-%02d.'%(yy,mm,dd))
plt.xlabel('Current Magnitudes m/sec')
plt.xlim((0.02,0.4))
plt.ylim((0,35))
plt.savefig('Hist_%04d%02d%02d.png'%(yy,mm,dd))
P.show()