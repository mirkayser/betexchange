#! /usr/bin/env python

from IPython import embed
#embed() # this call anywhere in your program will start IPython

import sys, os, time, progressbar
import datetime
import pickle
import numpy as np
import matplotlib.pyplot as mp
import matplotlib.gridspec as gridspec
from glob import glob



class Data_Handle():
	
	def __init__(self,timeunit=60, load=False):
		
		self.fname = 'Data/data.npy'
		self.timeunit=float(timeunit)
		
		if load: self.load_data()
		else: self.cut_raw_data()

		
	def cut_raw_data(self):

		def gen_array(events):
			
			count=0
			alist=[]
			for i in xrange(len(events)):
				
				x = events[i]
				
				event_ids,runner_ids,runner_names,point_nums,deltas,prices = [],[],[],[],[],[]
				for rname in x['data'].keys():
					for j,item in enumerate(x['data'][rname]):
						delta = -( (x['time']-item[0]).total_seconds() ) /self.timeunit
						price = np.round(item[1],2)
						
						event_ids.append(i)
						runner_ids.append(count)
						runner_names.append(rname)
						point_nums.append(j)
						deltas.append(delta)
						prices.append(price)
						
					count+=1
						
				array = np.array(zip(event_ids,runner_ids,runner_names,point_nums,deltas,prices),dtype=[('eid',int),('rid',int),('name','S30'),('num',int),('time',float),('price',float)])
				alist.append(array)
			
			return alist
		
		print 'reading events from raw data...'
			
		inputdir  = 'Data/raw/'
		
		fnames = glob(inputdir+'*')		
		
		events = []		
		bar = progressbar.ProgressBar()
		for fname in bar(fnames):	
			with open(fname,'rb')as inputfile: event = pickle.load(inputfile)
			
			data = event['data']
			
			#erase runners with empty list
			for k in data.keys():
				if len(data[k])==0: 
					data.pop(k,None)
		
			#skip sets without data
			if len(data.keys())<1: continue
			
			#skip sets without complete data
			elif datetime.timedelta(minutes=15) < ( event['time_e'] - data[data.keys()[0]][-1][0]):	continue
			
			#save quality data sets 
			else:
				event['time']=event['data'][event['data'].keys()[-1]][-1][0]
				events.append(event)
		
		alist = gen_array(events)
		np.save(self.fname,alist)
		self.alist = alist
		
		print '%d of %d events written to %s\n' % (len(events),len(fnames),self.fname)

	def load_data(self):
		self.alist = np.load(self.fname)
		print '%d events read from %s\n' % (self.get_size(),self.fname)

	def get_size(self):
		return len(self.alist)

	def draw_event(self,eid):
		
		from my.tools import colorlist
		
		mp.figure(num=1, figsize=(8, 6), dpi=80)
		mp.clf()
		gs1 = gridspec.GridSpec(1,1)
		ax1 = mp.subplot(gs1[0, 0])
		
		event = self.get_event(eid)
		
		for i,name in enumerate(set(event['name'])):
			
			if i>=15: break
			
			else:
				runner = event[event['name']==name]
				
				xs = runner['time']
				ys = runner['price']
				
				ax1.plot(xs,ys,marker='',ls='-',c=colorlist()[i])
			
		ax1.set_title(r'Event %d' % eid)
		ax1.set_xlabel(r'price', size='large')
		ax1.set_ylabel(r'time', size='large')
		#~ ax1.set_xlim(left=np.min(x)-.5,right=np.max(x)+.5)
		mp.savefig('event_%d.pdf' % eid)

	def get_event(self,eid):
		return self.alist[eid]
	

			
def main():
	print 'here starts main program'

	from my.tools import Timer
	timer=Timer()
			
	d = Data_Handle(load=1)
	
	for i in xrange(15):
		d.draw_event(i)
	
	e4 = d.get_event(4)
	e5 = d.get_event(5)

	
	timer.stop()
	
	#~ mp.show()

if __name__ == "__main__":
    main()
