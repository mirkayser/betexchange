#! /usr/bin/env python

"""sklearn analysis"""

import numpy as np
from sklearn import cross_validation

from data_handle import Data_Handle
from classifier import *

from IPython import embed
#embed() # this call anywhere in your program will start IPython

np.set_printoptions(precision=3, threshold=50, linewidth=100)		

class Analysis():
	
	def __init__(self):
		
		#load datalist from file
		datalist = Data_Handle(load=1).get_datalist()
		
		#~ #randomize sample
		#~ np.random.shuffle(datalist)
		
		#get lists (names,features,etc...)
		runner_names,feature_names,features,result = DataML().get_lists(datalist)
		
		#prepare data for classifiers
		self.x,self.y = prepareData(features,result,limit=0.1)
		
		#split in train and test samples (not random!!!)
		self.xtrain,self.xcontrol,self.ytrain,self.ycontrol = cross_validation.train_test_split(self.x,self.y,test_size=0.2,random_state=42)
		print 'Samples:\ntrain: %d\ncontrol: %d\n' % (len(self.x),len(self.xcontrol))	
		
		self.clf = Classifier()

	def fit(self):
	
		self.clf.fit(self.xtrain,self.ytrain)
		self.clf.performance(self.xcontrol,self.ycontrol)
	
			
def main():
	print 'here starts main program'

analysis = Analysis()
analysis.fit()


#~ #analize single event
#~ data = [datalist[0]]		
				
#~ #get lists (names,features,etc...)
#~ runner_names,feature_names,features,result = DataML().get_lists(data)	
	
#~ #prepare data for classifiers
#~ x = np.array(features)

#~ c_ym  = clf.clfs['combi'].predict(x) 
#~ p_ym,p_pm = clf.clfs['ptree'].predict_proba(x)

#~ c_ym[np.isnan(c_ym)] = 0
#~ p_ym[np.isnan(p_ym)] = 0
#~ p_pm[np.isnan(p_pm)] = 0

#~ array = np.array(zip(runner_names,c_ym,p_ym,p_pm),dtype=[('name','S30'),('c_ym',int),('p_ym',int),('p_pm',float)])

#~ array[::-1].sort(order=['p_ym','p_pm'])


#~ for item in array:
	#~ print item




	
	

