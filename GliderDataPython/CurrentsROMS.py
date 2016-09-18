'''
Created on Sep 3, 2011

@author: Arvind de Menezes Pereira
@summary: A much needed visualization system for ROMS currents vis a vis
        what my other planner has been using.
        
'''
import numpy as np
import sys
import datetime
import shelve
import math
import LatLonConversions
from FindRiskFromLatLon import LatLonMap

sys.path.append('/Users/arvind/Documents/code/workspace/ppas/src/ppas')
import roms

# glider dive parameters. used to estimate travel times between each node
dive_params = dict(
dive_spacing = 100., # horizontal spacing between dives in meters
min_depth = 20., # minimum glider depth in meters
max_depth = 90., # maximum glider depth in meters
horizontal_vel = .278 # glider velocity in m/s
)

lon0 = -118.8 -0.03
lon1 = -117.7 +0.03
lat0 = 33.25 -0.03
lat1 = 34.133333 + 0.03
llmap = LatLonMap(1000.)

'''
Create a current-vector map with all the currents
in a particular region. Here, we are going to use
the operating regime of the glider to determine
the average currents in a vertical profile at 
each location in the map
'''

yy,mm,dd = 2011,7,16
dt = datetime.date(yy,mm,dd)
dt_str = '%04d%02d%02d' % (yy,mm,dd)
fName = '%04d%02d%02dROMSCurrentMap' % (yy,mm,dd)
fName = fName + str(1000.) + '.vmap'
f = open(fName,mode='w')
time0 = roms.datetime_to_seconds(datetime.datetime(yy,mm,dd,15))
time1 = time0 + 24.*3600.
depth0 = 20
depth1 = 90
current_lims = 4    # +-10 m/s

print 'Connecting to ROMS server'
dataset = roms.open_dataset(dt)

print 'Downloading data'
data = roms.get_data(dataset, lat0, lat1, lon0, lon1, depth0,depth1, time0, time1)
myDepth = (depth0 + depth1)/2.
for i in range(0,103):
    for j in range(0,98):
        #tot_u, tot_v,avg_u,avg_v = 0.,0.,-2. * current_lims,-2. * current_lims
        tot_u, tot_v,avg_u,avg_v = 0.,0.,float('nan'),float('nan')
        count_u, count_v = 0.,0.
        myLat,myLon = llmap.GetLatLon( j,i )
        myTime = time0
        for k in range(depth0,depth1):
            u = roms.get_value(data,myLat,myLon,myDepth,myTime,'u',interp='linear')
            v = roms.get_value(data,myLat,myLon,myDepth,myTime,'v',interp='linear')
            '''
                Quality control needed!!!
            '''
            if abs(u)<current_lims:
                tot_u = tot_u + u
                count_u = count_u + 1
            if abs(v)<current_lims:
                tot_v = tot_v + v
                count_v  = count_v + 1
        if count_u > 0:
            avg_u = tot_u/count_u
        if count_v > 0:
            avg_v = tot_v/count_v
        print >> f, '%d,%d,%f,%f' %(j,i,avg_u,avg_v)

print 'Done writing currents to file!'
f.close()