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

from betcalc import Lay_Bets

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By		

@cached
def get_data_sportsbooks(names=None):
	
	urls = [	'http://www.oddschecker.com/tennis/atp-winston-salem',
						'http://www.oddschecker.com/tennis/challenger-tour',
						'http://www.oddschecker.com/tennis/us-open/mens',
						'http://www.oddschecker.com/tennis/us-open/womens'
						]
	market_names = [ item.split("tennis/")[-1] for item in urls ]					
	
	
	spider = Spider(gui=0)
	
	#get links
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
						matchlinks.append( (link,market_names[i]) )
						break
						
	if len(matchlinks)==0: raise ValueError("no events found in specified markets")
	
	#get data from oddschecker
	sportsbook = []	
	print 'getting data from sportsbooks: (%d events)' % len(matchlinks)
	bar = progressbar.ProgressBar()
	for item in bar(matchlinks):
		
		link = item[0]
		market_name=item[1]
		
		#skip handicaps
		if "handicap" in link: continue
		
		spider.get_url(link)
		players = spider.driver.find_elements_by_xpath('//tbody/tr')
		
		for player in players:
			dic = { 'market-name':market_name }
			elems =  player.find_elements_by_xpath('./td')
			dic['name'] = elems[0].get_attribute('textContent')
			
			split = dic['name'].split("/")
			if len( split )>1:
				dic['name'] = split[0].split(" ")[-1]+'/'+split[1].split(" ")[-1]
			else:
				dic['name'] = dic['name'].split(" ")[-1]
			
			headers=spider.driver.find_elements_by_xpath('//thead/tr[@class="eventTableHeader"]/td')
			rates = {}
			for i in xrange(len(headers)):
				if headers[i]==None: continue
				else:
					head = headers[i].get_attribute("data-bk")
					elem = elems[i].get_attribute('data-odig')
					if elem!=None:	elem=float(elem)
					else: elem=0.
					
					rates[head]=elem
			dic['rates']=rates
			sportsbook.append(dic)
	
	spider.close()
	
	return sportsbook
	
@cached	
def get_data_exchange():
	
	start='unknown'
	spider = Spider(gui=0)	
	
	#get urls
	urls,market_names=[],[]
	spider.get_url('https://www.betfair.com/exchange/tennis')
	elems = spider.driver.find_elements_by_xpath('//ul[@class="children"]/li/a')
	for elem in elems:
		url = elem.get_attribute("href")
		market_name = elem.get_attribute("market-name")
		
		if 'Challenger' in market_name: pass
		elif 'Winston' in market_name: pass
		elif 'US Open' in market_name: pass
		else: continue
		
		urls.append(url)
		market_names.append(market_name)	
	
	print 'get data from betfair exchange: (%d urls)' % len(urls)
	
	names,prices,starts,mnames = [],[],[],[]
	for j,url in enumerate(urls):
		
		print 'get data from market %d/%d: (%s)' % (j,len(urls),market_names[j])
			
		spider.get_url(url)
		
		markets = spider.driver.find_elements_by_xpath('//div[@class="container-market"]')
	
		#skip empty markets
		if len(markets)==0:
			print '--WARNING: market empty (%s)' % market_names[j]
			continue
	
		bar = progressbar.ProgressBar()
		for market in bar(markets):
			
			#~ market = markets[5]
			text = market.find_element_by_xpath('./a/div').text
			
			if len(text.split('\n'))>1:
				text,start = text.split('\n')
	
			players = text.split(" v ")
			if len(players)!=2: continue
			else:
				
				for i in xrange(len(players)):
					split = players[i].split("/")
					if len(split)==2:
						players[i] = split[0].rstrip().split(" ")[-1]+'/'+split[1].rstrip().split(" ")[-1]
					else:
						players[i] = players[i].split(" ")[-1]
						
				price1 = market.find_element_by_xpath('./div/ul/li/ul/li[contains(@class,"lay selection-0")]/button').text
				price2 = market.find_element_by_xpath('./div/ul/li/ul/li[contains(@class,"lay selection-1")]/button').text
				
				if price1!=' ':
					price1 = float(price1)
					names.append(players[0])
					prices.append(price1)
					starts.append(start)
					mnames.append(market_names[j])
				if price2!=' ':
					price2 = float(price2)
					names.append(players[1])
					prices.append(price2)
					starts.append(start)
					mnames.append(market_names[j])
	
	spider.close()
	
	return names,prices,starts,mnames

def compare(data,limit=0.5):
	
	success=False
	
	b = Lay_Bets()
	out='\nResult:\n'		
	for item in data:
		 
		for k in item['rates'].keys():
			
			if k=='lay': continue
			
			diff = item['rates']['lay'] - item['rates'][k]
			
			if item['rates'][k]<1.5 and diff>0: continue
			if diff > limit: continue
			
			b.set_rates(item['rates'][k],item['rates']['lay'])
			b.get_stake(50,verbose=False)
			profit = b.get_profit_laywin()
			
			out += '%5.2f (%5.2f)  %s (%s)  back=%5.2f  lay=%5.2f  -> %s  (%s)\n' % (diff,profit,item['name'].rjust(15," "),k,item['rates'][k],item['rates']['lay'],item['start'],item['market-name'])
			
			if diff<0:
				success=True
		
	if out=='': out = 'WARNING: no item fits specifications'
	
	print out
	
	return success
		
def main():
	print ''
	
	names,prices,starts,mnames = get_data_exchange()
	sportsbook = get_data_sportsbooks(names)
	
	#join datasets
	print '\njoin datasets'
	data = []
	for dic in sportsbook:
		found=False
		for i in xrange(len(names)):
			keyword = dic['name']
			if re.search(keyword,names[i],re.IGNORECASE):
				
				dic['rates']['lay'] = prices[i] 
				dic['start'] = starts[i]
				dic['market-name'] = mnames[i]
				data.append(dic)
				found=True
				break
		#~ if not found:
			#~ print '--WARNING: not found %s (%s)' % (dic['name'],dic['market-name'])
	print '%d/%d matched' % (len(data),len(sportsbook))
					
	success = compare(data,limit=0.)
	
	embed()
	
	return success


if __name__ == "__main__":

	#parse options
	parser = OptionParser()
	parser.add_option("-r","--repeat", dest="repeat", default=False,
	                  help="repeat x times")
	(options, args) = parser.parse_args()

	if not options.repeat:
		success = main()	
		b = Lay_Bets()
		#~ embed()
		
	else:
		count=0
		while count<int(options.repeat):
			
			print 'scrape %d/%d' %(count+1,int(options.repeat))
			os.system("rm cache-*")
			
			success = main()
			
			if success: 
				
				#alert and start ipython upon success
				comand = 'gnome-terminal -x bash -c "./odds_crawler.py"'
				os.system(comand)
				
				#~ break

			mins = 30
			secs = mins*60
			print 'sleeping for %d seconds' % secs
			bar = progressbar.ProgressBar()
			for sec in bar(xrange(secs)):
				time.sleep(1)
			count+=1
		

