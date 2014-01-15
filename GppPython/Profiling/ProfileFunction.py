import sys
import optparse
import subprocess
from subprocess import Popen

''' @author: Arvind Pereira
	@summary: Script that helps profile debug code automatically.
	
	Sample Usage:
	python ProfileFunction.py -o debugSim.prof -p debugSim.png debugSimulation.py
	
	Here, debugSim.prof is the file we want to store the cProfile output to.
	debugSim.png is the name of the call-graph heat-map.
	debugSimulation.py is the file being profiled.
'''
parser = optparse.OptionParser(
	usage="\n\t%prog [options] [file] ...")
parser.add_option(
	'-o','--output', metavar='FILE',
	type="string", dest="output",
	help="output cProfile.profile")
parser.add_option(
	'-p','--png', metavar='FILE',
	type="string", dest="pngfile",
	help="output pngfile")


(options, args) = parser.parse_args(sys.argv[1:])

print options, args
if len(args):
    #p = Popen(["python -m cProfile -o %s %s"%(options['output'],args[0])], bufsize=bufsize,stdin=PIPE, stdout=PIPE, close_fds=True)
    try:
        retcode = subprocess.call("python -m cProfile -o Profiling/%s %s"%(options.output,args[0]),shell=True)
    except OSError, e:
        print >>sys.stderr, "Execution failed:", e
	sys.exit(-1)
    # Try to create a graph using pstats and so on...
    try:
        retcode2 = subprocess.call("python gprof2dot.py -f pstats Profiling/%s | dot -Tpng -o Profiling/%s"%(options.output,options.pngfile),shell=True)
    except OSError, e:
        print >>sys.stderr, "Execution failed:", e
        sys.exit(-2)
	print 'Stored all Profiling information in the directory Profiling. Look for %s for a heatmap.'%(output.pngfile)
