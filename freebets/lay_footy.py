#! /usr/bin/env python

from IPython import embed
#embed() # this call anywhere in your program will start IPython

import sys,os,time,re,datetime,progressbar
import numpy as np
from optparse import OptionParser
#~ from operator import itemgetter
#~ from my.spider import Spider
#~ from my.tools import *
#~ from pyik.performance import cached,pmap

from betmod import *
from betcalc import Lay_Bets


def compare(data,limit=0.1):
	
	success=False
			
	b = Lay_Bets()		
	out='\nResult:\n'	
	for item in data:
		
		backs=item['rates']
		lays =item['lay'] 
		names =item['items'] 
		for i in xrange(3):
			
			if lays[i]==None: continue
			
			for k in backs[i].keys():
				
				name = names[i]
				lay = lays[i]
				back= backs[i][k]
					
				diff = lay - back
			
				if back<1.5 and diff>0: continue
				if diff > limit: continue
				
				b.set_rates(back,lay)
				b.get_stake(50,verbose=False)
				profit = b.get_profit_laywin()
				
				if k!='Sky Bet': continue
				
				out += '%5.2f  (%5.2f)  %s  (%s)  back=%5.2f  lay=%5.2f  -> %s (%s - %s)\n' % (diff,profit,name.ljust(5," "),k,back,lay,item['start'],item['market-name'],item['competition'])
			
				if diff<0:
					success=True
		
	if out=='': out = 'WARNING: no item fits specifications'
	
	print out
	
	return success
		
def main():
	print ''

urls = []

if 1:
	urls = [
				#'http://www.oddschecker.com/football/english/premier-league',
				'http://www.oddschecker.com/football/english/championship',
				'http://www.oddschecker.com/football/english/league-1',
				'http://www.oddschecker.com/football/english/league-2',
				#'http://www.oddschecker.com/football/scottish/premiership'
				]	

for url in urls:
		
	exch = get_data_exchange()
	book = sportsbooks([url],exch=None)
	
	#join datasets
	print '\njoin datasets'
	data = []
	for b in book:
		found=False
		for e in exch:
			
			if re.search(b['market-name'],e['market-name'],re.IGNORECASE):
				b['competition'] = e['competition']
				b['start'] = e['start']
				b['items'] = ['home','X','away']			
				b['lay'] = e['rates']
				
				data.append(b)
				found=True
				break
	
		if not found: print 'not found: ',b['market-name']
			
	print '%d/%d matched' % (len(data),len(book))
						
	success = compare(data,limit=0.0)
	
	b = Lay_Bets(exchange_rate=1)
	embed()
	
	
	
	#~ return success


#~ if __name__ == "__main__":

	#~ #parse options
	#~ parser = OptionParser()
	#~ parser.add_option("-r","--repeat", dest="repeat", default=False,
	                  #~ help="repeat x times")
	#~ (options, args) = parser.parse_args()

	#~ if not options.repeat:
		#~ success = main()	
		#~ embed()
		
	#~ else:
		#~ count=0
		#~ while count<int(options.repeat):
			
			#~ print 'scrape %d/%d' %(count+1,int(options.repeat))
			#~ os.system("rm cache-*")
			
			#~ success = main()
			
			#~ if success: 
				
				#~ #alert and start ipython upon success
				#~ comand = 'gnome-terminal -x bash -c "./odds_crawler.py"'
				#~ os.system(comand)

			#~ mins = 30
			#~ secs = mins*60
			#~ print 'sleeping for %d seconds' % secs
			#~ bar = progressbar.ProgressBar()
			#~ for sec in bar(xrange(secs)):
				#~ time.sleep(1)
			#~ count+=1
		

