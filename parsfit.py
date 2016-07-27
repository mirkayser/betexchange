#! /usr/bin/env python

"""parameter study for analysis.py"""

from IPython import embed

import numpy as np
import cPickle as pickle
from analysis import Analysis
from my.tools import Timer,poolmap

np.set_printoptions(precision=3, threshold=50, linewidth=100)		

class ParsFit(object):
	
	def model(self,par,verbose=False):
		
		a = Analysis(limit=par[0],max_price=5,cut_pars=par[1:],verbose=False)
		
		if len(a.xtrain)<5:
			score,subset = np.nan,np.nan
		else:	
			scores = a.clf.cross_val_score_values(a.clf.clfs['ptree'], a.xtrain, a.ytrain, num_cv=5)
			score  = scores.mean()
			subset = a.clf.clfs['ptree'].get_size_subset_values(a.xtrain)
		
		if verbose: print 'score=%.2f, subset=%.2f  pars: %s' % (score,subset,str(par))
		
		return score,subset
	
	def __call__(self, par):
		
		score,subset = self.model(par)
		
		subset*=2
		result = -(score+subset)
		
		return result

	def Minimize(self, starts, lower_bounds=None, upper_bounds=None, method=None,
							 absolute_tolerance=1e-6, relative_tolerance=0.0,
							 stochastic_population=0, max_evaluations=None,
							 max_time=0, covarianceMethod="fast"):
	
		from pyik.fit import Minimizer
		
		starts = np.atleast_1d(starts)
	
		m = Minimizer()
		
		if not method is None: m.SetMethod(method)
		
		if not lower_bounds is None:
			if np.any(starts < lower_bounds):
				raise ValueError("A start value is smaller than its lower bound.")
			m.SetLowerBounds(lower_bounds)
		
		if not upper_bounds is None:
			if np.any(starts > upper_bounds):
				raise ValueError("A start value is larger than its upper bound.")
			m.SetUpperBounds(upper_bounds)
		
		m.SetAbsoluteTolerance(absolute_tolerance)
		m.SetRelativeTolerance(relative_tolerance)
		m.SetStochasticPopulation(stochastic_population)
		m.SetMaximumEvaluations(max_evaluations)
		m.SetMaximumTime(max_time)
		
		self.starts = starts
		self.pars = m(self, starts)
		self.result = self(self.pars)
		self.score,self.subset = self.model(self.pars)
		
		return np.squeeze(self.pars), self.result

	def __repr__(self):
		
		out = 'starts=%s\npars  =%s\n' %(self.starts,self.pars) 
		out += 'score=%.2f, subset=%.2f\n' % (self.score,self.subset)
		return out

def export_pars(fits):
	
	fname = 'parameters_analysis.pkl'
	
	pars = []
	for i,fit in enumerate(fits):
		pars.append(fit.pars)
	with open(fname,'wb') as outputfile:
		pickle.dump(pars,outputfile,pickle.HIGHEST_PROTOCOL)
	print '%s parameter sets written to %s' % (len(fits),fname)

def get_parsfits(args):
	
	starts,lb,ub = args
	
	fit = ParsFit()
	pars,result = fit.Minimize(starts,lower_bounds=lb, upper_bounds=ub,method='BOBYQA')
	score,subset= fit.score,fit.subset
	
	print fit
	
	return fit
	
def main():
	print 'here starts main program'

#parameters for unparallel fit
pars = [ 	[  0.22,     7.0e+01,4.0e+00,2.4e+01], #score=0.81, subset=0.19
					[  0.113,  	 7.0e+01,4.0e+00,2.4e+01], #score=0.78, subset=0.23
					[  2.500e-02,7.0e+01,4.0e+00,2.4e+01], #score=0.78, subset=0.38
					[  1.330e-02,7.0e+01,4.0e+00,2.4e+01]  #score=0.79, subset=0.45				 
				]

lb = [0.0,70, 4,24]
ub = [0.3,70, 4,24]


#parallelfit
args = [ [ pars[0],[0.2,  70, 4,24],ub ],  #score=0.84, subset=0.19
				 [ pars[1],[0.1,  70, 4,24],ub ],  #score=0.80, subset=0.28
				 [ pars[2],[0.025,70, 4,24],ub ],  #score=0.82, subset=0.58
				 [ pars[3],[0.01, 70, 4,24],ub ]  
				]

fits = poolmap(get_parsfits,args,numProcesses=2)

export_pars(fits)
	
	

