#!/usr/bin/env python

import re

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
	

states = readStates( 'states.txt' )
