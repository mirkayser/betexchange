#! /usr/bin/env python

from IPython import embed
#embed() # this call anywhere in your program will start IPython

import sys, os
from optparse import OptionParser
import modules as mod
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
			running=True
			i=0
			while running:
				time.sleep(5) 
				i+=5
				print "in queue",i,"sec"
								
				self.result = str(self.browser.page().currentFrame().toHtml().toAscii())
				tree = html.fromstring(self.result)	
				content = tree.xpath('//div[@class="single-race"]/span/a/text()')				
				if len(content)>0:
					print "waiting..."
					time.sleep(5)
					self.result = str(self.browser.page().currentFrame().toHtml().toAscii())
					self.app.quit()
					running=False
					print "rendering finished\n"
				elif i>=120:
					self.result = ""
					self.app.quit()
					running=False
					print "rendering failed..."
					
		self.app = QApplication(sys.argv)
		self.browser = QWebView()
		self.browser.load(QUrl(url))
		#self.browser.show()
		
		thread = threading.Thread(target=worker)
		thread.setDaemon(True)
		thread.start()
		
		self.app.exec_()
		#self.browser.close()
		self.date = datetime.now()

def render(url):
	print 'rendering page...'
	r = Render(url)
	result = r.result
	return result
	

def main():
	print 'here starts main program'
	
url = 'https://www.betfair.com/exchange/horse-racing'

result = render(url)
tree = html.fromstring(result)	
dates = tree.xpath('//div[@class="single-race"]/span/a/@class')
times = tree.xpath('//div[@class="single-race"]/span/a/text()')
links = tree.xpath('//div[@class="single-race"]/span/a/@href')

today,tomorrow = [],[]
for i in xrange(len(dates)):
	if links[i]=='#': continue
	else:
		if links[i][0:9]=='/exchange':
			links[i] = '//www.betfair.com'+links[i]
		if dates[i][-5:]=='today':
			today.append((times[i],'https:'+links[i]))
		elif dates[i][-8:]=='tomorrow':
			tomorrow.append((times[i],'https:'+links[i]))
		else: raise NameError('race NOT today or tomorrow!')	

fname = 'urls_today.txt'
with open(fname, 'wb') as output:
	for item in today:
		output.write(item[1]+'\n')
print len(today),"urls written to",fname 

fname = 'urls_tomorrow.txt'
with open(fname, 'wb') as output:
	for item in tomorrow:
		output.write(item[1]+'\n')
print len(tomorrow),"urls written to",fname 

#~ embed()

