#! /usr/bin/env python

from IPython import embed
#embed() # this call anywhere in your program will start IPython

import sys, os
import pickle
import modules as mod

filename = '01:12(AUS).pkl'
if os.path.isfile(filename):	
	with open(filename, 'rb') as input:
		event = pickle.load(input)
		
embed()
		#~ 
#~ if os.path.isfile('data.pkl'):	
	#~ with open('data.pkl', 'rb') as input:
		#~ event = pickle.load(input)
