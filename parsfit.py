#! /usr/bin/env python

"""parameter study for analysis.py"""

from IPython import embed

import numpy as np
from analysis import Analysis

from my.tools import Timer

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
		
		score,subset = self.model(par,verbose=True)
		
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
		
		self.pars = m(self, starts)
		self.result = self(self.pars)
		self.score,self.subset = self.model(self.pars)
		
		return np.squeeze(self.pars), self.result

	def __repr__(self):
		
		out = 'score=%.2f, subset=%.2f\npars=' % (self.score,self.subset)
		for i in xrange(len(pars)):
			if i==0: 							out += '[%s,' % pars[i]
			elif i==len(pars)-1: 	out += '%s]' % pars[i]
			else:									out += '%s,' % pars[i]
		return out

def main():
	print 'here starts main program'


pars = [ [0.2,70.0,3.0,24.0], #score=0.84, subset=0.19
				 [0.1,70.0,3.9,23.5], #score=0.80, subset=0.28
				 [0.0,70.0,4.0,23.9]  #score=0.82, subset=0.58
				]

lb = [0.0,69, 3,23]
ub = [0.3,70, 5,25]

starts = [.0,70, 4,24]

fit = ParsFit()
pars,result = fit.Minimize(starts,lower_bounds=lb, upper_bounds=ub,method='BOBYQA')
score,subset= fit.score,fit.subset

print '\n',fit
