from __future__ import division
import numpy as np
import math

cimport numpy as np

DTYPE = np.int
ctypedef np.int_t DTYPE_t


def FindLowAndHighIndices(a,A):
    min_a,max_a =  min(A)[0],max(A)[0]
    lowInd,highInd = 0, len(A[0])-1
    if a<A[0][0]:
        highInd = 0
        return lowInd,highInd
    
    for i in range(0,len(A)):
        if A[i] <= a:
            lowInd,highInd = i,i+1
            if highInd>=len(A):
                highInd = len(A)-1
                return lowInd,highInd
        else:
            return lowInd,highInd
        
'''
Linear Interpolation
Reference: http://en.wikipedia.org/wiki/Linear_interpolation
'''
def LinearInterpolate(x,F):
    x0,x1 = FindLowAndHighIndices(x,F)
    if x1!=x0:
        return (F[x1]-F[x0])*(x-x0)/float(x1-x0)
    else:
        return F[x0]

'''
Bilinear Interpolation
Reference: http://en.wikipedia.org/wiki/Bilinear_interpolation

Here: lat0,lon0 are the point which we're interested in.
      lat,lon are the lat and lon arrays.
      V is the 2D array from which interpolation will take place. 
'''
def BilinearInterpolate(lat0,lon0,lat,lon,V):
    #print lat0,lon0
    y1,y2 = FindLowAndHighIndices(lat0,lat)
    x1,x2 = FindLowAndHighIndices(lon0,lon)
    xDif,yDif = lon[x2][0] - lon[x1][0], lat[y2][0]-lat[y1][0]
    fQ11,fQ12,fQ21,fQ22 = V[y1,x1],V[y2,x1],V[y1,x2],V[y2,x2]
    if xDif != 0 and yDif !=0:
        return (fQ11*(lon[x2]-lon0)*(lat[y2]-lat0) + fQ21*(lon0-lon[x1])*(lat[y2]-lat0) +\
            fQ12*(lon[x2]-lon0)*(lat0-lat[y1]) + fQ22*(lon0-lon[x1])*(lat0-lat[y1]))/(xDif*yDif)
    else:
        return (fQ11+fQ21+fQ12+fQ22)/4.0
            
'''
Trilinear Interpolation
Reference: http://en.wikipedia.org/wiki/Trilinear_interpolation
'''        
def TriLinearInterpolate(depth0,lat0,lon0,t,depth,lat,lon,V):
    #import pdb; pdb.set_trace()
    #x0,x1,y0,y1,z0,z1 = math.floor(x),math.ceil(x),math.floor(y),math.ceil(y),math.floor(z),math.ceil(z)
    x0,x1 = FindLowAndHighIndices(depth0,depth)
    y0,y1 = FindLowAndHighIndices(lat0,lat)
    z0,z1 = FindLowAndHighIndices(lon0,lon)
    xd,yd,zd = 0.5,0.5,0.5
    xDif,yDif,zDif = depth[x1][0]-depth[x0][0],lat[y1][0]-lat[y0][0],lon[z1][0]-lon[z0][0]
    if xDif>0:
        xd = (depth0-depth[x0][0])/float(xDif)
    if yDif>0:
        yd = (lat0-lat[y0][0])/float(yDif)
    if zDif>0:
        zd = (lon0-lon[z0][0])/float(zDif)
        
    i1 = V[t,x0,y0,z0] * (1-zd)+ V[t,x0,y0,z1]*zd
    i2 = V[t,x0,y1,z0] * (1-zd)+ V[t,x0,y1,z1]*zd
    j1 = V[t,x1,y0,z0] * (1-zd)+ V[t,x1,y0,z1]*zd
    j2 = V[t,x1,y1,z0] * (1-zd)+ V[t,x1,y1,z1]*zd
    
    w1 = i1*(1-yd)+i2*yd
    w2 = j1*(1-yd)+j2*yd
    
    val = w1 * (1-xd) + w2 * xd
    return val