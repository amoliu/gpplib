'''
This is a simple little Vrms calculator for some of the CRO data.
'''
import numpy as np
#import matplotlib.pyplot as plt

import sys
import os
import re
import pylab
import scipy

nfft = 4096


def GetVoltage(fileName):
    f=open(fileName,'r')
    lines=f.readlines()
    
    
    lval,rval=[],[]
    for line in lines:
        mSamp = re.match('Sample Interval,([0-9\-E\.]+),s,([0-9E\-\.]+),([0-9E\-\.]+),',line)
        if(mSamp):
            sampRate = 1./float(mSamp.group(1))
        m=re.match(',,,([0-9E\-\.]+),([0-9E\-\.]+),',line)
        if(m):
            #print m.group(1),m.group(2)
            lval.append(float(m.group(1))); rval.append(float(m.group(2)))
            
    time,hVolts = np.array(lval), np.array(rval)
    f.close()
    
    return time,hVolts,sampRate


def ComputeRMS( data ):
    
    # Get Mean
    mean= np.mean(data)
    dataMinusMean =  data - mean
    
    rms = dataMinusMean ** 2
    rms = scipy.sqrt( rms.sum()/len(dataMinusMean) )
    
    return rms

def MovingAverage(data, windSize=5):
    mAvg = np.cumsum(data, dtype=float)
    return (mAvg[windSize-1:]-mAvg[:1-windSize])/windSize

def RMSfromPSD( data, samplerate, graph=True ):
    
    y, x = pylab.psd(data, NFFT = nfft, Fs=samplerate)
    t = np.linspace(0, len(data)*samplerate, num=len(data))
    # Calculate the RMS
    
    # The energy returned by PSD depends on FFT size
    freqbandwidth = x[1]
    y=y*freqbandwidth
    
    # The energy returned by PSD depends on Samplerate
    y=y/float(samplerate)
    
       
    
    
    # Summing the power in freq domain to get RMS
    rms = scipy.sqrt(y.sum())
    if graph == True :
        pylab.subplot(311)
        pylab.plot(t,data)
        pylab.subplot(312)
        pylab.plot(MovingAverage(data,100))
        pylab.subplot(313)
        pylab.psd(data, nfft, samplerate)
        pylab.show()

    return rms
    

for i in range(1,10):
    #file = 'GumstixOff.csv'
    file = 'resistordivider/%d.csv'%(i)
    time,hVolts,sampRate = GetVoltage(file)
    print 'Mean Voltage = %.3f V'%(scipy.mean(hVolts))
    print 'Peak to Peak Voltage = %.3f V'%(np.max(hVolts)-np.min(hVolts))
    print 'RMS for High=%.5f'%(ComputeRMS(hVolts))
    print 'RMS using PSD method = %.5f'%(RMSfromPSD(hVolts,sampRate))

#file = 'squarewave.csv'
#time,hVolts,sampRate = GetVoltage(file)
#print 'Mean Voltage = %.3f V'%(scipy.mean(hVolts))
#print 'Peak to Peak Voltage = %.3f V'%(np.max(hVolts)-np.min(hVolts))
#print 'RMS for High=%.5f'%(ComputeRMS(hVolts))
#print 'RMS using PSD method = %.5f'%(RMSfromPSD(hVolts,sampRate))
