'''
This file creates risk and obstacle maps which will be used for our simulations. It will not
be using gpp_in_cpp for risk-map creation, and instead relies upon LatLonZ and MapTools for 
bathymetric information.
'''
import UseAgg
import numpy as np
import scipy.io as sio
from scipy.ndimage import gaussian_filter
from gpp_in_cpp import ImgMap
from gpp_in_cpp import ImgMapUtils
import matplotlib.pyplot as plt
import math
import shelve
import networkx as nx
import os
import gpplib

conf = gpplib.Utils.GppConfig()


figSaveDir = 'pngs'
try:
    os.mkdir(figSaveDir)
except:
    pass

ais_data  = sio.loadmat(conf.myDataDir + 'ais_data.mat')
