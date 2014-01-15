'''
:Author: Arvind A de Menezes Pereira
:Date: $Date: 2012-05-16 15:00:00 PST (Wed, 16 May 2011) $
:Revision: $Revision: 1 $
:Summary: This class produces 2D Autocorrelations.
'''
import numpy as np
import scipy.io as sio
import shelve
import math
import gpplib
from gpplib.GenGliderModelUsingRoms import GliderModel
from gpplib.Utils import DateRange
import matplotlib.pyplot as plt

class GetRomsCorrelations(object):
    ''' Class to compute ROMS auto-correlations.
    '''
    def __init__(self,maxLagHrs):
        ''' __init__(maxLagHrs) 
        Args:
            maxLagHrs (int): maximum number of  lag-hours
        '''
        self.maxLagHrs = maxLagHrs
        
        self.gm = GliderModel(conf.riskMapDir+'RiskMap.shelf',gpplib.gppConf.romsDataDir)
        self.numPts = len( self.gm.x_pts )
        self.cumVec_u = np.zeros((self.numPts**2, 2* maxLagHrs-1))
        self.cumVec_v = np.zeros((self.numPts**2, 2* maxLagHrs-1))
        self.cumVec_s = np.zeros((self.numPts**2, 2* maxLagHrs-1))
        self.tLags = np.zeros((self.numPts**2, 2* maxLagHrs-1))
        self.totAcc = 0
    
    def PlotCorrelationWithLocations(self,lags,cVecs,X,Y,lat,lon,lyMax,lxMax,figTitle,\
            yLabel='Auto-Correlation\nCurrent m/s',saveFigName=None,Thresh=0.6,TimeScale=24):
        ''' 
        '''
        fig = plt.figure()
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        ax2.axes.set_xlim(-1,lyMax+1 )
        ax2.axes.set_ylim(-1,lxMax)
        ax1.axes.set_xlim((0,self.maxLagHrs))
        ax1.axes.set_ylim((-0.5,1.1))   
        ax1.grid(True)
        ax1.yaxis.label.set_text(yLabel)
        #x_pts,y_pts = np.linspace(0.1,lxMax-0.1,self.numPts),np.linspace(0.1,lyMax-0.1,self.numPts)
        
        i=0
        CorrMat = np.zeros((len(X),len(Y))) #np.zeros((len(x_pts),len(y_pts)))
        BinCorrMat = np.zeros((len(X),len(Y))) #np.zeros((len(x_pts),len(y_pts)))
        import pdb; pdb.set_trace()

        for j in range(0,len(Y)):
            for k in range(0,len(X)):
                x,y = X[k],Y[j]
                #plt.acorr(s_mean[:,x,y],usevlines=True,detrend=mlab.detrend_mean,normed=True,maxlags=None)
                #lags,cVec,linecols,lines = ax1.acorr(u_mean[:,y,x],usevlines=False,normed=True,maxlags=None,lw=2,color='#%02x%02x%02x'%((x*5+50)%256,(x*5)%256,(y*5)%256))
                if self.gm.GetRisk(lat[y],lon[x])<1:
                    ax1.plot(lags[i],cVecs[i],'.',color='#%02x%02x%02x'%((x*5+50)%256,(x*5)%256,(y*5)%256))
                    CorrMat[k,j] = cVecs[i,lags[0,-1]+TimeScale]
                    #ax2.plot(x,y,'*',color='#%02x%02x%02x'%((x*5+50)%256,(x*5)%256,(y*5)%256),lw=5,ms=14)
                    if cVecs[i,lags[0,-1]+TimeScale]>=Thresh:
                        ax2.plot(x,y,'*',color='#0000ff',lw=5,ms=20)
                        BinCorrMat[k,j] = 1.0
                    else:
                        if cVecs[i,lags[0,-1]+TimeScale]<Thresh:
                            ax2.plot(x,y,'x',color='#ff0000',lw=5,ms=20)
                            BinCorrMat[k,j] = 0.0
                else:
                    ax2.plot(x,y,'.',color='#ffff00',lw=5,ms=10)
                    CorrMat[k,j] = 0.0
                    BinCorrMat[k,j] = -1.0
                i=i+1
        if saveFigName != None:
            saveFigName='%s_Thresh_%.2f_TScale_%d.pdf'%(saveFigName,Thresh,TimeScale)
            plt.savefig(saveFigName)
        return CorrMat,BinCorrMat

    def ThresholdLocations(self, Thresh=0.5, TimeScale=48 ):
            ''' Apply the given threshold of amount of correlation required by the given time.
            Also stores a few plots of the results.
            
            Args:
                Thresh=0.5 (float) : Threshold on a scale between (-1 and +1) above which we deem something well-correlated
                TimeScale=48 (int) : Time in hours at which the thresholding operation is performed.
                
            Returns:
                CorrMatU,CorrMatV,CorrMatS : Correlation matrices for the easting, northing and magnitudes.
                BinCorrMatU,BinCorrMatV,BinCorrMatS : Correlation matrices after thresholding
            '''
            CorrMatU,BinCorrMatU = self.PlotCorrelationWithLocations(self.tLags,self.cumVec_u/float(self.totAcc),self.X,self.Y,self.lat,self.lon,self.lyMax,self.lxMax, \
                'Plot of Auto-correlations in ocean current predictions for \n%d days from %04d-%02d-%02d' \
                %(self.totAcc,self.yy,self.mm,self.dd),'Auto-Correlation\nCurrent u m/s','AutoCorrelate_U_mean',Thresh,TimeScale) 
            CorrMatV,BinCorrMatV = self.PlotCorrelationWithLocations(self.tLags,self.cumVec_v/float(self.totAcc),self.X,self.Y,self.lat,self.lon,self.lyMax,self.lxMax, \
                'Plot of Auto-correlations in ocean current predictions for \n%d days from %04d-%02d-%02d' \
                %(self.totAcc,self.yy,self.mm,self.dd),'Auto-Correlation\nCurrent v m/s','AutoCorrelate_V_mean',Thresh,TimeScale) 
            CorrMatS,BinCorrMatS = PlotCorrelationWithLocations(self.tLags,self.cumVec_s/float(self.totAcc),self.X,self.Y,self.lat,self.lon,self.lyMax,self.lxMax, \
                'Plot of Auto-correlations in ocean current predictions for \n%d days from %04d-%02d-%02d' \
                %(self.totAcc,self.yy,self.mm,self.dd),'Auto-Correlation\nCurrent s m/s','AutoCorrelate_S_mean',Thresh,TimeScale) 
            
            CorrShelf = shelve.open('CorrModel_%.2f_%d.shelf'%(Thresh,TimeScale))
            CorrShelf['CorrMatU'],CorrShelf['BinCorrMatU'] = CorrMatU,BinCorrMatU
            CorrShelf['CorrMatV'],CorrShelf['BinCorrMatV'] = CorrMatV,BinCorrMatV
            CorrShelf['CorrMatS'],CorrShelf['BinCorrMatS'] = CorrMatS,BinCorrMatS
            CorrShelf['tLags'] = tLags
            CorrShelf['cumVec_u'],CorrShelf['cumVec_v'],CorrShelf['cumVec_s'] = cumVec_u, cumVec_v, cumVec_s
            CorrShelf['X'],CorrShelf['Y'],CorrShelf['lat'],CorrShelf['lon'] = X,Y,lat,lon
            CorrShelf['lyMax'], CorrShelf['lxMax'] = lyMax,lxMax
            CorrShelf.close()
            self.SaveCorrelationShelfToMatlabFormat(Thresh,TimeScale)    
        
            CorrMatU = np.where(np.isnan(CorrMatU),0,CorrMatU)
            CorrMatV = np.where(np.isnan(CorrMatV),0,CorrMatV)
            CorrMatS = np.where(np.isnan(CorrMatS),0,CorrMatS)
            # Save to Matlab if Geoff needs this.
            
            figU = plt.figure()
            plt.imshow(CorrMatU.transpose(),origin='Upper',cmap=plt.get_cmap(plt.cm.jet_r))
            plt.title('Auto-correlation coefficient U (threshold %.2f @ %d hour lag)'%(Thresh,TimeScale))
            plt.colorbar()
            plt.savefig('CorrMatU_Thresh%.2f_Lag%d.pdf'%(Thresh,TimeScale))
            figV = plt.figure()
            plt.imshow(CorrMatV.transpose(),origin='Upper',cmap=plt.get_cmap(plt.cm.jet_r))
            plt.title('Auto-correlation coefficient V (threshold %.2f @ %d hour lag)'%(Thresh,TimeScale))
            plt.colorbar()
            plt.savefig('CorrMatV_Thresh%.2f_Lag%d.pdf'%(Thresh,TimeScale))
            figS = plt.figure()
            plt.imshow(CorrMatS.transpose(),origin='Upper',cmap=plt.get_cmap(plt.cm.jet_r))
            plt.title('Auto-correlation coefficient S (threshold %.2f @ %d hour lag)'%(Thresh,TimeScale))
            plt.colorbar()
            plt.savefig('CorrMatS_Thresh%.2f_Lag%d.pdf'%(Thresh,TimeScale))
            
            return CorrMatU,CorrMatV,CorrMatS,BinCorrMatU,BinCorrMatV,BinCorrMatS

    def SaveCorrelationShelfToMatlabFormat(self,Thresh,TimeScale):
        ''' Convert from Correlation Shelf format to Matlab.
        '''
        CorrShelf = shelve.open('CorrModel_%.2f_%d.shelf'%(Thresh,TimeScale))
        corrs = CorrShelf
        sio.savemat('Correlations_%.2f_%d.mat'%(Thresh,TimeScale),corrs)
        CorrShelf.close()    
        
    def GetCorrelationPlot(self,lat,lon,qty,yy,mm,dd,numDays,numPts):
        ''' GetCorrelationPlot(lat,lon,qty,yy,mm,dd,numDays,numPts)
        Args:
            lat,lon (floats) : latitude and longitude arrays
            qty (np.array) : quantity whose auto-correlation we are computing
            yy,mm,dd, numDays (ints): year, month, day, number of days
            numPts : number of points we are finding the auto-correlations for.
            
        Returns:
            tLags (np.array) : vector with the time-lags (always the same)
            cumVec (np.array): correlation coefficients at different lags
            X, Y (np.arrays) : locations for which we have computed these
            lxMax, lyMax (ints): the width and height of the ROMS map
        '''
        # Now let us look at the correlation in this variability over time.
        (tMax,lyMax,lxMax) = qty.shape
        self.tMax,self.lyMax,self.lxMax = qty.shape
        qty = np.where(np.isnan(qty),0,qty)
        #x_pts,y_pts = gm.x_pts,gm.y_pts 
        lat_pts,lon_pts = self.gm.lat_pts,self.gm.lon_pts
        x_pts,y_pts=[],[]
        for i in range(0,len(lat_pts)):
            x,y = self.gm.LatLonToRomsXY(lat_pts[i],lon_pts[i],lat,lon)
            x_pts.append(x)
            y_pts.append(y)
        
        X,Y = np.array(np.floor(x_pts),int),np.array(np.floor(y_pts),int)
        self.X,self.Y = X,Y
        cumVec = np.zeros((numPts**2,self.maxLagHrs *2 -1))
        tLags =  np.zeros((numPts**2,self.maxLagHrs *2 -1))
        i=0
        fig = plt.figure()
        for y in Y:
            for x in X:
                lags,cVec,linecols,lines = plt.acorr(qty[:,y,x],usevlines=False,normed=True,maxlags=None,lw=2)
                tLags[i] = lags
                cumVec[i] += cVec
                i=i+1
        plt.close()
        return tLags,cumVec,X,Y,lxMax,lyMax
    
    
    def ComputeCorrelations(self,yy_start,mm_start,dd_start,yy_end,mm_end,dd_end):
        ''' ComputeCorrelations(yy_start,mm_start,dd_start,yy_end,mm_end,dd_end)
        Args:
            yy_start,mm_start,dd_start (ints) : date correlation computations start from.
            yy_end,mm_end,dd_end (ints) : date correlation computations end at.
            
        Returns:
            CorrMatU, CorrMatV, CorrMatS
        '''
        numPts = self.numPts
        numDays = int(self.maxLagHrs/24 + 0.5)
        self.dr = DateRange(yy_start,mm_start,dd_start,yy_end,mm_end,dd_end)
        for yy,mm,dd in self.dr.DateList:
            self.yy,self.mm,self.dd = yy,mm,dd
            u,v,time1,depth,lat,lon = self.gm.GetRomsData(yy,mm,dd,numDays)
            u_mean, v_mean = np.mean(u,axis=1), np.mean(v,axis=1)
            s_mean = np.sqrt(u_mean**2 + v_mean**2)
            lags_u,cVec_u,X,Y,lxMax,lyMax = self.GetCorrelationPlot(lat,lon,u_mean,yy,mm,dd,numDays,numPts)
            lags_v,cVec_v,X,Y,lxMax,lyMax = self.GetCorrelationPlot(lat,lon,v_mean,yy,mm,dd,numDays,numPts)
            lags_s,cVec_s,X,Y,lxMax,lyMax = self.GetCorrelationPlot(lat,lon,s_mean,yy,mm,dd,numDays,numPts)
            self.cumVec_u+=cVec_u
            self.cumVec_v+=cVec_v
            self.cumVec_s+=cVec_s
            self.tLags = lags_u
            self.totAcc += 1
            self.lat,self.lon = lat,lon
            
            

grc = GetRomsCorrelations(120)
grc.ComputeCorrelations(2011,1,1,2011,1,10)
CorrMatU,CorrMatV,CorrMatS,BinCorrMatU,BinCorrMatV,BinCorrMatS = \
    grc.ThresholdLocations(0.5,48)