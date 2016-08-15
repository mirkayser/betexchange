#! /usr/bin/env python

"""trading tool"""

from IPython import embed

import numpy as np
from my.tools import closeTo 

np.set_printoptions(precision=3, threshold=50, linewidth=100)		

class Bets():

	def __init__(self,commision=0.065,exchange_rate=1.1):
		
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

	def get_stakes_50(self,liability=50):
		
		stake = self.get_stake(liability,verbose=False)
		stake = np.round(stake*self.exchange_rate,0) /self.exchange_rate
		liability = self.get_liability(stake,verbose=True)
		

			
def main():
	print 'here starts main program'

	b = Bets()
	b.set_rates(2.87,2.86)
	b.get_stakes_50()
		
if __name__ == "__main__":
    main()		

