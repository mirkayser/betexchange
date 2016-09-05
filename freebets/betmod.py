#! /usr/bin/env python

from IPython import embed
#embed() # this call anywhere in your program will start IPython

import sys, os, time,re, progressbar
#~ from operator import itemgetter
from my.spider import Spider
from my.tools import *
from pyik.performance import cached,pmap

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By		

@cached
def get_data_sportsbooks(link):
	
	#~ print 'get data %s' % link
	
	spider = Spider(gui=0)
	spider.get_url(link)
	market_name = spider.driver.find_element_by_xpath('//div[@class="page-description module"]/header/h1').text.replace(" Winner Betting Odds","")
	
	dic = { 'market-name':market_name }
	
	rates=[]
	#~ headers=spider.driver.find_elements_by_xpath('//thead/tr[@class="eventTableHeader"]/td')
	headers=spider.driver.find_elements_by_xpath('//thead/tr[@class="eventTableHeader"]/td/aside/a')
	options = spider.driver.find_elements_by_xpath('//tbody/tr')		
	for option in options:
		
		elems =  option.find_elements_by_xpath('./td')
		
		sel  = elems[0].text.split("\n")[0]

		books = {}
		for i in xrange(len(headers)):
			#~ head = headers[i].get_attribute("data-bk")
			head = headers[i].get_attribute("title")
			if head==None: continue
			else:
				elem = elems[i].get_attribute('data-odig')
				if elem!=None:	elem=float(elem)
				else: elem=0.
				
				books[head]=elem
		
		rates.append(books)

	dic['rates'] = rates	
	spider.close()
	
	return dic

@cached
def get_links_sportsbooks(args):
	
	url = args[0]
	names = args[1]	
	
	spider = Spider(gui=0)
		
	print 'get links from:  %s' % url
	matchlinks=[]
	spider.get_url(url)
	elems = spider.driver.find_elements_by_xpath('//td[@class="betting"]/a')
	for elem in elems:
		if "in-play" in elem.get_attribute("class"): continue
		else:
			link = elem.get_attribute("href")
			if names!=None:
				for name in names:
					if name.lower() in link:
						matchlinks.append(link)
						break
			else: matchlinks.append(link)
	spider.close()
	return matchlinks

#~ @cached
def sportsbooks(urls,pool=False,exch=None):
	
	if exch!=None:
		names = []
		for item in exch:
			split = item['market-name'].lower().split(" ")
			names.append(split[0])
			names.append(split[-1])
	else: names=None
	
	args = []
	for url in urls:
		args.append( (url,names) )
	
	if pool:		
		linklists = pmap(get_links_sportsbooks, args, numProcesses=2,displayProgress = True)
	else:
		linklists=[]
		for arg in args:
			linklists.append( get_links_sportsbooks(arg) )

	matchlinks = []
	for item in linklists:
		for entry in item:
			matchlinks.append(entry)
	
	#~ matchlinks=matchlinks[:5]
	
	#get data from oddschecker	
	print 'getting data from sportsbooks: (%d events)' % len(matchlinks)
	
	if pool:
		sportsbooks = pmap(get_data_sportsbooks, matchlinks, numProcesses=2,displayProgress = True)
	else:
		bar=progressbar.ProgressBar()
		sportsbooks = []
		for link in bar(matchlinks):
			sportsbooks.append( get_data_sportsbooks(link) )
	
	return sportsbooks
	
	
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
