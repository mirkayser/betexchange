#! /usr/bin/env python

from IPython import embed
#embed() # this call anywhere in your program will start IPython

import sys, os, time,re, progressbar
import datetime
import pickle
import numpy as np
from optparse import OptionParser
from operator import itemgetter
from my.spider import Spider
from my.tools import *
from pyik.performance import cached

from betcalc import Bets

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By		

@cached
def get_data_sportsbooks(urls,exch=None):
	
	#get links
	spider = Spider(gui=0)
	
	names = []
	for item in exch:
		split = item['market-name'].lower().split(" v ")
		names.append(split[0])
		names.append(split[-1])
		
	matchlinks=[]
	print ''
	for i,url in enumerate(urls):
		print 'get links from:  %s' % url
		spider.get_url(url)
		elems = spider.driver.find_elements_by_xpath('//td[@class="betting"]/a')
		for elem in elems:
			if "in-play" in elem.get_attribute("class"): continue
			else:
				link = elem.get_attribute("href")
				for name in names:
					if name.lower() in link:
						matchlinks.append( link )
						break
	
	#get data from oddschecker
	sportsbook = []	
	print 'getting data from sportsbooks: (%d events)' % len(matchlinks)
	bar = progressbar.ProgressBar()
	for link in bar(matchlinks):

		spider.get_url(link)
		market_name = spider.driver.find_element_by_xpath('//div[@class="page-description module"]/header/h1').text.replace(" Winner Betting Odds","")
		
		dic = { 'market-name':market_name }
		
		tmp = {}
		headers=spider.driver.find_elements_by_xpath('//thead/tr[@class="eventTableHeader"]/td')
		options = spider.driver.find_elements_by_xpath('//tbody/tr')		
		for option in options:
			
			elems =  option.find_elements_by_xpath('./td')
			
			sel  = elems[0].text.split("\n")[0]

			rates = {}
			for i in xrange(len(headers)):
				head = headers[i].get_attribute("data-bk")
				if head==None: continue
				else:
					elem = elems[i].get_attribute('data-odig')
					if elem!=None:	elem=float(elem)
					else: elem=0.
					
					rates[head]=elem
			
			tmp[sel] = rates
		
		home,away = dic['market-name'].split(" v ")
		rates = [ tmp[home], tmp['Draw'], tmp[away] ]
		
		dic['rates'] = rates	
		sportsbook.append(dic)
		
	spider.close()
	
	return sportsbook
	
@cached	
def get_data_exchange():
	
	start='unknown'
	spider = Spider(gui=0)	
	
	#get urls
	competitions=[]
	spider.get_url('https://www.betfair.com/exchange/football')
	elems = spider.driver.find_elements_by_xpath('//ul/li/a[@data-section-title="Top Competitions"]')
	for elem in elems:
		dic = { 'name':elem.get_attribute("data-ga-title"), 'url':elem.get_attribute("href") }
		
		if 'Rio' in dic['name']: continue
		if 'UEFA' in dic['name']: continue
		competitions.append(dic)	
	
	print 'get data from betfair exchange: (%d urls)' % len(competitions)

	exchange = []
	for j,comp in enumerate(competitions):
		
		print 'get data from market %d/%d: (%s)' % (j+1,len(competitions),comp['name'])	
			
		spider.get_url(comp['url'])
		
		#~ markets = spider.driver.find_elements_by_xpath('//tbody[@data-sportid="1"]')
		markets = spider.driver.find_elements_by_xpath('//div[@class="container-market"]')
		
		#skip empty markets
		if len(markets)==0:
			print '--WARNING: market empty'
			continue
	
		bar = progressbar.ProgressBar()
		for market in bar(markets):

			textlist = market.text.split('\n')
			
			dic = {'competition':comp['name'],'market-name':textlist[0],'start':textlist[1]}
			
			selections = dic['market-name'].split(" v ")
			if len(selections)!=2: continue
			
			else:
				
				prices=[]
				for i in xrange(3):
					
					if i==0: j=0
					if i==1: j=2
					if i==2: j=1
					
					xpath = './div/ul/li/ul/li[contains(@class,"lay selection-%d")]' % j	
					price = market.find_element_by_xpath(xpath).text
					
					if price!=' ':	price = float(price)
					else: 					price = None
					
					prices.append(price)
				
				dic['rates'] = prices	
				exchange.append(dic)
				
	spider.close()
	
	return exchange

def compare(data,limit=0.1):
	
	success=False
			
	b = Bets()		
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
	uk = [	'http://www.oddschecker.com/football/english/premier-league',
					'http://www.oddschecker.com/football/english/championship',
					'http://www.oddschecker.com/football/english/league-1',
					'http://www.oddschecker.com/football/english/league-2',
					'http://www.oddschecker.com/football/scottish/premiership']	
	urls+=uk 

exch = get_data_exchange()
book = get_data_sportsbooks(urls,exch)

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

b = Bets()
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
		

