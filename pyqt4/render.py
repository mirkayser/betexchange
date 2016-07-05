#! /usr/bin/env python

from IPython import embed
#embed() # this call anywhere in your program will start IPython

import sys, os
from optparse import OptionParser
import betmod as mod
from lxml import html
from PyQt4.QtWebKit import QWebView
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QUrl
import threading
import time
from datetime import datetime
from pyik.performance import cached
import pickle

class Render(QWebView):
		
	def __init__(self, url):
		
		def worker():
			output=False
			running=True
			i=0
			if output:	print 'rendering page...'
			while running:
				time.sleep(5) 
				i+=5
				if output:	print "in queue",i,"sec"
				
				self.result = str(self.browser.page().currentFrame().toHtml().toAscii())
				tree = html.fromstring(self.result)	
				content = tree.xpath('//span[@class="venue-name ng-binding"]//text()')
				if len(content)>0:
					if output:	print "waiting..."
					time.sleep(5)
					self.result = str(self.browser.page().currentFrame().toHtml().toAscii())
					self.app.quit()
					running=False
					if output:	print "rendering finished\n"
				if i>=120:
					self.result = ""
					self.app.quit()
					running=False
					if output:	print "rendering failed..."
					
		self.app = QApplication(sys.argv)
		self.browser = QWebView()
		self.browser.load(QUrl(url))
		#~ self.browser.show()
		
		thread = threading.Thread(target=worker)
		thread.setDaemon(True)
		thread.start()
		
		self.app.exec_()
		#~ self.browser.close()
		self.date = datetime.now()		
		
def createDateObject(ename,edate):
	day,month=str(edate[-7:-5]),str(edate[-4:-1])
	months=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
	i=1
	for m in months:
		if m==month: 
			month = '%d' %i
			if len(month)<2: month = '0'+month
			break
		i+=1
	year = str(datetime.now().year)
	h,min,s = str(ename[:2]),str(ename[3:5]),'00'
	edate = datetime.strptime(year+month+day+h+min+s,"%Y%m%d%H%M%S")
	return edate		

def render(url):
	output=True
	r = Render(url)
	if r.result=="": 
		ename,edate,date,names,prices="","","","",""
		return ename,edate,date,names,prices
	else:
		date=r.date
		tree = html.fromstring(r.result)
		ename = tree.xpath('//span[@class="venue-name ng-binding"]/@ng-bind-template')
		edate = tree.xpath('//span[@class="event-date ng-binding"]/@ng-bind-template')
		#~ edate = createDateObject(ename,edate)
		#~ ename = ename[6:-1]
		
		names = tree.xpath('//span[@class="runner-name ng-binding ng-isolate-scope"]//text()')
		prices = tree.xpath('//button[@class="bf-col-3-24 btn back depth-back-2 back-selection-button"]/span[@class="price ng-binding"]//text()')
		if len(prices)==0:	raise ValueError('event suspended!!!')
		else:
			if output:
				print ename, edate
				print len(names), len(prices)
				for i in xrange(len(prices)):
					print names[i],prices[i]
				try:
					ename,edate=ename[0],edate[0]
					eh,emin=str(ename[:2]),str(ename[3:5])
					h,min=str(date)[11:13],str(date)[14:16]
					estamp=int(eh)*60+int(emin)
					stamp=int(h)*60+int(min)
					diff=estamp-stamp
					print diff,'\n'
				except: pass
			return ename,edate,date,names,prices

def main():
	print 'here starts main program'

parser = OptionParser()
(options, args) = parser.parse_args()

if len(args)!=1:
	raise NameError("Usage: %s some_url")
else: url=args[0]

ename,edate,date,names,prices  = render(url)



if ename!="":
	filename = url[-9:]+'.pkl'
	filename = filename.replace(' ','')

	if os.path.isfile(filename):	
		with open(filename, 'rb') as input:
			event = pickle.load(input)
			os.remove(filename)	
	else:	event = mod.Event(url,ename,edate)
	
	event.addDatapoint(date,names,prices)
	

	with open(filename,'wb') as output:
		pickle.dump(event,output,pickle.HIGHEST_PROTOCOL)







#~ i=1
#~ while i<5:
	#~ print "\nnext run in 30 sec"
	#~ time.sleep(30)
	#~ ename,edate,date,names,prices  = render(url)
	#~ event.addDatapoint(date,names,prices)
	
