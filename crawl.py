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

def get_events(timespan=(4,12),trial=False):
	
	import progressbar
	from selenium.webdriver.support import expected_conditions as EC
	from selenium.webdriver.common.by import By
	
	print 'searching for events on betfair.com'
	spider = Spider(gui=0)
	spider.get_url('https://www.betfair.com/exchange/horse-racing')
	spider.wait.until(EC.presence_of_element_located((By.XPATH,'//div[@class="single-race"]/span/a')))
	
	events = []
	bar = progressbar.ProgressBar()
	races = spider.driver.find_elements_by_xpath('//div[@class="single-race"]/span/a')
	for r in bar(races):
		dic={}
		dic['link']=r.get_attribute('href')
		if dic['link'][-1]!='#':
			
			#set date	
			if 'today' in r.get_attribute('class'):			date = datetime.date.today()
			elif 'tomorrow' in r.get_attribute('class'): 	date = datetime.date.today() + datetime.timedelta(days=1)
			else: continue
			
			#set time
			time = r.get_attribute('textContent')
			time = datetime.time(int(time[:2]),int(time[-2:]))
			
			#combine date and time
			time_e = datetime.datetime.combine(date, time)
			
			#fix date for races in the first hours of the morning
			if (time_e - datetime.datetime.now()) <= datetime.timedelta(days=0): time_e = time_e + datetime.timedelta(days=1)
			
			#fix time difference
			time_e = time_e - datetime.timedelta(hours=5)
			
			if trial:
				if datetime.timedelta(minutes=30) > (time_e - datetime.datetime.now()) > datetime.timedelta(minutes=0):
					
					dic['time_e'] = time_e
					events.append(dic)
			else:	
				#select events with min 4 and max 12 hours time diff to start
				if datetime.timedelta(hours=timespan[1]) > (time_e - datetime.datetime.now()) > datetime.timedelta(hours=timespan[0]):
				
					dic['time_e'] = time_e
					events.append(dic)	
					
	spider.driver.close()			
	print 'available: %d events' % len(events)			

	return events
	
				
class ScrapeEvent():
	
	def __init__(self,event):
		
		self.event = event
		self.spider = Spider(gui=0)
		self.driver = self.spider.driver
		self.spider.get_url(self.event['link'])

		self.fname = 'Data/raw/data_'+str(self.event['time_e']).replace(" ","_")+'_'+self.event['link'].split("/")[-1]+'.pkl'
		self.load_data()

	def get_status(self):
		
		if not self.event.has_key('status'):	self.event['status'] = 'before'
		
		if self.event['status']!='finished':
				 
			try:	  suspended = self.driver.find_element_by_xpath('//span[contains(@class,"suspended-label")]').is_displayed()
			except: suspended=False
			
			finished = False
			wrapper = self.driver.find_element_by_xpath('//div[contains(@id,"main-wrapper")]').get_attribute('textContent')
			if 'Winner' in wrapper: 
				finished = True
				
				#add winner
				if self.event.has_key('data'):
					winners=[]
					winner = wrapper.split("Winner")[1][:30]
					for key in self.event['data'].keys():
						if key in winner:
							winners.append(key)
					if len(winners)!=1:
						self.event['winner']='nan'
					else: 
						self.event['winner']=winners[0]
			
			else:
				try:		
					finished = self.driver.find_element_by_xpath('//div[contains(@class,"runner-winner-label")]').is_displayed()
				except:	pass
					
			if suspended:
				if self.event['status']!='suspended':	
					self.event['time_s'] = datetime.datetime.now()
					self.event['status'] = 'suspended'
			elif finished:	
				self.event['time_f'] = datetime.datetime.now()			
				self.event['status'] = 'finished'
			else:
				self.event['status'] = 'before'
		
	def add_data(self):

		from selenium.webdriver.support import expected_conditions as EC
		from selenium.webdriver.common.by import By		

		self.spider.get_url(self.event['link'])
		self.spider.wait.until(EC.presence_of_element_located((By.XPATH,'//span[@class="venue-name ng-binding"]')))
		
		rnames = self.driver.find_elements_by_xpath('//span[@class="runner-name ng-binding ng-isolate-scope"]')
		rprices= self.driver.find_elements_by_xpath('//button[contains(@class,"selection-button") and contains(@class,"back")]')
		if len(rprices)==0: raise ValueError('no prices found')
		
		for i in xrange(len(rprices)):
			
			name = rnames[i].get_attribute('textContent')
			price = rprices[i].get_attribute('textContent')
			if price=='':
				print '   WARNING: no price available (%s)' % name
				continue
			price = float(price.split(" ")[0])
			time  = datetime.datetime.now()
			
			self.event['data'][name].append( (time,price) )
			
	def print_last_set(self):
		
		for item in self.event['data'].items():
			print 'runner: %s,  %s' % (item[0],str(item[1][-1]))

	def save_data(self):
		
		import pickle
		
		with open(self.fname,'wb') as outputfile: pickle.dump(self.event,outputfile,pickle.HIGHEST_PROTOCOL)
	
	def load_data(self):
		
		import pickle
		
		if not os.path.isfile(self.fname):	

			#check status
			self.get_status()
			
			if self.event['status']=='before':
			
				#runner names
				self.event['data'] = {}
				xpath_rnames = '//span[@class="runner-name ng-binding ng-isolate-scope"]'
				
				self.spider.wait.until(EC.presence_of_element_located((By.XPATH,xpath_rnames)))
				rnames = self.driver.find_elements_by_xpath(xpath_rnames)
				for rname in rnames:
					name = rname.get_attribute('textContent')
					self.event['data'][name]=[]		
				
				#event name
				xpath_name = '//span[contains(@class,"-name ng-binding") and (contains(@class,"venue") or contains(@class,"event"))]'
				self.spider.wait.until(EC.presence_of_element_located((By.XPATH,xpath_name)))
				self.event['name'] = self.driver.find_element_by_xpath(xpath_name).get_attribute('textContent')			
			

		else:
			with open(self.fname,'rb')as inputfile: 
				self.event = pickle.load(inputfile)
				
	def close(self):
		
		self.driver.close()
		self.driver.quit()

def scrape_events(etuple):

	run=etuple[0]
	events=etuple[1]
	
	if len(events)>15: events = events[:15]

	finished = np.zeros_like(events)
	while len(finished[finished==0])>0:
		
		print '\nStart Run %d: (%d / %d)  finished: %s' % (run,len(finished[finished==0]),len(events),str(finished))
		
		for i in xrange(len(events)):
			
			if finished[i]==1: continue
			
			output=''
			try:
				event = ScrapeEvent(events[i])				
				
				#check if event has finished
				event.get_status()
				
				#if event has finished, take it out of loop, else add datapoint for ongoing event
				if event.event['status']=='finished':
					output+='\n  --race finished'
					finished[i] = 1
				elif event.event['status']=='suspended':
					output+='\n  --suspended'
				else:	
					event.add_data()
				
				diff = (event.event['time_e'] - datetime.datetime.now())
				num_runners = len(event.event['data'].keys())
				num_datapoints = len(event.event['data'][event.event['data'].keys()[0]])
				output+= '\n  Run %i, Scrape %i:  %s  (%s)' % (run,i+1,event.event['name'],event.event['link'])
				output+= '\n  start in %s  (%d datapoints, %d runners)' % (str(diff),num_datapoints,num_runners)
				
				#save data and close event
				event.save_data()
				event.close()
				
			except:
				output+= '\n--WARNING: event skipped (%s)' % events[i]['link']
				finished[i] = 1
			
			output+='\n  --%s' % finished
			print output

		
def main():
	print 'here starts main program'
	
parser = OptionParser()
parser.add_option("-l", "--load-events", dest="load_events", action="store_true", default=False,
                  help="load event list from file (events.pkl)")
parser.add_option("-n", "--numProcesses", dest="numProcesses", default='2',
                  help="specifies how many processes scrape simultaneously")
parser.add_option("-t", "--timespan", dest="timespan", default='4,6',
                  help="specifies range in time from where to select events")
parser.add_option("--trial", dest="trial", action="store_true", default=False,
                  help="get events close to finish")

(options, args) = parser.parse_args()
numProcesses = int(options.numProcesses)
timespan = ( int(options.timespan.split(",")[0]), int(options.timespan.split(",")[1]) )

#get event urls
if options.load_events:
	with open('events.pkl','rb')as inputfile: events = pickle.load(inputfile)	
else:
	events = sorted(get_events(timespan=timespan,trial=options.trial), key=itemgetter('time_e'))
	with open('events.pkl','wb') as outputfile: pickle.dump(events,outputfile,pickle.HIGHEST_PROTOCOL)
	

events = np.array(events)
np.random.shuffle(events)
events_list = np.array_split(events,numProcesses)
etuples = [ ( i+1,item ) for i,item in enumerate(events_list) ] 

#test
#~ embed()
#~ event = ScrapeEvent(events[0])


if numProcesses==1: scrape_events(etuples[0])
else:	poolmap(scrape_events,etuples,numProcesses=numProcesses)

#purge phantomjs from system
os.system('pgrep phantomjs | xargs kill')
