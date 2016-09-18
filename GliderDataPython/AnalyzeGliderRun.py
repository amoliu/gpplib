from gpplib.GliderFileTools import *
import random
from sets import Set
import gpplib
from gpplib.Utils import *
from gpplib.GenGliderModelUsingRoms import *
from gpplib.StateActionMDP import *
from gpplib.LatLonConversions import *
from gpplib.PseudoWayptGenerator import *
import datetime
import ftplib

import numpy as np


conf = GppConfig()

dataFileDir = conf.myDataDir + 'ProcessedWebbMatlabFormat/'
import os, sys

FileList = os.listdir(dataFileDir)

# Column numbers
m_present_time = 519 ;
m_heading = 477 ;
m_speed = 534 ;
m_depth = 397 ;
m_dist_to_wpt = 419 ;
m_time_til_wpt = 560 ;
m_gps_lat = 454 ;
m_gps_lon = 455 ;
m_gps_mag_var = 456 ;
m_gps_on = 458 ;
m_heading = 477 ;
m_initial_water_vx = 478 ;
m_initial_water_vy = 479 ;
m_final_water_vx = 437 ;
m_final_water_vy = 438 ;
m_lat = 500 ;
m_lon = 509 ;
m_roll = 526 ;
m_avg_climb_rate = 366 ;
m_avg_depth_rate = 367 ;
m_avg_dive_rate = 368 ;
m_avg_downward_inflection_time = 369 ;
m_avg_speed = 370 ;
m_certainly_at_surface = 383 ;
m_climb_tot_time = 387 ;
m_dive_tot_time = 421 ;
m_gps_dist_from_dr = 445 ;
m_gps_utc_day = 466 ;
m_gps_utc_hour = 467 ;
m_gps_utc_minute = 468 ;
m_gps_utc_month = 469 ;
m_gps_utc_second = 470 ;
m_gps_utc_year = 471 ;
c_wpt_lat = 238 ;
c_wpt_lon = 239 ;
m_mission_avg_speed_climbing = 512 ;
m_mission_avg_speed_diving = 513 ;
m_mission_start_time = 514 ;
m_pitch = 516 ;



data= np.loadtxt(c, delimiter=',', usecols=(0, 2), unpack=True)
