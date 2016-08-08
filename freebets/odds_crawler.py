#! /usr/bin/env python

from IPython import embed
#embed() # this call anywhere in your program will start IPython

import sys, os, time, progressbar
import datetime
import pickle
import numpy as np
from optparse import OptionParser
from operator import itemgetter
from my.spider import Spider
from my.tools import *

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By		

def get_data_sportsbooks(spider):
	
	urls = [	'http://www.oddschecker.com/olympics/tennis/olympic-mens',
						'http://www.oddschecker.com/olympics/tennis/olympic-womens',
						'http://www.oddschecker.com/olympics/tennis/olympic-specials',
						'http://www.oddschecker.com/olympics/tennis/olympic-womens-doubles'
						]
	
	#get links
	matchlinks=[]
	for url in urls:
		print 'get links from:  %s' % url
		spider.get_url(url)
		elems = spider.driver.find_elements_by_xpath('//td[@class="betting"]/a')
		for elem in elems:
			matchlinks.append(elem.get_attribute("href"))
	
	#get data from oddschecker
	sportsbook = []	
	print 'getting data from sportsbooks: (%d events)' % len(matchlinks)
	bar = progressbar.ProgressBar()
	for link in bar(matchlinks):
		
		spider.get_url(link)
		players = spider.driver.find_elements_by_xpath('//tbody/tr')
		
		for player in players:
			dic = {}
			elems =  player.find_elements_by_xpath('./td')
			dic['name'] = elems[0].get_attribute('textContent')
			
			bet365 = elems[1].get_attribute('data-odig')
			if bet365!=None: 
				dic['bet365']  = float(bet365)
				sportsbook.append(dic)
	
	return sportsbook
	
def get_data_exchange(spider):

	#get data from betfair exchange
	print 'get data from betfair exchange:'
	spider.get_url('https://www.betfair.com/exchange/tennis/competition?id=9574834')
	
	markets = spider.driver.find_elements_by_xpath('//div[@class="container-market"]')
	
	names,prices = [],[]
	bar = progressbar.ProgressBar()
	for market in bar(markets):
		
		#~ market = markets[5]
		text = market.find_element_by_xpath('./a/div').text.split(" v ")
		if len(text)!=2: continue
		else:
			
			name1,name2 = text
			price1 = market.find_element_by_xpath('./div/ul/li/ul/li[contains(@class,"lay selection-0")]/button').get_attribute("textContent")
			price2 = market.find_element_by_xpath('./div/ul/li/ul/li[contains(@class,"lay selection-1")]/button').get_attribute("textContent")
		
			price1,price2 = float(price1),float(price2)
		
			names.append(name1)
			names.append(name2)
			prices.append(price1)
			prices.append(price2)
	
	return names,prices

def compare(data,book='bet365',limit=0.5):
			
	out=''
				
	for item in data:
		
		if item[book] < 1.5: continue
		
		diff = np.abs( item[book] - item['lay'] )
		if diff > limit: continue
		
		out += '%.2f  %s  (back=%.2f, lay=%.2f)\n' % (diff,item['name'].ljust(20," "),item[book],item['lay'])

	if out=='': out = 'WARNING: no item fits specifications'
	
	print out
		
def main():
	print 'here starts main program'
	
spider = Spider(gui=0)

sportsbook = get_data_sportsbooks(spider)
names,prices = get_data_exchange(spider)

spider.close()	
	
#join datasets
print 'join datasets'
data = []
for dic in sportsbook:
	for i in xrange(len(names)):
		if dic['name'] in names[i]:
			dic['lay'] = prices[i] 
			data.append(dic)

compare(data,limit=0.5)
	


