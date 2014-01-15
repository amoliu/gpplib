import gpplib
import time
from gpplib.LatLonConversions import *
from simplekml import *

WebbLonLatlist = [
(-11835.3100,    3331.4822),
(-11833.6180,    3330.4184),
(-11831.9260,    3330.4184),
(-11830.2340,    3329.3546),
(-11828.5420,    3328.2908),
(-11826.8500,    3327.2270),
(-11825.1580,    3327.2270),
(-11823.4660,    3326.1632),
(-11821.7740,    3326.1632),
(-11820.0820,    3327.2270),
(-11820.0820,    3328.2908),
(-11835.3100,    3331.4822),
]

t1= time.time()
t = t1
timeList = []
# make up some surfacing times
for ll in WebbLonLatlist:
    t += 3600;
    timeList.append(t)
w_lon,w_lat = zip(*WebbLonLatlist); w_lon = list(w_lon); w_lat = list(w_lat)
