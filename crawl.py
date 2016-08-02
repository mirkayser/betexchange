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

def get_events(timespan=(90,150),countries=None):
	
	import progressbar
	from selenium.webdriver.support import expected_conditions as EC
	from selenium.webdriver.common.by import By
	
	events = []
	
	print 'searching for events on betfair.com'
	spider = Spider(gui=0)
	spider.get_url('https://www.betfair.com/exchange/horse-racing')
	spider.wait.until(EC.presence_of_element_located((By.XPATH,'//div[@class="single-race"]/span/a')))
	
	#select all available races
	if countries==None:
		races = spider.driver.find_elements_by_xpath('//div[@class="single-race"]/span/a')
	
	#select races from specified countries
	else:
		
		cs = spider.driver.find_elements_by_xpath('//span[@class="country-code"]')
		
		races = []
		for cou in countries:
			for c in cs:
				
				if c.get_attribute("rel")==cou:
					
					mod = c.find_element_by_xpath('./../../../..')
					tags = mod.find_elements_by_xpath("./div/div/div/div/div/div/span/a")
					
					for tag in tags:
						races.append( (cou,tag) )
	
	if len(races)>0:
		bar = progressbar.ProgressBar()	
		for item in bar(races):
			
			r = item[1] 
			
			dic={ 'country':item[0] }
			dic['link']=r.get_attribute('href')
			if dic['link'][-1]!='#':
				
				#set date	
				if 'today' in r.get_attribute('class'):				date = datetime.date.today()
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
				
				#select events with timespan time diff to start
				if datetime.timedelta(minutes=timespan[1]) > (time_e - datetime.datetime.now()) > datetime.timedelta(minutes=timespan[0]):
				
					dic['time_e'] = time_e
					events.append(dic)	
					
		print 'available: %d events' % len(events)	
		spider.driver.close()
		
	else:
		spider.driver.close()
		raise ValueError('no events available in timespan')				
				
	return events
	
				
class ScrapeEvent():
	
	def __init__(self,event):
		
		self.data = event
		self.spider = Spider(gui=0)
		self.driver = self.spider.driver
		self.spider.get_url(self.data['link'])

		self.fname = 'data_'+str(self.data['time_e']).replace(" ","_")+'_'+self.data['link'].split("/")[-1]+'.pkl'
		
		self.data['last_get'] = datetime.datetime(1999,1,1)
		
	def get_status(self):
		
		if not self.data.has_key('status'):	self.data['status'] = 'before'
		
		if self.data['status']!='finished':
				 
			try:	  suspended = self.driver.find_element_by_xpath('//span[contains(@class,"suspended-label")]').is_displayed()
			except: suspended=False
			
			finished = False
			wrapper = self.driver.find_element_by_xpath('//div[contains(@id,"main-wrapper")]').get_attribute('textContent')
			if 'Winner' in wrapper: 
				finished = True
				
				#add winner
				if self.data.has_key('data'):
					winners=[]
					winner = wrapper.split("Winner")[1][:30]
					for key in self.data['data'].keys():
						if key in winner:
							winners.append(key)
					if len(winners)!=1:
						self.data['winner']='nan'
					else: 
						self.data['winner']=winners[0]
			
			else:
				try:		
					finished = self.driver.find_element_by_xpath('//div[contains(@class,"runner-winner-label")]').is_displayed()
				except:	pass
					
			if suspended:
				if self.data['status']!='suspended':	
					self.data['time_s'] = datetime.datetime.now()
					self.data['status'] = 'suspended'
			elif finished:	
				self.data['time_f'] = datetime.datetime.now()			
				self.data['status'] = 'finished'
			else:
				self.data['status'] = 'before'
	
	def get_runner_names(self):
		
		#~ xpaths = ['//h3[@class="runner-name ng-binding ng-scope ng-isolate-scope runner-name-with-jockey"]'
							#~ '//h3[@class="ng-binding ng-isolate-scope runner-name runner-name-with-jockey"]',
							#~ '//h3[@class="ng-binding ng-isolate-scope runner-name"]',
							#~ '//span[@class="runner-name ng-binding ng-isolate-scope"]']
		xpaths = ['//h3[contains(@class,"runner-name")]',
							'//span[contains(@class,"runner-name")]']
		for xpath in xpaths:					
			rnames = self.driver.find_elements_by_xpath(xpath)
			if len(rnames)!=0:
				break
		if len(rnames)==0: 
			raise ValueError("unable to get runner names")
		return rnames
		
	def add_data(self):

		from selenium.webdriver.support import expected_conditions as EC
		from selenium.webdriver.common.by import By		
		
		self.spider.get_url(self.data['link'])
		self.spider.wait.until(EC.presence_of_element_located((By.XPATH,'//span[@class="venue-name ng-binding"]')))
		
		rnames = self.get_runner_names()
		rprices= self.driver.find_elements_by_xpath('//button[contains(@class,"selection-button") and contains(@class,"back")]')
		if len(rprices)==0: raise ValueError('no prices found')
		
		for i in xrange(len(rprices)):
			
			name = rnames[i].text
			price = rprices[i].get_attribute('textContent')
			if price=='':
				print '   WARNING: no price available (%s)' % name
				continue
			price = float(price.split(" ")[0])
			time  = datetime.datetime.now()
			
			self.data['data'][name].append( (time,price) )
			
		self.data['last_get'] = datetime.datetime.now()

	def load_data(self,dirnm):
		
		import pickle
		
		fname = dirnm + self.fname
		
		#create datafile
		if not os.path.isfile(fname):	

			#check status
			self.get_status()
			
			if self.data['status']=='before':
			
				#runner names
				self.data['data'] = {}
				self.spider.wait.until(EC.presence_of_element_located((By.XPATH,'//span[@class="venue-name ng-binding"]')))
				
				rnames = self.get_runner_names()
				for rname in rnames:
					#~ name = rname.get_attribute('textContent')
					name = rname.text
					self.data['data'][name]=[]		
				
				#event name
				xpath_name = '//span[contains(@class,"-name ng-binding") and (contains(@class,"venue") or contains(@class,"event"))]'
				self.spider.wait.until(EC.presence_of_element_located((By.XPATH,xpath_name)))
				self.data['name'] = self.driver.find_element_by_xpath(xpath_name).get_attribute('textContent')			
		
		#load datafile	
		else:
			with open(fname,'rb')as inputfile: 
				self.data = pickle.load(inputfile)
			
	def print_last_set(self):
		
		for item in self.data['data'].items():
			print 'runner: %s,  %s' % (item[0],str(item[1][-1]))

	def save_data(self,dirnm):
		
		import pickle
		
		fname = dirnm + self.fname
		
		with open(fname,'wb') as outputfile: pickle.dump(self.data,outputfile,pickle.HIGHEST_PROTOCOL)
				
	def close(self):
		
		self.driver.close()
		self.driver.quit()

def get_event_schedule(events):
	
	now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
	fname = 'Data/schedules/schedule_'+now+'.txt'
	
	names,e_times,a_times = [],[],[]
	for e in events:
		names.append(e['link'])
		e_times.append(e['time_e'])
		a_times.append( e['time_e'] - datetime.timedelta(minutes=25) )
	
	a = np.array(zip(names,a_times,e_times),dtype=[('name','S100'),('a_time',object),('e_time',object)])
	a.sort(order=['e_time'])	
		
	output = '\nSchedule Races:\n'
	for e in a:
		
		a_time = e['a_time'].strftime("%m-%d %H:%M")	
		e_time = e['e_time'].strftime("%m-%d %H:%M")
				
		output += '%s: %s -> %s\n' % (e['name'], a_time, e_time)
	
	with open(fname,"wb") as textfile:
		textfile.write(output)
	print output	
	
	return np.array(e_times)
	
def scrape_events(events):
	
	if len(events)>15: events = events[:15]
	
	dirnm="Data/new/"
	
	#schedule events, start analysis/event
	e_times = get_event_schedule(events)
	
	run=1	
	finished = np.zeros_like(events)
	while len(finished[finished==0])>0:
		
		print '\nStart Run %d: (%d / %d)  finished: %s' % (run,len(finished[finished==0]),len(events),str(finished))
		
		for i in xrange(len(events)):
			
			#skip finished
			if finished[i]==1: continue		
			
			output=''

			try:
				#init event
				event = ScrapeEvent(events[i])				
				
				#load runner nammes or existing data
				event.load_data(dirnm=dirnm)
				
				#check if event has finished
				event.get_status()

				#artificial delay if datataking too fast
				#if event does NOT terminate within 30 minutes
				if ( event.data['time_e'] - datetime.datetime.now() ) > datetime.timedelta(minutes=30):
				
					#check if data has been taken within the last minutes
					diff = np.abs( (event.data['last_get'] - datetime.datetime.now()).total_seconds() )
					if diff < datetime.timedelta(minutes=5).total_seconds(): 
						
						#if no event within 30 minutes of start -> go to sleep
						if np.all( e_times[finished==0] - datetime.datetime.now() ) > datetime.timedelta(minutes=30):
							sleep = int(datetime.timedelta(minutes=5).total_seconds() - diff)
							print '\nsleeping %d seconds:' % sleep
							bar = progressbar.ProgressBar()
							for sec in bar(xrange(sleep)):
								time.sleep(1)										
						#else only skip this event
						else: 
							print '\nskipping event (last_get=%.1f)' % (diff/60.)
							
							#close event
							event.close()
							continue
												
				#if event has finished, take it out of loop, else add datapoint for ongoing event
				if event.data['status']=='finished':
					output+='\n  --race finished'
					finished[i] = 1
				elif event.data['status']=='suspended':
					output+='\n  --suspended'
				else:	
					event.add_data()
				
				diff = (event.data['time_e'] - datetime.datetime.now())
				num_runners = len(event.data['data'].keys())
				num_datapoints = len(event.data['data'][event.data['data'].keys()[0]])
				output+= '\n  Run %i, Scrape %i:  %s  (%s)' % (run,i+1,event.data['name'],event.data['link'])
				output+= '\n  start in %s  (%d datapoints, %d runners)' % (str(diff),num_datapoints,num_runners)
				
				#save copy for analysis
				if datetime.timedelta(minutes=35) > diff:
					event.save_data(dirnm='Data/prediction/')
				
				#save data
				event.save_data(dirnm=dirnm)				
				
				#close event
				event.close()
			
			except:
				output+= '\n  --WARNING: scrape event failed (%s)\n    %s' % (events[i]['link'],sys.exc_info()[:2])
				finished[i] = 1
				
				#try closing event
				try:		event.close()
				except: pass
			
			output+='\n  --%s' % finished
			print output
			
		run+=1
		
def main():
	print 'here starts main program'
	
parser = OptionParser()
parser.add_option("-l", "--load-events", dest="load_events", action="store_true", default=False,
                  help="load event list from file (cache-events.pkl)")
parser.add_option("--cachenum", dest="cachenum", default='0',
                  help="load event list from file (events.pkl)")
parser.add_option("-t", "--timespan", dest="timespan", default='60,90',
                  help="specifies range in time from where to select events")

(options, args) = parser.parse_args()
timespan = ( int(options.timespan.split(",")[0]), int(options.timespan.split(",")[1]) )

#get countries
if len(args)<1:	countries = None
else: 					countries = args

#~ countries = ['US','CL']

#get event urls
cachenm='cache-events_%s.pkl' % options.cachenum
if options.load_events:
	with open(cachenm,'rb')as inputfile: events = pickle.load(inputfile)	
else:
	events = sorted(get_events(timespan=timespan,countries=countries), key=itemgetter('time_e'))
	with open(cachenm,'wb') as outputfile: pickle.dump(events,outputfile,pickle.HIGHEST_PROTOCOL)
	

events = np.array(events)
np.random.shuffle(events)

scrape_events(events)

#~ #purge phantomjs from system
#~ os.system('pgrep phantomjs | xargs kill')
