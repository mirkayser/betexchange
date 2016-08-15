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
def get_data_sportsbooks():
	
	urls = [	'http://www.oddschecker.com/olympics/tennis/olympic-mens',
						'http://www.oddschecker.com/olympics/tennis/olympic-womens',
						'http://www.oddschecker.com/olympics/tennis/olympic-specials',
						'http://www.oddschecker.com/olympics/tennis/olympic-womens-doubles',
						'http://www.oddschecker.com/tennis/atp-los-cabos',
						'http://www.oddschecker.com/tennis/itf-futures',
						'http://www.oddschecker.com/tennis/challenger-tour'
						]
	market_names = [ 'rio men','rio women','rio men double','rio women double','atp cabo','itf futures','challenger' ]
	
	spider = Spider(gui=0)
	
	#get links
	matchlinks=[]
	for i,url in enumerate(urls):
		print 'get links from:  %s' % url
		spider.get_url(url)
		elems = spider.driver.find_elements_by_xpath('//td[@class="betting"]/a')
		for elem in elems:
			if "in-play" in elem.get_attribute("class"): continue
			else:
				matchlinks.append( (elem.get_attribute("href"),market_names[i]) )
	
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
					
			bet365 = elems[1].get_attribute('data-odig')
			if bet365!=None: 
				dic['bet365']  = float(bet365)
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

def compare(data,book='bet365',limit=0.5):
	
	success=False
			
	out='\nResult:\n'
				
	for item in data:
		
		diff = item['lay'] - item[book]
		
		if item[book]<1.5 and diff>0: continue
		if diff > limit: continue
		
		out += '%5.2f  %s  back=%5.2f  lay=%5.2f  -> %s  (%s)\n' % (diff,item['name'].ljust(20," "),item[book],item['lay'],item['start'],item['market-name'])
		
		if diff<0:
			success=True
		
	if out=='': out = 'WARNING: no item fits specifications'
	
	print out
	
	return success
		
def main():
	print ''
	
	sportsbook = get_data_sportsbooks()
	names,prices,starts,mnames = get_data_exchange()
	
	#join datasets
	print '\njoin datasets'
	data = []
	for dic in sportsbook:
		found=False
		for i in xrange(len(names)):
			keyword = dic['name']
			if re.search(keyword,names[i],re.IGNORECASE):
			#~ if dic['name'] in names[i]:
			#~ if names[i] in dic['name']:
			
				dic['lay'] = prices[i] 
				dic['start'] = starts[i]
				dic['market-name'] = mnames[i]
				data.append(dic)
				found=True
				break
		#~ if not found:
			#~ print '--WARNING: not found %s (%s)' % (dic['name'],dic['market-name'])
	print '%d/%d matched' % (len(data),len(sportsbook))
					
	success = compare(data,limit=0.1)
	
	return success


if __name__ == "__main__":

	#parse options
	parser = OptionParser()
	parser.add_option("-r","--repeat", dest="repeat", default=False,
	                  help="repeat x times")
	(options, args) = parser.parse_args()

	if not options.repeat:
		success = main()	
		b = Bets()
		embed()
		
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
		

