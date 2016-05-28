#! /usr/bin/env python

from IPython import embed
#embed() # this call anywhere in your program will start IPython

import sys, os, time, datetime, progressbar
import numpy as np

from selenium import webdriver	
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.proxy import *

class Spider():
	
	def __init__(self,gui=1):
		self.name='spider'
		#use proxy
		#~ if hide:
			#~ proxy = self.generate_proxy()	
			#~ self.driver = webdriver.Firefox(proxy=proxy)
		#select browser
		if gui: #firefox
			self.driver = webdriver.Firefox()
		else: #headless driver
			dcap = dict(DesiredCapabilities.PHANTOMJS)
			dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (X11; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0")
			self.driver = webdriver.PhantomJS(desired_capabilities = dcap)
			self.driver.set_window_size(1920, 1080)
		self.wait = WebDriverWait(self.driver, 60)
	
	def generate_proxy(self):
		#Build the Proxy object using the locally running Privoxy
		port = "8118" #The Privoxy (HTTP) port
		myProxy = "127.0.0.1:"+port
		proxy = Proxy({
		    'proxyType': ProxyType.MANUAL,
		    'httpProxy': myProxy,
		    'ftpProxy': myProxy,
		    'sslProxy': myProxy,
		    'noProxy': ''})
		self.proxy = proxy
		return proxy
	
	def get_url(self,url):
		self.url = url
		self.driver.get(url)
				
	def close_popup(self):
		# Switch to new window opened, close and switch back to original windows
		self.driver.switch_to.window(self.driver.window_handles[-1])
		self.driver.close()
		self.driver.switch_to.window(self.driver.window_handles[0])
		
	def verify_ip(self,block_country=False):
		url_privacy = "http://analyze.privacy.net/"
		self.get_url(url_privacy)
		self.wait.until(EC.presence_of_element_located((By.XPATH,'//table/tbody/tr/td/font/b')))
		ip   = self.driver.find_element_by_xpath('//table/tbody/tr/td/font/b').text
		elem = self.driver.find_element_by_xpath('//table/tbody/tr/td/font/br/..')
		text = elem.text.split('\n')
		loc = text[0]
		self.close_popup()
		for i in xrange(len(text)):
			if "Browser Type" in text[i]:browsernm = text[i+1]
		output = 'ip: %s (%s)\nsystem info: %s' % (ip,loc,browsernm)
		print output
		if block_country:
			for c in block_country:
				if c in loc:
					raise NameError("country blocked")
		return ip,loc


def main():
	print 'here starts main program'
	


if __name__ == "__main__":
    main()
