#! /usr/bin/env python

"""sklearn analysis example"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn import tree,neighbors
from sklearn.ensemble import RandomForestClassifier,ExtraTreesClassifier,BaggingClassifier

from data_handle import Data_Handle
from linreg import DataML, split_samples

from IPython import embed
#embed() # this call anywhere in your program will start IPython


def prepareData(data):
	
	limit=0.0
	
	runner_names,feature_names,features,result = DataML().get_lists(data)
	
	x1,x2,x3 = [],[],[]
	for i in xrange(len(features)):
		
		if result[i]>limit:
			x1.append(features[i])
		elif result[i]<-limit:
			x2.append(features[i])
		else:
			x3.append(features[i])
			
	x1= np.array(x1)
	x2= np.array(x2)
	x3= np.array(x3)
	y1= np.ones(len(x1))
	y2=-np.ones(len(x2))	
	y3= np.zeros(len(x3))	
	x = np.concatenate((x1, x2, x3), axis=0) # concatenate the samples
	y = np.concatenate((y1, y2, y3))
	
	print ' Samples Class 1: %i'%len(x1)
	print ' Samples Class 2: %i'%len(x2)
	print ' Samples Class 3: %i'%len(x3)
	print ''
	return x,y,feature_names


def main():
	print 'here starts main program'

d = Data_Handle(load=1)

dic = {'ld':[],'tree':[],'knn':[],'forest':[],'extraT':[],'bag-ld':[],'bag-knn':[],'bag-tree':[]}

for i in xrange(5):

	train,control = split_samples(d.alist)
	
	print 'training sample: ',len(train)
	x,y,fnames = prepareData(train)
	print 'control sample: ',len(control)
	xcontrol,ycontrol,fnames=prepareData(control)
	
	print '\ntest algorithms:'

	#ldac
	clf = LinearDiscriminantAnalysis()
	clf.fit(x,y)
	test =  clf.score(xcontrol,ycontrol)		# test points
	print 'LDAC: %.1f percent predicted'%(100*test) 
	dic['ld'].append(test)
	
	t = clf.predict(xcontrol)
	test,ynew=[],[]
	for i in xrange(len(t)):
		if t[i]==1:
			test.append(t[i])
			ynew.append(ycontrol[i])
	test = np.array(test)
	ynew = np.array(ynew)
	print 'LDAC (y>lim): %.1f percent predicted'%(100*len(test[test==ynew])/len(test))
	
	#decision tree 
	clf = tree.DecisionTreeClassifier()
	clf.fit(x,y)
	test =  clf.score(xcontrol,ycontrol)		# test points
	print 'ClassTree: %.1f percent predicted'%(100*test) 
	dic['tree'].append(test)
	
	#only use class prob = 1 
	p=clf.predict_proba(xcontrol)
	test,ynew = [],[]
	for i in xrange(len(p)):
		for j,cl in enumerate(clf.classes_):
			if p[i][j]==1:
				test.append(cl) 
				ynew.append(ycontrol[i])
	test=np.array(test)
	ynew=np.array(ynew)
	print 'ClassTree (p=1): %.1f percent predicted'%(100*len(test[test==ynew])/len(test)) 
	
	#knn
	clf = neighbors.KNeighborsClassifier()
	clf.fit(x,y)
	test =  clf.score(xcontrol,ycontrol)		# test points
	print 'KNN: %.1f percent predicted'%(100*test) 
	dic['knn'].append(test)
	
	#ensemble random forest
	clf = RandomForestClassifier(n_estimators=10)
	clf.fit(x,y)
	test =  clf.score(xcontrol,ycontrol)		# test points
	print 'ClassForest: %.1f percent predicted'%(100*test) 
	dic['forest'].append(test)
	
	#ensemble extremely randomized trees
	clf = ExtraTreesClassifier(n_estimators=10, max_depth=None,min_samples_split=1, random_state=0)
	clf.fit(x,y)
	test =  clf.score(xcontrol,ycontrol)		# test points
	print 'ExtraTree: %.1f percent predicted'%(100*test) 
	dic['extraT'].append(test)	
	
	#ensemble bagging LDAC
	clf = BaggingClassifier(LinearDiscriminantAnalysis(),max_samples=0.5, max_features=0.5)
	clf.fit(x,y)
	test =  clf.score(xcontrol,ycontrol)		# test points
	print 'Bag-LDAC: %.1f percent predicted'%(100*test) 
	dic['bag-ld'].append(test)	
	
	#ensemble bagging knn
	clf = BaggingClassifier(neighbors.KNeighborsClassifier(),max_samples=0.5, max_features=0.5)
	clf.fit(x,y)
	test =  clf.score(xcontrol,ycontrol)		# test points
	print 'Bag-KNN: %.1f percent predicted'%(100*test) 
	dic['bag-knn'].append(test)	

	#ensemble bagging tree
	clf = BaggingClassifier(tree.DecisionTreeClassifier(),max_samples=0.5, max_features=0.5)
	clf.fit(x,y)
	test =  clf.score(xcontrol,ycontrol)		# test points
	print 'Bag-Tree: %.1f percent predicted'%(100*test) 
	dic['bag-tree'].append(test)	
	
new={}
for k in dic.keys():
	new[k]={'avg':np.round(100*np.average(dic[k]),2), 'min':np.round(100*np.min(dic[k]),2)}

print ''
for item in new.items():	print item
