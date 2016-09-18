''' Here we write a very simple wave simulator.

Reference: http://www.labri.fr/publications/is/2006/Fre06/frechot_realistic_simulation_of_ocean_surface_using_wave_spectra.pdf
Title: Realistic simulation of ocean surface using wave spectra
}

'''
import numpy as np
from numpy import random

class WaveSim(object):
    ''' Initialize '''
    def __init__(self,N=1):
        self.simTime = 10.
        self.fs = 100.
        numPts = self.fs*self.simTime
        
        self.t = np.linspace(0,self.simTime,numPts)
        self.x0 =  [ 10., 0. ]
        
        
        Wn = random.randn(N)
        print Wn
        
        
        
        
ws = WaveSim(1)
