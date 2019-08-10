#! /usr/bin/env python

"""trading tool"""

from IPython import embed

import numpy as np
import matplotlib.pyplot as mp
import matplotlib.gridspec as gridspec
from my.tools import closeTo 

np.set_printoptions(precision=3, threshold=50, linewidth=100)		

class Lay_Bets():

	def __init__(self,commision=0.065,exchange_rate=1):
		
		self.comfactor = 1-commision
		self.exchange_rate=exchange_rate

	def set_rates(self,brate,lrate):
		self.brate = brate
		self.lrate = lrate
		
	def get_backers_stake(self,liability):
		return np.round( liability / (self.lrate-1), 2 )

	def get_liability(self,stake,verbose=True):
		
		self.stake = np.round(stake,2)
		self.liability = np.round( stake*self.brate*(self.lrate-1) / (self.comfactor+self.lrate-1), 2 )
		self.bstake = self.get_backers_stake(self.liability)
		
		if verbose:	print self
		
		return self.liability

	def get_stake(self,liability,verbose=True):
		
		self.liability = np.round(liability,2)
		self.bstake = self.get_backers_stake(self.liability)
		stake = liability*(self.comfactor+self.lrate-1) / ( self.brate*(self.lrate-1) )
		self.stake = np.round( stake, 2)
		
		if verbose:	print self
		
		return self.stake
	
	def get_profit_laywin(self):
		return np.round( self.bstake*self.comfactor - self.stake, 2)
	
	def get_profit_backwin(self):
		return np.round( self.stake*(self.brate-1) - self.liability, 2)
	
	def __repr__(self):
			
		out = 'lay rate =%6.2f, bstake=%6.2f (liability=%6.2f)\n' % (self.lrate,self.bstake,self.liability) 
		out+= 'back rate=%6.2f,  stake=%6.2f ($%6.2f)\n' % (self.brate,self.stake,self.stake*self.exchange_rate)
		out+= '-> profit lay =%6.2f\n' % (self.get_profit_laywin())
		out+= '-> profit back=%6.2f\n' % (self.get_profit_backwin())
		
		return out

	def get_stakes_50(self,liability=50,verbose=True):
		
		stake = self.get_stake(liability,verbose=False)
		stake = np.round(stake*self.exchange_rate,0) /self.exchange_rate
		liability = self.get_liability(stake,verbose=verbose)
		

			
def main():
	print 'here starts main program'

	b = Bets()
	diffs = np.linspace(-0.1,0.1,201)
	
	brates,lrates,profits = [],[],[]
	brate=1.01
	while brate<3:
		
		for d in diffs:
			
			lrate = brate+d
			
			if lrate<1.01: continue
			
			b.set_rates(brate,lrate)
			b.get_stake(50,verbose=False)
			profit = b.get_profit_laywin()
			
			brates.append(brate)
			lrates.append(lrate)
			profits.append(profit)
		
		brate+=.01
	
	diffs = [ brates[i]-lrates[i] for i in xrange(len(brates)) ]
	array = np.array(zip(brates,lrates,diffs,profits),dtype=[('brate',float),('lrate',float),('diff',float),('profit',float)])
	
	brates,min_diffs = [],[]
	np.sort(array,order=['brate','profit'])
	a = array[array['profit']>0]
	for item in a:
		tmp = a[a['brate']==item['brate']]
		
		min_diff = np.min(tmp['diff'])
		
		brates.append(item['brate'])
		min_diffs.append(min_diff)
	
	mp.figure(num=1, figsize=(8, 6), dpi=80)
	mp.clf()
	gs1 = gridspec.GridSpec(1,1)
	ax1 = mp.subplot(gs1[0, 0])
	
	ax1.plot(brates,min_diffs,marker='',ls='-',c='r',label='')
	
	#~ ax1.set_title(r'cashflow globalfit ($\sigma=%d$)' % self.sigma)
	ax1.set_xlabel(r'back rate', size='large')
	ax1.set_ylabel(r'difference', size='large')
	#~ ax1.set_xlim(left=np.min(x)-.5,right=np.max(x)+.5)
	#~ mp.savefig('cf_globalfit_%dsigma.pdf' % self.sigma)
	
	mp.show()	
	
		
if __name__ == "__main__":
    main()		

