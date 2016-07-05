#! /usr/bin/env python

from IPython import embed
#embed() # this call anywhere in your program will start IPython

import sys, os

		
class Datapoint():
	def __init__(self,date,names,prices):
		self.date=date
		self.names=names
		self.prices=prices

class Event():
	
	def __init__(self,url,ename,edate):
		self.url=url
		self.ename=ename
		self.edate=edate
		self.datapoints=[]
	
	def addDatapoint(self,date,names,prices):
		Data=Datapoint(date,names,prices)
		self.datapoints.append(Data)			
