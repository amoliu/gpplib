from collections import namedtuple

class PlannerResult:
    def __init__(self,**kwargs):
        self.PlannerType = ''
        self.Result = {}
        self.Result['DescStr'] = []
        self.Result['Risk'], self.Result['pathLength'], self.Result['Time'] = [], [], []
        self.Result['numHops'], self.Result['distFromGoal'], self.Result['CollisionReason'] = [], [], []
        self.Result['isSuccess'], self.Result['finalLoc'], self.Result['pathLen'] = [], [], []
        self.Result['Successes'], self.Result['Collisions'] = [], []
        self.Result['start'], self.Result['goal'] = [], []
        if kwargs.has_key('PlannerType'):
            self.PlannerType = kwargs['PlannerType']
        self.totResults = 0

    def UpdateWithResultOfRun(self,**kwargs):
        if kwargs.has_key('start'):
            self.Result['start'].append(kwargs['start'])
        if kwargs.has_key('goal'):
            self.Result['goal'].append(kwargs['goal'])
        if kwargs.has_key('Risk'):
            self.Result['Risk'].append(kwargs['Risk'])
        if kwargs.has_key('Time'):
            self.Result['Time'].append(kwargs['Time'])
        if kwargs.has_key('numHops'):
            self.Result['numHops'].append(kwargs['numHops'])
        if kwargs.has_key('distFromGoal'):
            self.Result['distFromGoal'].append(kwargs['distFromGoal'])
        if kwargs.has_key('finalLoc'):
            self.Result['finalLoc'].append(kwargs['finalLoc'])
        if kwargs.has_key('pathLen'):
            self.Result['pathLen'].append(kwargs['pathLen'])
        if kwargs.has_key('DescStr'):
            self.Result['DescStr'].append(kwargs['DescStr'])

        if kwargs.has_key('isSuccess'):
            self.Result['isSuccess'].append(kwargs['isSuccess'])
            if kwargs['isSuccess']:
                self.Result['Successes'].append(1)
            else:
                self.Result['Successes'].append(0)
        if kwargs.has_key('CollisionReason'):
            self.Result['CollisionReason'].append(kwargs['CollisionReason'])
            if kwargs['CollisionReason'] == 'Obstacle':
                self.Result['Collisions'].append(1)
            else:
                self.Result['Collisions'].append(0)
        self.totResults += 1

    def ComputeTotAvg(self,resArr):
        totalR, avgR, numR = 0., 0., 0.
        for r in resArr:
            totalR+=r
            numR +=1
        if numR > 0:
            avgR = totalR/numR
        return totalR, avgR

        
    def ComputeTotalsAndAverages(self):
        self.Totals = namedtuple('Totals',['Risk','Time','numHops','distFromGoal','Successes','Collisions','pathLen' ])
        self.Averages = namedtuple('Averages',['Risk','Time','numHops','distFromGoal','Successes','Collisions','pathLen'])
        
        rT,rA = self.ComputeTotAvg(self.Result['Risk'])
        tT,tA = self.ComputeTotAvg(self.Result['Time'])
        hT,hA = self.ComputeTotAvg(self.Result['numHops'])
        dT,dA = self.ComputeTotAvg(self.Result['distFromGoal'])
        sT,sA = self.ComputeTotAvg(self.Result['Successes'])
        cT,cA = self.ComputeTotAvg(self.Result['Collisions'])
        pT,pA = self.ComputeTotAvg(self.Result['pathLen'])
        self.Totals.Risk,self.Totals.Time,self.Totals.numHops,self.Totals.distFromGoal, \
            self.Totals.Successes, self.Totals.Collisions, self.Totals.pathLen = rT,tT,hT,dT,sT,cT,pT
        self.Averages.Risk, self.Averages.Time, self.Averages.numHops, self.Averages.distFromGoal, \
            self.Averages.Successes, self.Averages.Collisions, self.Averages.pathLen = rA,tA,hA,dA,sA,cA,pA
        return self.Totals, self.Averages
