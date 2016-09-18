from gpplib.GenGliderModelUsingRoms import GliderModel
from matplotlib import pyplot as plt
from matplotlib import mlab as mlab
import datetime
import numpy as np
import math
import shelve
import gpplib

conf = gpplib.GppConfig()
dataShelf,dataDirectory = conf.myDataDir+'RiskMap.shelf',conf.myDataDir+'roms'

class LookAtRoms():
    def __init__(self):
        self.gm = GliderModel(dataShelf,dataDirectory)
        pass
    
    def GetDataForNdaysStarting(self,yy,mm,dd,numDays):
        self.yy,self.mm,self.dd,self.numDays = yy,mm,dd,numDays
        self.u,self.v,self.time1,self.depth,self.lat,self.lon = self.gm.GetRomsData(yy,mm,dd,numDays)
        self.u_mean, self.v_mean = np.mean(self.u,axis=1), np.mean(self.v,axis=1)
        self.s_mean = np.sqrt(self.u_mean * self.u_mean + self.v_mean * self.v_mean)
        self.zerodNanS_mean = np.where(np.isnan(self.s_mean),0,self.s_mean)
        self.S_meanNZlocs = self.zerodNanS_mean.nonzero()
        self.S_meanNZVals = self.zerodNanS_mean[self.S_meanNZlocs]
        self.hist,self.bin_edges = np.histogram(self.S_meanNZVals,bins=np.linspace(0,10,60))
        plt.figure()
        
        normed_value=1
        
        hist,bins = np.histogram( self.S_meanNZVals, range=(0,1.0), bins= 50, density=True )
        widths = np.diff(bins)
        hist*=normed_value
        
        dt = datetime.datetime(yy,mm,dd)
        plt.bar(bins[:-1],hist,widths)
        plt.title('Current magnitudes on %s'%(dt.strftime('%B %d, %Y')),fontsize=15)
        plt.xlabel('Current Magnitude in m/s',fontsize=15)
        plt.axis([0, 1.0, 0, 12.0])
        plt.text(0.25,5.0,'Mean=%.3f, Var=%.3f, Median=%.3f'%(self.S_meanNZVals.mean(),self.S_meanNZVals.var(),np.median(self.S_meanNZVals)),fontsize=15)
        plt.annotate('Glider speed 0.27 m/s', xy=( 0.27 , 0.01), xytext=(0.27,3.0 ),arrowprops=dict(facecolor='red', shrink=0.05), fontsize=15)
        plt.savefig('HistCvals_%04d%02d%02d.png'%(yy,mm,dd))
        '''
        plt.figure()
        plt.hist(self.S_meanNZVals,bins=np.linspace(0,0.5,50),histtype='stepfilled')
        plt.plot(0.278,200,'r^',ms=16)
        plt.text(0.28,2100,'Glider Velocity=0.28 m/s',fontsize=15)
        plt.text(0.15,5000,'Mean=%.3f, Var=%.3f, Median=%.3f'%(self.S_meanNZVals.mean(),self.S_meanNZVals.var(),np.median(self.S_meanNZVals)),fontsize=15)
        plt.title('Histogram of current values for %04d-%02d-%02d'%(yy,mm,dd),fontsize=20)
        plt.xlabel('Current Magnitude in m/s',fontsize=15)
        plt.savefig('HistCvals_%04d%02d%02d.png'%(yy,mm,dd))
        ''' 


mm = 5
lar = LookAtRoms()
for dd in range(4,25):
    lar.GetDataForNdaysStarting(2011, mm, dd, 1)
    print '%04d-%02d-%02d Average Velocity = %.3f, Avg. Variance= %.3f'%(lar.yy,lar.mm,lar.dd,lar.S_meanNZVals.mean(),lar.S_meanNZVals.var())
    print 'Median = %.3f'%(np.median(lar.S_meanNZVals))
