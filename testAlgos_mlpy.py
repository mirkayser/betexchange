#! /usr/bin/env python

"""mlpy analysis example"""

import numpy as np
import matplotlib.pyplot as plt
import mlpy

from data_handle import Data_Handle
from linreg import DataML, split_samples

from IPython import embed
#embed() # this call anywhere in your program will start IPython


def prepareData(data):
	
	runner_names,feature_names,features,result = DataML().get_lists(data)
	
	x1,x2 = [],[]
	for i in xrange(len(features)):
		
		if result[i]>0:
			x1.append(features[i])
		elif result[i]<0:
			x2.append(features[i])
			
	x1=np.array(x1)
	x2=np.array(x2)
	y1=np.ones(len(x1))
	y2=-np.ones(len(x2))	
	x = np.concatenate((x1, x2), axis=0) # concatenate the samples
	y = np.concatenate((y1, y2))
	print ' Samples Class 1: %i'%len(x1)
	print ' Samples Class 2: %i'%len(x2)
	print ''
	return x,y,feature_names


def main():
	print 'here starts main program'

d = Data_Handle(load=1)

dic = {'ld':[],'perc':[],'elnet':[],'da':[],'golub':[],'knn':[],'tree':[]}

for i in xrange(1):

	train,control = split_samples(d.alist)
	
	print 'training sample: ',len(train)
	x,y,fnames = prepareData(train)
	print 'control sample: ',len(control)
	xcontrol,ycontrol,fnames=prepareData(control)
	
	print '\ntest algorithms:'
	 
	ld = mlpy.LDAC()
	ld.learn(x,y)
	test =  ld.pred(xcontrol)		# test points
	print 'LDAC: %.1f percent predicted'%(100*len(test[test==ycontrol])/float(len(test))) 
	dic['ld'].append(100*len(test[test==ycontrol])/float(len(test)))
	
	perc = mlpy.Perceptron()
	perc.learn(x,y)
	test =  perc.pred(xcontrol)		# test points
	print 'Perceptron: %.1f percent predicted'%(100*len(test[test==ycontrol])/len(test)) 
	dic['perc'].append(100*len(test[test==ycontrol])/len(test))
	
	elnet = mlpy.ElasticNetC(lmb=0.01, eps=0.001)
	elnet.learn(x,y)
	test =  elnet.pred(xcontrol)		# test points
	print 'Elastic Net: %.1f percent predicted'%(100*len(test[test==ycontrol])/len(test)) 
	dic['elnet'].append(100*len(test[test==ycontrol])/len(test))
	
	da =mlpy.DLDA(delta=0.1)
	da.learn(x,y)
	test =  da.pred(xcontrol)		# test points
	print 'DLDA: %.1f percent predicted'%(100*len(test[test==ycontrol])/len(test))
	dic['da'].append(100*len(test[test==ycontrol])/len(test))
	
	golub =mlpy.Golub()
	golub.learn(x,y)
	test =  golub.pred(xcontrol)		# test points
	print 'Golub: %.1f percent predicted'%(100*len(test[test==ycontrol])/len(test))
	dic['golub'].append(100*len(test[test==ycontrol])/len(test))
	
	knn = mlpy.KNN(k=7)
	knn.learn(x,y)
	test =  knn.pred(xcontrol)		# test points
	print 'KNN: %.1f percent predicted'%(100*len(test[test==ycontrol])/len(test))
	dic['knn'].append(100*len(test[test==ycontrol])/len(test))
	
	tree = mlpy.ClassTree(stumps=0,minsize=100)
	tree.learn(x,y)
	test =  tree.pred(xcontrol)		# test points
	print 'ClassTree: %.1f percent predicted'%(100*len(test[test==ycontrol])/len(test))
	dic['tree'].append(100*len(test[test==ycontrol])/len(test))
	
	rank = mlpy.rfe_w2(x,y,p=0,classifier=ld)
	print ''
	print fnames
	print rank

new={}
for k in dic.keys():
	new[k]={'avg':np.round(np.average(dic[k]),2), 'min':np.round(np.min(dic[k]),2)}

print ''
for item in new.items():	print item
