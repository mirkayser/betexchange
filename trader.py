#! /usr/bin/env python

"""trading tool"""

from IPython import embed

import numpy as np
from my.tools import closeTo 

np.set_printoptions(precision=3, threshold=50, linewidth=100)		

def lay(lrate,brate,bstake=2):
	
	lrate,brate,bstake = float(lrate),float(brate),float(bstake)
	
	liability = bstake*(lrate-1)
	
	stake = (bstake+liability) / brate
	bprofit = stake*(brate-1)
	
	#calculate profit
	bwin =  bprofit-liability
	lwin = bstake - stake
	if not closeTo(bwin,lwin,eps=0.1): raise ValueError('results of winning back/lay unequal!')
	
	out = 'lay rate =%6.2f, bstake=%6.2f (liability=%6.2f)\n' % (lrate,bstake,liability) 
	out+= 'back rate=%6.2f,  stake=%6.2f\n' % (brate,stake)
	out+= '-> profit=%6.2f  (min_bank=%6.2f)\n' % (bwin,stake+liability)
	
	print out

def back(brate,lrate,stake=2):
	
	lrate,brate,stake = float(lrate),float(brate),float(stake)
	
	bprofit = stake*(brate-1)
	
	bstake = stake + ( bprofit - stake*(lrate-1) ) / lrate
	liability = bstake*(lrate-1)
		
	#calculate profit
	bwin =  bprofit-liability
	lwin = bstake - stake
	if not closeTo(bwin,lwin,eps=0.1): raise ValueError('results of winning back/lay unequal!')
	
	out = '' 
	out+= 'back rate=%6.2f,  stake=%6.2f\n' % (brate,stake)
	out+= 'lay rate =%6.2f, bstake=%6.2f (liability=%6.2f)\n' % (lrate,bstake,liability)
	out+= '-> profit=%6.2f  (min_bank=%6.2f)\n' % (bwin,stake+liability)
	
	print out
			
def main():
	print 'here starts main program'

		
if __name__ == "__main__":
    main()		

