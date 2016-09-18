from gpplib.GenGliderModelUsingRoms import GliderModel
import numpy as np
import scipy.io as sio
import math
import shelve
import os, re
import time

daysInMonths = [31,28,31,30,31,30,31,31,30,31,30,31]

gModel = {}
yy,mm,dd,numDays,dMax = 2011,1,1,2,1.5
gm = GliderModel('../gpplib/RiskMap.shelf','/Users/arvind/data/roms/')
global gmShelf
useNoise = True
useRomsNoise = True

curNoiseVals = [0.01, 0.025, 0.05, 0.1, 0.15, 0.2, 0.32, 0.5]

for mm in range(2,3):
    for i in range(0,daysInMonths[mm-1],numDays):
        for j in range(0,len(curNoiseVals)):
            print 'Generating the transition model for %04d-%02d-%02d over %d hours using Current Noises of %.3f'%(yy,mm,dd+i,numDays*24,curNoiseVals[j])
            startTime = time.time()
            #gModel['TransModel'] = gm.GenerateTransitionModelsUsingRomsData(yy,mm,dd+i,numDays,dMax)
            
            if useRomsNoise:
                curNoiseSigma = curNoiseVals[j]
                gm.UseRomsNoise = True
                gm.sigmaCurU = curNoiseSigma; gm.sigmaCurV = curNoiseSigma;
            
            if not useNoise:
                gModel['TransModel'] = gm.GenerateTransitionModelsUsingRomsData(yy,mm,dd+i,numDays,dMax)
                if not useRomsNoise:
                    gmShelf = shelve.open('gliderModel_%04d%02d%02d_%d.shelf'%(yy,mm,dd+i,numDays))
                else:
                    gmShelf = shelve.open('gliderModel_%04d%02d%02d_%d_RN_%.3f.shelf'%(yy,mm,dd+i,numDays,curNoiseSigma))
            else:
                noiseSigma = 0.1
                gm.sigmaX, gm.sigmaY = noiseSigma, noiseSigma
                gModel['TransModel'] = gm.GenerateTransitionModelsUsingRomsData(yy,mm,dd+i,numDays,dMax, useNoise )
                if not useRomsNoise:
                    gmShelf = shelve.open('gliderModel_%04d%02d%02d_%d_%.3f.shelf'%(yy,mm,dd+i,numDays,noiseSigma))
                else:
                    gmShelf = shelve.open('gliderModel_%04d%02d%02d_%d_%.3f_RN_%.3f.shelf'%(yy,mm,dd+i,numDays,noiseSigma,curNoiseSigma))
            endTime = time.time()
            gmShelf['TransModel'] = gModel['TransModel']
            gmShelf['FinalLocs'] = gm.FinalLocs
            gmShelf['TracksInModel']= gm.TracksInModel
            gmShelf['GenTime']=endTime-startTime
            gmShelf.close()
            print '\n\n\n'
