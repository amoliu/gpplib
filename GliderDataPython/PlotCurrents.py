'''
Created on Sep 4, 2011

@author: Arvind Antonio de Menezes Pereira
@summary: This program plots the current field contained in the file created by
          CurrentsROMS.py. I am trying to push this onto my GIT repository, but it keeps failing!
'''

import csv
import pylab
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.transforms as tform
import numpy as np
import math

#currentFileName1 = '20110823ROMSCurrentMap1000.0.vmap'
currentFileName2 = '20110716ROMSCurrentMap1000.0.vmap'

def NonNanMinMax(arrayVals):
    min = float('inf')
    max = float('-inf')
    for arrayVal in arrayVals:
        if not math.isnan(arrayVal):
            if arrayVal<min:
                min = arrayVal
            if arrayVal>max:
                max = arrayVal
    return min,max

def PlotCurrents(currentFileName):
    currents = csv.reader(open(currentFileName), delimiter=',', quotechar='#')

    u=[]
    v=[]
    x=[]
    y=[]
    
    
    for current in currents:
        x.append(float(current[0]))
        y.append(float(current[1]))
        u.append(float(current[2]))
        v.append(float(current[3]))
    
    y_max=max(y)    
    U=np.array(u)
    V=np.array(v)
    X=np.array(x)
    Y=np.array(y)
    Y=y_max-Y
    Mag = np.sqrt(np.square(U)+np.square(V))
    MagMin,MagMax = NonNanMinMax(Mag)
    div=(MagMax-MagMin)/100.
    N = np.arange(MagMin,MagMax,div)
    #Colors = plt.makeMappingArray(N,)
    print MagMin,MagMax
    
    # Create a colormap for these
    plt.figure()
    Q=plt.quiver(X,Y,U,V,Mag,cmap=plt.cm.jet_r)
    plt.colorbar()



if __name__ == '__main__':
    #plt.figure()
    #PlotCurrents(currentFileName1)
    plt.figure()
    PlotCurrents(currentFileName2)
