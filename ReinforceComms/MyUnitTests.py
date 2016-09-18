import unittest
from MapTools import *


class TestDistanceCalculator(unittest.TestCase):
    def setUp(self):
        self.lat1,self.lon1 = 34.442659,-120.461171
        self.lat2, self.lon2 = 31.753746,-116.754850
        self.distFromGE = 456700.85
        latN=33.25; latS=32.00
        er = EarthRadius((latN+latS)/2.)
        self.R = er.R
        

    def test_DistanceCalculator(self): # Unit test for distance calculations
        
        dc = DistCalculator(self.R)
        distCalculated = dc.GetDistBetweenLocs(self.lat1,self.lon1,self.lat2,self.lon2 ) #33.571264, -118.246228, 33.485031, -118.415274)
        errorPercent = (self.distFromGE-distCalculated)/self.distFromGE * 100.
        print 'DistGE=%f, DistCalculated:%f, Error in Calculation =%.5f'%(self.distFromGE,distCalculated,self.distFromGE-distCalculated)
        print 'Error =%.2f%%'%(errorPercent)

        self.assertTrue(errorPercent<0.1)
        
        
if __name__ == '__main__':
    unittest.main()