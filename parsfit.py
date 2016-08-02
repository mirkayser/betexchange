#! /usr/bin/env python

"""parameter study for analysis.py"""

from IPython import embed

import numpy as np
import cPickle as pickle
from analysis import Analysis
from my.tools import Timer,poolmap

np.set_printoptions(precision=3, threshold=50, linewidth=100)		

class ParsFit(object):
	
	def model(self,pars,verbose=False): 

		self.cut_pars = [ 60,4,24  ]
		
		a = Analysis(limits=pars,max_price=5,cut_pars=self.cut_pars,verbose=False)
		
		if len(a.xtrain)<5:
			score,subset = np.nan,np.nan
		else:	
			scores = a.clf.cross_val_score_values(a.clf.clfs['ptree'], a.xtrain, a.ytrain, num_cv=5)
			score  = scores.mean()
			subset = a.clf.clfs['ptree'].get_size_subset_values(a.xtrain)
		
		if verbose: print 'score=%.2f, subset=%.2f  pars: %s' % (score,subset,str(pars))
		
		
		return score,subset
	
	def __call__(self, par):
		
		score,subset = self.model(par,verbose=0)
		
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
	
	#~ print fit.cut_pars
	print fit
	
	return fit
	
def main():
	print 'here starts main program'

starts = 	[ [0.1, 0.3],
						[0.2, 0.5],
						[0.2, 1.0],
						[0.2, 2.5],
						]

args = []						
for item in starts:
		
	lb = [ 0.1,        item[1]    ]
	ub = [ item[1]/2., item[1] 		]
	
	args.append([item,lb,ub])

#~ fit = get_parsfits(args[0])
fits = poolmap(get_parsfits,args,numProcesses=2)

export_pars(fits)
	
	

