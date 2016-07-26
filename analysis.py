#! /usr/bin/env python

"""sklearn analysis"""

import datetime

import numpy as np
import cPickle as pickle
from sklearn import cross_validation
from optparse import OptionParser

from data_handle import Data_Handle
from classifier import *

from IPython import embed
#embed() # this call anywhere in your program will start IPython

np.set_printoptions(precision=3, threshold=50, linewidth=100)		

def create_dummy_files(fnames):
	"""generate dummy analysis events from complete events"""
	
	for fname in fnames:
		
		with open(fname,'rb')as inputfile: 
			
			event = pickle.load(inputfile)
			
			for k in event['data'].keys():
				
				new_data = []
				for item in event['data'][k]:
					
					if ( event['time_e'] - item[0] ) > datetime.timedelta(minutes=35):
						new_data.append(item)
				event['data'][k] = new_data
				
		with open(fname,'wb') as outputfile: 
			pickle.dump(event,outputfile,pickle.HIGHEST_PROTOCOL)		
			

class Analysis():
	
	def __init__(self,limit,max_price):
		
		print 'fitting methods to dataset:\n'
		
		self.limit=float(limit)
		self.max_price=float(max_price)
		
		#load datalist from file
		datalist = Data_Handle().load_data().get_datalist()
		
		#randomize sample
		np.random.shuffle(datalist)
		
		#get lists (names,features,etc...)
		runner_names,feature_names,features,result = DataML().get_lists(datalist,max_price=self.max_price)
		
		#prepare data for classifiers
		self.x,self.y = prepareData(features,result,limit=self.limit)
		
		#split in train and test samples (not random!!!)
		self.xtrain,self.xcontrol,self.ytrain,self.ycontrol = cross_validation.train_test_split(self.x,self.y,test_size=0.2,random_state=42)
		print 'Samples (limit=%.2f, max_price=%.1f):\ntrain: %d\ncontrol: %d\n' % (self.limit,self.max_price,len(self.x),len(self.xcontrol))	
		
		self.clf = Classifier()

	def fit(self):
	
		self.clf.fit(self.xtrain,self.ytrain)
		self.clf.performance_values(self.xcontrol,self.ycontrol)

	def predict(self,link,data,verbose=True):			
		
		out = ''
		
		#get lists (names,features,etc...)
		runner_names,feature_names,features,result = DataML().get_lists([data],max_price=self.max_price)	
		
		#skip event if not enough data
		if len(features)==0:
			print 'WARNING: not enough usable data to predict event\n'
					
		#classification
		else:
		
			#prepare data for classifiers
			x = np.array(features)
			
			c_ym  = analysis.clf.clfs['combi'].predict(x) 
			t_ym,t_pm = analysis.clf.clfs['ptree'].predict_proba(x)
			k_ym,k_pm = analysis.clf.clfs['pknn'].predict_proba(x)
			
			c_ym[np.isnan(c_ym)] = 0
			t_ym[np.isnan(t_ym)] = 0
			t_pm[np.isnan(t_pm)] = 0
			k_ym[np.isnan(k_ym)] = 0
			k_pm[np.isnan(k_pm)] = 0
			
			#prediction possible
			if np.any(c_ym)!=0 or np.any(t_ym)!=0 or np.any(k_ym)!=0:
				
				price = x[:,feature_names.index("last")]
				
				array = np.array(zip(runner_names,c_ym,t_ym,t_pm,k_ym,k_pm,price),dtype=[('name','S30'),('c_ym',int),('t_ym',int),('t_pm',float),('k_ym',int),('k_pm',float),('price',float)])
							
				#~ array[::-1].sort(order=['t_ym','t_pm'])	#reverse sort
				array.sort(order=['price'])
				
				#output succesful prediction
				out += 'url:  %s\n' % link
				out += '%s    %s   %s          %s          %s\n' %(' '.ljust(20,' '), 'c','t','k','price')
				for item in array:
					out += '%s:  %2d  %2d (%.2f)  %2d (%.2f)   %5.2f\n' % (item['name'][:20].ljust(20,' '),item['c_ym'],item['t_ym'],item['t_pm'],item['k_ym'],item['k_pm'],item['price'])
			
			else:
				print 'WARNING: no prediction possible (%s)\n' % link
				
			return out  
			
	def cross_validation(self):
		
		self.clf.cross_validation_clfs_values(self.x,self.y,self.xcontrol,num_cv=5)
			
def main():
	print 'here starts main program'

#parse options
parser = OptionParser()
parser.add_option("--cv", dest="cv", action="store_true", default=False,
                  help="cross validate methods with dataset")
(options, args) = parser.parse_args()

#init analysis object
analysis = Analysis(limit=0.0,max_price=5)

if options.cv:
	#perform cross validation
	analysis.cross_validation()

else:
	#get filenames
	if len(args)<1:
		raise NameError("Usage: %s /path_some_file")
	else: fnames=args
	
	#create dummy files for testing purpose
	if fnames[0].split("/")[1]=='test':	create_dummy_files(fnames)

	#train clf with existing data
	analysis.fit()

	#predict outcome events
	print 'Predicting outcome events:\n'

	#load event data from fnames
	dh = Data_Handle().cut_raw_data(fnames=fnames,analysis=True)
	linklist = dh.get_linklist()
	datalist = dh.get_datalist()
	
	outputs = []
	for i in xrange(len(datalist)):
		
		data = datalist[i]
		link = linklist[i]
		
		out = analysis.predict(link,data)
		
		if out!='': outputs.append(out)
	
	if len(outputs)>0:
		print '\n\nEvents with prediction:\n'
		for i,output in enumerate(outputs):
			print 'event #%d:' % i
			print output
			
		print  '%d of %d events with prediction' % (len(outputs),len(datalist))
	
	#~ embed()
	
	

