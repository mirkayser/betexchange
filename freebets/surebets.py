#! /usr/bin/env python

from IPython import embed
#embed() # this call anywhere in your program will start IPython

import sys,os,time,re,datetime,progressbar
import numpy as np
from optparse import OptionParser

from betmod import *

def get_best_prices(events):

	new_list=[]
	for event in events:
	
		new_event={}
		new_event['market-name']=event['market-name']
		new_event['cup-name']=event['cup-name']
		new_event['rates']=[]
		new_event['bookies']=[]
		
		for item in event['rates']:
			
			if item=={}: continue
			best=max(item.values())
			bookies= [ k for k in item.keys() if item[k]==best ]
			
			new_event['rates'].append(best)
			new_event['bookies'].append(bookies)
		
		if len(new_event['rates'])>0:
			new_list.append(new_event)
	
	return new_list

class Sure_Bets(object):
	
	def __init__(self,event,stake_max=10):
		
		self.event=event	
		self.stake_max=stake_max
		
	def get_profit(self):
		
		rates = self.event['rates']
		
		rate_min = min(rates)
		win = np.round( self.stake_max*rate_min, 2)
		
		stakes=[]
		for r in rates:
			stake = np.round(win/r, 2)
			stakes.append(stake)
		
		total_stake=sum(stakes)
				
		self.rates=rates
		self.stakes=stakes
		self.total_stake=total_stake
		self.profit= win-total_stake
		self.percentage=np.round(100*(self.profit/self.total_stake), 2)
		
		return self.profit

	def get_bookies(self):
		
		bookies = self.event['bookies']
		total_bookies = self.get_total_bookies()
		
		new=[]
		for sel in bookies:
			
			found=False
			for item in sel:
				
				if item in total_bookies:
					total_bookies.remove(item)
					new.append(item)
					found=True
					break
			
			if not found:
				new.append('')

		self.bookies = np.array(new)
		
		return self.bookies
		
	def get_total_bookies(self):
		
		bookies = self.event['bookies']
		
		total_bookies=[]
		for item in bookies:
			for entry in item:
				total_bookies.append(entry)
		total_bookies = list(set(total_bookies))
		return total_bookies
		
def main():
	print ''

#parse options
parser = OptionParser()
parser.add_option("-p","--pool", dest="pool", action="store_true", default=False,
                  help="use pmap to to parallelize jobs")
parser.add_option("-a","--all", dest="all", action="store_true", default=False,
                  help="use all available urls")
(options, args) = parser.parse_args()

urls = []

if 'uk' in args or options.all:
	urls+= ['http://www.oddschecker.com/football/english/premier-league',
					'http://www.oddschecker.com/football/english/championship',
					'http://www.oddschecker.com/football/english/league-1',
					'http://www.oddschecker.com/football/english/league-2',
					'http://www.oddschecker.com/football/scottish/premiership',
					]	
if 'de' in args or options.all:	
	urls+= ['http://www.oddschecker.com/football/germany/bundesliga',
					'http://www.oddschecker.com/football/germany/bundesliga-2',
					'http://www.oddschecker.com/football/germany/3rd-liga',
					'http://www.oddschecker.com/football/germany/dfb-pokal',
					]
if 'it' in args or options.all:	
	urls+= ['http://www.oddschecker.com/football/italy/serie-a',
					'http://www.oddschecker.com/football/italy/serie-b',
					'http://www.oddschecker.com/football/italy/coppa-italia',
					]
if 'sp' in args or options.all:					
	urls+= ['http://www.oddschecker.com/football/spain/la-liga-primera',
					'http://www.oddschecker.com/football/spain/la-liga-segunda',
					'http://www.oddschecker.com/football/spain/copa-del-rey',
					'http://www.oddschecker.com/football/spain/la-liga-segunda-b',
					]
if 'fr' in args or options.all:
	urls+= ['http://www.oddschecker.com/football/france/ligue-1',
					'http://www.oddschecker.com/football/france/ligue-2',
					'http://www.oddschecker.com/football/france/national',
					'http://www.oddschecker.com/football/france/cfa',
					]
if 'uefa' in args or options.all:
	urls+= [	'http://www.oddschecker.com/football/champions-league',
						'http://www.oddschecker.com/football/europa-league',
						]
if 'tennis' in args or options.all:	
	urls+= [	'http://www.oddschecker.com/tennis/atp-winston-salem',
						'http://www.oddschecker.com/tennis/challenger-tour',
						'http://www.oddschecker.com/tennis/us-open/mens',
						'http://www.oddschecker.com/tennis/us-open/womens'
						]
	
events = sportsbooks(urls,pool=options.pool,exch=None)
events = get_best_prices(events)

booky_list=[]
for event in events:
	
	sure=Sure_Bets(event)
	profit = sure.get_profit()
	bookies = sure.get_bookies()
	total_bookies = sure.get_total_bookies()
	if sure.percentage>1 and np.all(bookies!=''):
		print profit,sure.percentage,bookies,event['market-name'],event['cup-name']
		booky_list += total_bookies
		
from collections import Counter

most_common = Counter(booky_list).most_common(5)#[0][0]
print most_common



