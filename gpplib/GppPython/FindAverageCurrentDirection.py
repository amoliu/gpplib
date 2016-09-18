''' This program will find the average current direction between ranges of dates '''
import gpplib
from gpplib.GenGliderModelUsingRoms import GliderModel
from gpplib.InterpRoms import *
from gpplib.Utils import *

from matplotlib import pyplot as plt

#yy,mm,dd,numDays = 2013,8,12,22-12
yy,mm,dd,numDays = 2012,8,17,24-17
MaxDepth, MinDepth = 80., 0.

conf= gpplib.Utils.GppConfig()
#gm = GliderModel(conf.myDataDir+'RiskMap3.shelf', conf.myDataDir+'roms5')
gm = GliderModel(conf.myDataDir+'RiskMap3.shelf', conf.myDataDir+'roms')

gm.GetRomsData(yy,mm,dd,numDays)

# Compute the average currents
d1,d2 = FindLowAndHighIndices(MaxDepth,gm.depth)
d0,d1 = FindLowAndHighIndices(MinDepth,gm.depth)

u2,v2 = gm.u[:,d0:d2,:,:], gm.v[:,d0:d2,:,:]

print 'Averaging depths between indices %d and %d.'%(d0,d2)
u2ma,v2ma = np.ma.masked_array(u2,np.isnan(u2)),np.ma.masked_array(v2,np.isnan(v2))
dAvgU,dAvgV = u2ma.mean(axis=1).filled(np.nan),v2ma.mean(axis=1).filled(np.nan)


dAvgMag=np.sqrt(dAvgU**2+dAvgV**2)
dAvgDir=np.arctan2(dAvgV,dAvgU)*180/np.pi
plt.figure()
ax = plt.gca();
plt.hist(dAvgMag[np.isfinite(dAvgMag)].flatten(),bins=50,normed=True)
plt.title('Histogram of the current magnitudes between %04d-%02d-%02d-%02d'%(yy,mm,dd,dd+numDays),fontsize='large')
plt.xlabel('velocity m/s',fontsize='large')

plt.figure()
plt.hist(dAvgDir[np.isfinite(dAvgDir)].flatten(),bins=50,normed=True)
plt.title('Histogram of the current directions between %04d-%02d-%02d-%02d'%(yy,mm,dd,dd+numDays),fontsize='large')
plt.xlabel('degree',fontsize='large')

median_current_dir = np.median(dAvgDir[np.isfinite(dAvgDir)].flatten())
print 'Median Current Direction is: %.2f degrees'%(median_current_dir)

mean_current_dir = np.mean( dAvgDir[np.isfinite(dAvgDir)].flatten())
print 'Mean Current Direction is: %.2f degrees'%(mean_current_dir)

median_current_mag = np.median(dAvgMag[np.isfinite(dAvgMag)].flatten())
print 'Median Current Magnitude is: %.2f m/s'%(median_current_mag)
