#! /usr/bin/env python

from IPython import embed
#embed() # this call anywhere in your program will start IPython

import sys, os
from optparse import OptionParser
import modules as mod


def main():
	print 'here starts main program'

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename",
                  help="FILE containing urls (FILE must be in the form filename.txt)", metavar="FILE")
(options, args) = parser.parse_args()

fname = options.filename
if fname:
	if not os.path.isfile(fname):	raise NameError('file ' + fname + ' does not exist!')
	else:
		with open(fname, 'rb') as input:
			string = input.read()
			urls = string.split("\n")[:-1]
elif len(args)<1:raise NameError("Usage: %s some_url")
else: urls=args

i=0
for url in urls:
	comand = 'gnome-terminal -e "./dataColection.sh ' + url + '"'
	#~ comand = './dataColection.sh ' + url + '&'
	os.system(comand)
	os.system('pid=$!')
	v = os.environ.get('$pid')
	
	i+=1
	if i>=5: break


