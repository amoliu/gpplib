#!/usr/bin/env python
#import math
#import matplotlib.pyplot as plt

cellCapacity = 8000 # mAh
numCells  = 25

totalCap = cellCapacity * numCells

withoutElectronics = 273.6 #120
timeWithoutElectronics = totalCap/withoutElectronics

withElectronics = 335 #365 #273.6+150 #320
timeWithElectronics = totalCap/withElectronics

print 'Total Capacity = %.3f'%( totalCap/1000 )
print 'With Electronics it would last : %.3f days'%(timeWithElectronics/24)
print 'Without Electronics it would last: %.3f days'%(timeWithoutElectronics/24)
