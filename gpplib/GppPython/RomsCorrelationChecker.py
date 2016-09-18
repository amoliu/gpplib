from gpplib.GenGliderModelUsingRoms import GliderModel
from matplotlib import pyplot as plt
from matplotlib import mlab as mlab
from gpplib import *
from gpplib.Utils import GppConfig
import numpy as np
import scipy.signal as scisig
import scipy.io as sio
import math
import shelve

conf = GppConfig()

romsDataDir=conf.myDataDir+'/roms/'


def PlotCorrelationAndSaveFig(yy,mm,dd,numDays,numPts):
    #yy,mm,dd,numDays = 2011,4,1,15
    gm = GliderModel(myDataDir+'/RiskMap.shelf',romsDataDir)
    u,v,time1,depth,lat,lon = gm.GetRomsData(yy,mm,dd,numDays)
    
    u_mean, v_mean = np.mean(u,axis=1), np.mean(v,axis=1)
    s_mean = np.sqrt(u_mean * u_mean + v_mean * v_mean)
    
    # Now let us look at the correlation in this variability over time.
    (tMax,lyMax,lxMax) = s_mean.shape
    u_mean = np.where(np.isnan(u_mean),0,u_mean)
    v_mean = np.where(np.isnan(v_mean),0,v_mean)
    s_mean = np.where(np.isnan(s_mean),0,s_mean)
    fig = plt.figure()
    numPts = 10
    plt.title('Plot of Auto-correlations in ocean current predictions for \n%d days from %04d-%02d-%02d'%(numDays,yy,mm,dd))
    ax1 = fig.add_subplot(311)
    ax1.grid(True)
    ax1.yaxis.label.set_text('Auto-Correlation\nCurrent u m/s')
    x_pts,y_pts = np.arange(0.1,lxMax-0.1,numPts),np.arange(0.1,lyMax-0.1,numPts)
    X,Y = np.array(np.floor(x_pts),int),np.array(np.floor(y_pts),int)
    for x in X:
        for y in Y:    
            #plt.acorr(s_mean[:,x,y],usevlines=True,detrend=mlab.detrend_mean,normed=True,maxlags=None)
            lags,cVec,linecols,lines = plt.acorr(u_mean[:,y,x],usevlines=False,normed=True,maxlags=None,lw=2)
    plt.xlim((0,max(lags)))
    
    ax2 = fig.add_subplot(312,sharex=ax1)
    ax2.grid(True)
    ax2.yaxis.label.set_text('Auto-Correlation\ncurrent v m/s')
    for x in X:
        for y in Y:    
            #plt.acorr(s_mean[:,x,y],usevlines=True,detrend=mlab.detrend_mean,normed=True,maxlags=None)
            lags,cVec,linecols,lines = plt.acorr(v_mean[:,y,x],usevlines=False,normed=True,maxlags=None,lw=2)
    plt.xlim((0,max(lags)))
    
    ax3 = fig.add_subplot(313,sharex=ax1)
    ax3.grid(True)
    ax3.yaxis.label.set_text('Auto-Correlation\ncurrent mag. m/s')
    for x in X:
        for y in Y:    
            #plt.acorr(s_mean[:,x,y],usevlines=True,detrend=mlab.detrend_mean,normed=True,maxlags=None)
            lags,cVec,linecols,lines = plt.acorr(s_mean[:,y,x],usevlines=False,normed=True,maxlags=None,lw=2)
    plt.xlim((0,max(lags)))
    ax1.xaxis.label.set_text('hour')
    ax2.xaxis.label.set_text('hour')
    ax3.xaxis.label.set_text('hour')
    plt.savefig('AutoCorrelations_%04d%02d%02d_%d.pdf'%(yy,mm,dd,numDays),pad_inches='tight',transparent=True)



def PlotCorrelationWithLocations(gm,lags,cVecs,X,Y,lat,lon,lyMax,lxMax,figTitle,yLabel='Auto-Correlation\nCurrent m/s',saveFigName=None,Thresh=0.6,TimeScale=24):
    #gm = GliderModel('RiskMap.shelf','/Users/arvind/data/roms/')
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    #ax3 = fig.add_subplot(313)
    ax2.axes.set_xlim(-1,lyMax+1 )
    ax2.axes.set_ylim(-1,lxMax)
    #ax3.axes.set_xlim(-1,lyMax)
    #ax3.axes.set_ylim(-1,lxMax)
    ax1.axes.set_xlim((0,numDays*24))
    ax1.axes.set_ylim((-0.5,1.1))   
    ax1.grid(True)
    ax1.yaxis.label.set_text(yLabel)
    x_pts,y_pts = np.linspace(0.1,lxMax-0.1,numPts),np.linspace(0.1,lyMax-0.1,numPts)
    #Thresh = 0.65
    #TimeScale = 24
    # Plot the risk map just so we have an idea of the orientation.
    '''for y in range(1,lyMax-1):
        for x in range(1,lxMax-1):
            ax3.plot(x,y,'.',color='#%02xFF1F'%(int(gm.GetRisk(lat[y],lon[x])*255)))
    '''
    
    i=0
    CorrMat = np.zeros((len(x_pts),len(y_pts)))
    BinCorrMat = np.zeros((len(x_pts),len(y_pts)))
    #for y in Y:
    #    for x in X:
    for j in range(0,len(Y)):
        for k in range(0,len(X)):
            x,y = X[k],Y[j]
            #plt.acorr(s_mean[:,x,y],usevlines=True,detrend=mlab.detrend_mean,normed=True,maxlags=None)
            #lags,cVec,linecols,lines = ax1.acorr(u_mean[:,y,x],usevlines=False,normed=True,maxlags=None,lw=2,color='#%02x%02x%02x'%((x*5+50)%256,(x*5)%256,(y*5)%256))
            if gm.GetRisk(lat[y],lon[x])<1:
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
    
    #import pdb; pdb.set_trace()
                
    if saveFigName != None:
        saveFigName='%s_Thresh_%.2f_TScale_%d.pdf'%(saveFigName,Thresh,TimeScale)
        plt.savefig(saveFigName)
    return CorrMat,BinCorrMat


def GetCorrelationPlot(gm,lat,lon,qty,yy,mm,dd,numDays,numPts):
    # Now let us look at the correlation in this variability over time.
    (tMax,lyMax,lxMax) = qty.shape
    qty = np.where(np.isnan(qty),0,qty)
    
    #x_pts,y_pts = gm.x_pts,gm.y_pts 
    lat_pts,lon_pts = gm.lat_pts,gm.lon_pts
    x_pts,y_pts=[],[]
    for i in range(0,len(lat_pts)):
        x,y = gm.LatLonToRomsXY(lat_pts[i],lon_pts[i],lat,lon)
        x_pts.append(x)
        y_pts.append(y)
    
    #np.linspace(0.1,lxMax-0.1,numPts),np.linspace(0.1,lyMax-0.1,numPts)
    X,Y = np.array(np.floor(x_pts),int),np.array(np.floor(y_pts),int)
    cumVec = np.zeros((numPts**2,numDays *24 *2 -1))
    tLags =  np.zeros((numPts**2,numDays *24 *2 -1))
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


def GetVectorCorrelationPlot(gm,lat,lon,qty1,qty2,yy,mm,dd,numDays,numPts):
    # Here, we are going to treat [qty1 qty2]
    (tMax1,lyMax1,lxMax1) = qty1.shape
    (tMax2,lyMax2,lxMax2) = qty2.shape
    qty1 = np.where(np.isnan(qty1),0,qty1)
    qty2 = np.where(np.isnan(qty2),0,qty2)
    
    lat_pts, lon_pts = gm.lat_pts, gm.lon_pts
    x_pts, y_pts = [], []
    for i in range(0,len(lat_pts)):
        x,y = gm.LatLonToRomsXY(lat_pts[i],lon_pts[i],lat,lon)
        x_pts.append(x)
        y_pts.append(y)
    
    X,Y = np.array(np.floor(x_pts),int),np.array(np.floor(y_pts),int)
    cumVec = np.zeros((numPts**2,numDays *24 *2 -1))
    tLags =  np.zeros((numPts**2,numDays *24 *2 -1))
    i=0
    fig = plt.figure()
    for y in Y:
        for x in X:
            lags,cVec,linecols,lines = plt.acorr(np.dot(qty1[:,y,x],qty2[:,y,x]),usevlines=False,normed=True,maxlags=None,lw=2)
            tLags[i] = lags
            cumVec[i] += cVec
            i=i+1
    plt.close()
    
    return tLags,cumVec,X,Y,lxMax,lyMax
    
           
    

def PlotCorrelationsWithLocations(yy,mm,dd,numDays,numPts,startM=0,endM=6):
    
    gm = GliderModel(conf.myDataDir+'RiskMap.shelf',romsDataDir)
    cumVec_u = np.zeros((numPts**2, numDays *24 *2 -1))
    tLags =  np.zeros((numPts**2, numDays *24*2 -1))
    cumVec_v = np.zeros((numPts**2, numDays *24 *2 -1))
    cumVec_s = np.zeros((numPts**2, numDays *24 *2 -1))
    totAcc = 0
    
    daysInMonths = [31,28,31,30,31,30,31,31,30,31,30,31]
    if yy%4 == 0:
        daysInMonths[1] = 29
    
    import pdb; pdb.set_trace()
    for j in range(startM,endM):
        for i in range(0,daysInMonths[j+mm-1],1): # TODO: do this using with actual days in the month.
            u,v,time1,depth,lat,lon = gm.GetRomsData(yy,mm+j,dd+i,numDays)
            u_mean, v_mean = np.mean(u,axis=1), np.mean(v,axis=1)
            s_mean = np.sqrt(u_mean * u_mean + v_mean * v_mean)
            #PlotFFTandSaveFig(yy,mm,dd+i,numDays)
            lags_u,cVec_u,X,Y,lxMax,lyMax = GetCorrelationPlot(gm,lat,lon,u_mean,yy,mm+j,dd+i,numDays,numPts)
            lags_v,cVec_v,X,Y,lxMax,lyMax = GetCorrelationPlot(gm,lat,lon,v_mean,yy,mm+j,dd+i,numDays,numPts)
            lags_s,cVec_s,X,Y,lxMax,lyMax = GetCorrelationPlot(gm,lat,lon,s_mean,yy,mm+j,dd+i,numDays,numPts)
            #cVec,lags,nDays = PlotCorrelationsWithLocations(yy,mm,dd+i,numDays,numPts)
            cumVec_u+=cVec_u
            cumVec_v+=cVec_v
            cumVec_s+=cVec_s
            tLags = lags_u
            totAcc += 1
    Thresh=0.5
    TimeScale=48
    CorrMatU,BinCorrMatU = PlotCorrelationWithLocations(gm,tLags,cumVec_u/float(totAcc),X,Y,lat,lon,lyMax,lxMax,'Plot of Auto-correlations in ocean current predictions for \n%d days from %04d-%02d-%02d'%(totAcc,yy,mm,dd),'Auto-Correlation\nCurrent u m/s','AutoCorrelate_U_mean',Thresh,TimeScale) 
    CorrMatV,BinCorrMatV = PlotCorrelationWithLocations(gm,tLags,cumVec_v/float(totAcc),X,Y,lat,lon,lyMax,lxMax,'Plot of Auto-correlations in ocean current predictions for \n%d days from %04d-%02d-%02d'%(totAcc,yy,mm,dd),'Auto-Correlation\nCurrent v m/s','AutoCorrelate_V_mean',Thresh,TimeScale) 
    CorrMatS,BinCorrMatS = PlotCorrelationWithLocations(gm,tLags,cumVec_s/float(totAcc),X,Y,lat,lon,lyMax,lxMax,'Plot of Auto-correlations in ocean current predictions for \n%d days from %04d-%02d-%02d'%(totAcc,yy,mm,dd),'Auto-Correlation\nCurrent s m/s','AutoCorrelate_S_mean',Thresh,TimeScale) 
    
    CorrShelf = shelve.open('CorrModel_%.2f_%d.shelf'%(Thresh,TimeScale))
    CorrShelf['CorrMatU'],CorrShelf['BinCorrMatU'] = CorrMatU,BinCorrMatU
    CorrShelf['CorrMatV'],CorrShelf['BinCorrMatV'] = CorrMatV,BinCorrMatV
    CorrShelf['CorrMatS'],CorrShelf['BinCorrMatS'] = CorrMatS,BinCorrMatS
    CorrShelf['tLags'] = tLags
    CorrShelf['cumVec_u'],CorrShelf['cumVec_v'],CorrShelf['cumVec_s'] = cumVec_u, cumVec_v, cumVec_s
    CorrShelf['X'],CorrShelf['Y'],CorrShelf['lat'],CorrShelf['lon'] = X,Y,lat,lon
    CorrShelf['lyMax'], CorrShelf['lxMax'] = lyMax,lxMax
    CorrShelf.close()
    #import pdb; pdb.set_trace()

    CorrMatU = np.where(np.isnan(CorrMatU),0,CorrMatU)
    CorrMatV = np.where(np.isnan(CorrMatV),0,CorrMatV)
    CorrMatS = np.where(np.isnan(CorrMatS),0,CorrMatS)
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
    
    # Save to Matlab if Geoff needs this.
    SaveCorrelationShelfToMatlabFormat(Thresh,TimeScale)    
    return CorrMatU,CorrMatV,CorrMatS,BinCorrMatU,BinCorrMatV,BinCorrMatS

def PlotFFT(val,X,Y):
    fig=plt.figure()
    plt.title('Plot of FFT of U for \n%d days from %04d-%02d-%02d'%(numDays,yy,mm,dd))
    ax1 = fig.add_subplot(111)
    ax1.grid(True)
    ax1.yaxis.label.set_text('FFT magnitude U')
   
    numPts = 256
    
    #from numpy.fft import ftt,fftshift,fftfreq
    for x in X:
        for y in Y:
            #import pdb; pdb.set_trace()
            #t = np.linspace(0,24,120)
            dt = 1  # half hour.
            fMax = 1 # half hour
            f = np.linspace(0,fMax,numPts/2+1)*val.shape[0]
            ft = np.fft.fft(val[:,y,x],n=numPts)
            mgft = np.abs(ft)
            df = fMax/float(numPts/2+1)
            plt.plot(f,mgft[0:numPts/2+1])

def SaveCorrelationShelfToMatlabFormat(Thresh,TimeScale):
    CorrShelf = shelve.open('CorrModel_%.2f_%d.shelf'%(Thresh,TimeScale))
    corrs = CorrShelf
    sio.savemat('Correlations_%.2f_%d.mat'%(Thresh,TimeScale),corrs)
    CorrShelf.close()


def PlotFFTandSaveFig(yy,mm,dd,numDays):
    gm = GliderModel()
    u,v,time1,depth,lat,lon = gm.GetRomsData(yy,mm,dd,numDays)
    
    u_mean, v_mean = np.mean(u,axis=1), np.mean(v,axis=1)
    s_mean = np.sqrt(u_mean * u_mean + v_mean * v_mean)
    
    numPts = 10
    # Now let us look at the correlation in this variability over time.
    (tMax,lyMax,lxMax) = s_mean.shape
    x_pts,y_pts = np.arange(0.1,lxMax-0.1,numPts),np.arange(0.1,lyMax-0.1,numPts)
    X,Y = np.array(np.floor(x_pts),int),np.array(np.floor(y_pts),int)
    s_mean = np.where(np.isnan(s_mean),0,s_mean)
    PlotFFT(u_mean,X,Y)

numDays = 20
numPts = 10
sYY,sMM,sDD = 2011,01,5
CorrMatU,CorrMatV,CorrMatS,BinCorrMatU,BinCorrMatV,BinCorrMatS = PlotCorrelationsWithLocations(sYY,sMM,sDD,numDays,numPts)
