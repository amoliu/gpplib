import re, sys, os

def readStates( fileName ):
    states = {}
    stF = open( fileName, 'r' )
    if stF:
        stLines = stF.readlines()
        for line in stLines:
            m = re.match( '([0-9]+)=([0-9]+),([0-9]+),([0-9]+)', line )
            if m:
                state = int( m.group(1) )
                t,x,y = int( m.group(2) ), int( m.group(3) ), int( m.group(4) )
                print '%d,%d,%d,%d'%( state, t, x, y )
                states[ state ] = (t,x,y)
        stF.close()
    return states


numThreads = 10
states = readStates('states.txt')
numStates= len(states)
processState = numStates/numThreads

for i in range(numThreads):
    yy,mm,dd = 2013, 8, 13
    sState = (numStates*i)/numThreads; eState = (numStates*(i+1))/numThreads -1
    cmd = 'nohup python getTransitionModelsNS_GP_Parallel.py %04d %02d %2d %04d %2d %2d %d %d &'%(yy,mm,dd,yy,mm,dd,sState,eState)
    print cmd
    os.system(cmd)
