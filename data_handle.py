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

from pyik.performance import cached

np.set_printoptions(precision=3, threshold=300, linewidth=100)

class Data_Handle():
	
	def __init__(self,timeunit=60):
		
		self.fname = 'Data/data.npy'
		self.timeunit=float(timeunit)
		
	def cut_raw_data(self,fnames,analysis=True,remove=False):
		
		def gen_datalist(events):
			
			print 'generating datalist...'
			
			count=0
			linklist,datalist=[],[]
			bar = progressbar.ProgressBar()
			for i in bar(xrange(len(events))):
				
				x = events[i]
				
				event_ids,runner_ids,runner_names,point_nums,deltas,prices = [],[],[],[],[],[]
				for rname in x['data'].keys():
					for j,item in enumerate(x['data'][rname]):
						delta = -( (x['time']-item[0]).total_seconds() ) /self.timeunit
						price = np.round(item[1],3)
						
						event_ids.append(i)
						runner_ids.append(count)
						runner_names.append(rname)
						point_nums.append(j)
						deltas.append(delta)
						prices.append(price)
						
					count+=1
						
				array = np.array(zip(event_ids,runner_ids,runner_names,point_nums,deltas,prices),dtype=[('eid',int),('rid',int),('name','S30'),('num',int),('time',float),('price',float)])
				datalist.append( array )
				linklist.append( events[i]['link'] )
			
			return datalist,linklist
		
		def main_function():
		
			print 'reading %d events...' % len(fnames)
			
			rm_count=0
			events = []		
			bar = progressbar.ProgressBar()
			for fname in bar(fnames):	
				
				uncomplete=False
				
				with open(fname,'rb')as inputfile: event = pickle.load(inputfile)
				
				data = event['data']
				
				#erase runners with empty list
				for k in data.keys():
					if len(data[k])==0: 
						data.pop(k,None)
			
				#skip sets without data
				if len(data.keys())<1: 
					uncomplete=True
				
				#skip sets without complete data
				if analysis:	min_timedelta=50
				else:					min_timedelta=15
				
				if len(data.keys())==0: 
					uncomplete=True
				elif datetime.timedelta(minutes=min_timedelta) < ( event['time_e'] - data[data.keys()[0]][-1][0] ):	
					uncomplete=True
				
				#save quality data sets 
				if not uncomplete:
					#~ event['time']=event['data'][event['data'].keys()[-1]][-1][0]
					event['time']=event['time_e']
					events.append(event)
				
				#remove files
				if remove and uncomplete:
					os.system('rm %s' % fname.replace("(","\(").replace(")","\)"))
					rm_count+=1
			
			if len(events)>0:		
				datalist,linklist = gen_datalist(events)
				self.datalist = datalist
				self.linklist = linklist
				
				if not analysis:
					np.save(self.fname,datalist)
					print '%d of %d events read into dataset & written to %s\n' % (len(events),len(fnames),self.fname)
				else:
					print '%d of %d events read into dataset\n' % (len(events),len(fnames))
			
			else:
				raise ValueError('No valid events found')
			
			if remove: print '%d events removed' % rm_count
		
		main_function()
		
		return self

	def load_data(self,verbose=True):
		self.datalist = np.load(self.fname)
		if verbose: print '%d events read from %s\n' % (self.get_size(),self.fname)
		
		return self

	def get_size(self):
		return len(self.datalist)

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
		return self.datalist[eid]
	
	def get_datalist(self):
		return self.datalist

	def get_linklist(self):
		return self.linklist

class DataML():
	
	def get_size(self):
		return len(self.datalist)
	
	def get_runner_ids(self,array):
		return set(array['rid'])
	
	def set_cut_pars(self,ucut,lcut,split):
		self.cut_pars = { 'ucut':ucut, 'lcut':lcut, 'split':split }
				
	def split_arrays(self,datalist):
		
		ucut = self.cut_pars['ucut']
		lcut = self.cut_pars['lcut']
		split = self.cut_pars['split']
		
		flist,rlist=[],[]
		for i in xrange(len(datalist)):
			
			array=datalist[i]
			
			#cut datapoints too far back and too close to race
			array = array[array['time']>-ucut]
			array = array[array['time']<-lcut]
			
			#split in feature and result array
			fa = array[array['time']<-split]
			ra = array[array['time']>-split]
			
			flist.append(fa)
			rlist.append(ra)
			
		return flist,rlist		

	def get_result(self,eid,rid):
		
		a = self.rlist[eid]
		a = a[a['rid']==rid]		
		
		if len(a)>=5:	slope = self.get_slope(a['time'],a['price'])
		else:					slope = np.nan
		return slope
	
	def get_runner_name(self,eid,rid):
		a = self.datalist[eid]
		a = a[a['rid']==rid]
		if len(set(a['name']))>1: raise ValueError('more than one runner name for rid (%d)' % rid)
		else: return a['name'][0]

	def get_slope(self,xs,ys):
		
		A = ( xs[0],  ys[0] )
		B = ( xs[-1], ys[-1] )		
		
		s = (B[1]-A[1]) / (B[0]-A[0])
		
		return np.round(s,5)
		
	def get_maximas(self,ys):
		maximas=0
		for i in xrange(len(ys)):
			
			if i==0: continue
			
			else:
				
				if ys[i] > ys[i-1]: 		tmp=1  
				elif ys[i] == ys[i-1]: 	tmp=0
				elif ys[i] < ys[i-1]: 	tmp=-1

				if i==1: s=tmp
				else:
					if s==tmp: continue
					elif tmp==0: continue
					else:						
						s=tmp
						maximas+=1
		
		return maximas
	
	def get_features(self,eid,rid):
		
		a = self.flist[eid]
		a = a[a['rid']==rid]
		
		dic={}
		if len(a)>=5:	
			
			first  = a['price'][0]
			last   = a['price'][-1]
			median = np.median(a['price'])
			avg = np.average(a['price'])
			maximas= self.get_maximas(a['price'])
			tot_slope  = self.get_slope(a['time'],a['price'])
			end_slope  = self.get_slope(a['time'][-10:],a['price'][-10:])
			
			dic['first'] = first
			dic['last'] = last
			dic['median'] = median
			#~ dic['avg'] = avg
			dic['tot_slope'] = tot_slope
			dic['end_slope'] = end_slope
			#~ dic['med_dif'] = last-median		
			dic['maximas'] = maximas	
			
		else: dic['nan']=np.nan
					
		return dic
	
	def get_lists(self,datalist,analysis=True,max_price=None,cut_pars=[70,5,15],verbose=True):
		
		if verbose: print "  loading features from event-arrays..."
		
		self.datalist = datalist
		self.set_cut_pars(cut_pars[0],cut_pars[1],cut_pars[2],)
		self.flist,self.rlist = self.split_arrays(datalist)
		
		rnames,fnames,fs,rs = [],[],[],[]
		for eid in xrange(self.get_size()):
			
			a = self.datalist[eid]
			
			for rid in self.get_runner_ids(a):
			
				f = self.get_features(eid,rid)
				r = self.get_result(eid,rid)
				
				if not analysis and np.isnan(r): continue
				if f.has_key('nan'): continue
				
				if not max_price==None:
					if f['last']>max_price: continue
				
				flist = [ f[k] for k in sorted(f.keys()) ] 
				
				fs.append(flist)
				rs.append(r)
				
				rnames.append(self.get_runner_name(eid,rid))
		
		if verbose: print '  %d runners in data\n' % len(fs) 
		
		self.rnames = rnames
		self.fnames = sorted(f.keys())
		self.fs = np.array(fs)
		self.rs = np.array(rs)
		
		return self.rnames,self.fnames,self.fs, self.rs	

			
def main():
	print 'here starts main program'

	from my.tools import Timer
	timer=Timer()
	
	fnames = glob('Data/raw/'+'*')
			
	d = Data_Handle().cut_raw_data(fnames=fnames,analysis=False,remove=False)
	
	timer.stop()

if __name__ == "__main__":
    main()
