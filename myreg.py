#! /usr/bin/env python

from IPython import embed
#embed() # this call anywhere in your program will start IPython

import sys, os, time, progressbar
import random
import numpy as np
import matplotlib.pyplot as mp
import matplotlib.gridspec as gridspec
from data_handle import Data_Handle, DataML

from pyik.performance import cached

np.set_printoptions(precision=3, threshold=50, linewidth=100)

class LinearRegression():
	
	def __init__(self):
		
		self.data = DataML()		
		self.minimized=False
		
	def init_training(self,alist):
		
		print 'initializing training:'
		self.runner_names,self.feature_names,self.features,self.result = self.data.get_lists(alist)
		
	def get_flength(self):
		return len(self.get_fnames())
		
	def get_fnames(self):
		return self.feature_names
			
	def fit(self,model,starts,lb=None,ub=None,export_pars=False):
		
		from my.fit import LikelihoodLinReg
		
		fit = LikelihoodLinReg(model,self.result,self.features)
		fit.minimize(starts,lower_bounds=lb, upper_bounds=ub)
		self.fit = fit	
		self.minimized=True
		
	def draw_residuals(self,verbose=False):
		
		from pyik.numpyext import profile,centers
		
		if not self.minimized: raise ValueError('LinReg not minimized (run self.fit())')
		
		mp.figure(num=2, figsize=(8, 6), dpi=80)
		mp.clf()
		gs1 = gridspec.GridSpec(1,1)
		ax1 = mp.subplot(gs1[0, 0])
		
		xs = self.result
		ys = self.result
		
		ys[ys==0] = 0.001
		
		yms= self.fit.fitted_model(self.features)
		res = (ys-yms)/np.sqrt(np.abs(ys))
		
		resavg,reserr,n,xedge = profile(xs, res, bins=100, range=None, sigma_cut=None)
		cxs,hw=centers(xedge)
		
		mask = np.isnan(resavg)==False
		cxs  = cxs[mask]
		resavg = resavg[mask]
		reserr = reserr[mask]
		
		ax1.plot(xs,res,marker='.',ls='',color='#B3B3B3')
		ax1.errorbar(cxs, resavg, yerr=reserr, fmt='o', c='g', capsize=0)
		ax1.axhline(0, c='#B3B3B3', ls='--')	

		ax1.set_title('residuals')
		ax1.set_xlabel(r'result', size='large')
		ax1.set_ylabel(r'$<\mathrm{(ys - ys_{m})/\sigma_{ys}}>$', size='large')
		mp.savefig('bsc-global_residuals.pdf')
	
	
	def test_prediction(self,alist,verbose=False):
		
		if not self.minimized: raise ValueError('LinReg not minimized, run self.fit()')
		
		print 'predicting results:'
		
		runner_names,feature_names,features,result = self.data.get_lists(alist)
		
		ys = result
		yms= self.fit.fitted_model(features)
		
		#goodness of prediction
		test = np.zeros(len(runner_names))
		
		pos = (ys>0) & (yms>0)
		neg = (ys<0) & (yms<0)
		
		test[pos] = 1
		test[neg] =-1
		
		#generate array
		a = np.array(zip(runner_names,ys,yms,test),dtype=[('name','S30'),('ys',float),('yms',float),('test',int)])
		
		#cut unwanted datapoints
		a = a[a['yms']>0.0]
		
		mask = (a['test']==1) | (a['test']==-1)
		ratio = len(a[mask])/float(len(a))
		
		if verbose:
			out = '\nprediction results runners:\n'
			for i in xrange(len(a)):
				out += '%s:  %.3f  %.3f  %d\n' % (a['name'][i], a['ys'][i], a['yms'][i],a['test'][i])
			print out
			
		print 'ratio:  %.3f of %d' % (ratio, len(a)) 
		return ratio

def split_samples(data):

	"""split in control, training sample"""
	np.random.shuffle(data)
	split = np.int(0.8*len(data))			
	train,control = np.split(data, [split])
	
	print '\n%d total samples:  (train=%d, control=%d)\n' % (len(data),len(train),len(control))
	
	return train,control

def model(features,pars):
	result = np.sum(pars*features,axis=1)
	return result

def main():
	print 'here starts main program'

		
	d = Data_Handle(load=1)
	
	ratios=[]
	for i in xrange(1):
	
		train,control = split_samples(d.alist)
	
		linreg = LinearRegression()
		linreg.init_training(train)		
		
		starts = np.ones(linreg.get_flength())
		linreg.fit(model,starts)
		print linreg.feature_names
		print linreg.fit
		#~ linreg.draw_residuals()
		
		ratio = linreg.test_prediction(control,verbose=0)
		
		ratios.append(ratio)
		
	print '\n',np.average(ratios)	
		
	mp.show()

if __name__ == "__main__":
    main()
