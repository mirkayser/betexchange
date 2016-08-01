#! /usr/bin/env python

from IPython import embed
#embed() # this call anywhere in your program will start IPython

import sys, os, time, progressbar
from optparse import OptionParser


def main():
	print 'here starts main program'

parser = OptionParser()
parser.add_option("-n", "--numRuns", dest="numRuns", default='3',
                  help="number of runs to be started", metavar="FILE")
(options, args) = parser.parse_args()
numRuns = int(options.numRuns)

for i in xrange(numRuns):
	
	#~ comand = 'gnome-terminal -e "./crawl.py -t 60,90"'	#close terminal upon termiation of process
	comand = 'gnome-terminal -x bash -c "./crawl.py --cachenum %d -t 60,90 && bash"' % i	#keep terminal open
	os.system(comand)
	
	print 'waiting to start run %d:' % (i+2)
	bar = progressbar.ProgressBar()	
	for j in bar(xrange(1800)):
		time.sleep(1)
		
print 'finished'


