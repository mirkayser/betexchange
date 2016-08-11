#! /usr/bin/env python

"""trading tool"""

from IPython import embed

import numpy as np
from my.tools import closeTo 

np.set_printoptions(precision=3, threshold=50, linewidth=100)		

class Bets():

	def __init__(self,brate,lrate,commision=0.065,exchange_rate=1.1):
		
		self.brate = brate
		self.lrate = lrate
		self.comfactor = 1-commision
		self.exchange_rate=exchange_rate

	def get_backers_stake(self,liability):
		return np.round( liability / (self.lrate-1), 2 )

	def get_liability(self,stake):
		
		self.stake = np.round(stake,2)
		self.liability = np.round( stake*self.brate*(self.lrate-1) / (self.comfactor+self.lrate-1), 2 )
		self.bstake = self.get_backers_stake(self.liability)
		
		print self

	def get_stake(self,liability):
		
		self.liability = np.round(liability,2)
		self.bstake = self.get_backers_stake(self.liability)
		stake = liability*(self.comfactor+self.lrate-1) / ( self.brate*(self.lrate-1) )
		self.stake = np.round( stake, 2)
		
		print self
	
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


			
def main():
	print 'here starts main program'

		
if __name__ == "__main__":
    main()		

