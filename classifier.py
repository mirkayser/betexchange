#! /usr/bin/env python

"""sklearn classifier"""

import numpy as np
from sklearn import cross_validation
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn import tree,neighbors
from sklearn.ensemble import BaggingClassifier

from data_handle import Data_Handle, DataML

from IPython import embed
#embed() # this call anywhere in your program will start IPython

np.set_printoptions(precision=3, threshold=50, linewidth=100)

def prepareData(features,result,limit=0.1):
	"""prepare samples for ml"""		
	
	y=[]
	for r in result:
		if r>limit:			y.append(1)
		elif r<-limit:	y.append(-1)
		else:						y.append(0)

	x=np.array(features)
	y=np.array(y)

	return x,y

class CombiCLF():
	
	"""classifier combining the results of ldac, bagging KNN and Bagging ClassTree"""
	
	def __init__(self):
		
		self.clfs={}
		
		#ldac
		self.clfs['ldac'] = LinearDiscriminantAnalysis()			
		
		#bagging knn
		self.clfs['bknn'] = BaggingClassifier(neighbors.KNeighborsClassifier(),max_samples=0.5, max_features=0.5)

		#ensemble bagging tree
		self.clfs['btree'] = BaggingClassifier(tree.DecisionTreeClassifier(),max_samples=0.5, max_features=0.5)
		
		self.trained = False
		
	def fit(self,x,y):
		
		for k in self.clfs.keys():
			self.clfs[k].fit(x,y)		
		
		self.trained=True
	
	def predict(self,x):
		
		if not self.trained: raise ValueError('CLF not trained, run self.fit()')
		
		t1 = self.clfs['ldac'].predict(x)
		t2 = self.clfs['bknn'].predict(x)
		t3 = self.clfs['btree'].predict(x)
		
		ym=[]
		for i in xrange(len(x)):
			if t1[i]==t2[i]==t3[i]:	ym.append(t1[i])
			else:										ym.append(np.nan)
		ym=np.array(ym)
		
		return ym
		
	def score(self,x,y):
		
		if not self.trained: raise ValueError('CLF not trained, run self.fit()')
		
		ym = self.predict(x)
		
		mask = np.isnan(ym)==False
		ym= ym[mask]
		y = y[mask]
		s = len(ym[ym==y])/float(len(ym))
		
		return s

	def get_size_subset(self,x):

		if not self.trained: raise ValueError('CLF not trained, run self.fit()')
		
		ym = self.predict(x)
		ym = ym[np.isnan(ym)==False]
		
		return len(ym)/float(len(x))

class HighProb():
	
	def __init__(self,clf,p):
		
		self.clf = clf
		self.p = p
		self.trained=False


	def fit(self,x,y):
		
		self.clf.fit(x,y)		
		self.trained=True
	
	def predict(self,x):
		
		if not self.trained: raise ValueError('CLF not trained, run self.fit()')
		
		p = self.clf.predict_proba(x) 
		
		ym=[]
		for i in xrange(len(x)):
			tmp=np.nan
			for j,cl in enumerate(self.clf.classes_):
				if p[i][j]>self.p:	tmp=cl 
			ym.append(tmp) 						
		ym=np.array(ym)
		
		return ym

	def predict_proba(self,x):
		
		if not self.trained: raise ValueError('CLF not trained, run self.fit()')
		
		p = self.clf.predict_proba(x) 
		
		ym,pm=[],[]
		for i in xrange(len(x)):
			tmp1,tmp2=np.nan,np.nan
			for j,cl in enumerate(self.clf.classes_):
				if p[i][j]>self.p:	
					tmp1=cl 
					tmp2=p[i][j]
			ym.append(tmp1)
			pm.append(tmp2)					
		ym=np.array(ym)
		pm=np.array(pm)
		
		return ym,pm
		
	def score(self,x,y):
		
		if not self.trained: raise ValueError('CLF not trained, run self.fit()')
		
		ym = self.predict(x)
		
		mask = np.isnan(ym)==False
		ym= ym[mask]
		y = y[mask]
		s = len(ym[ym==y])/float(len(ym))
		
		return s
		
	def get_size_subset(self,x):

		if not self.trained: raise ValueError('CLF not trained, run self.fit()')
		
		ym = self.predict(x)
		ym = ym[np.isnan(ym)==False]
		
		return len(ym)/float(len(x))

class Classifier():
	
	def __init__(self):	
		
		self.clfs={}
		
		#ldac
		self.clfs['ldac'] = LinearDiscriminantAnalysis()		

		#ensemble bagging knn
		self.clfs['bknn'] = BaggingClassifier(neighbors.KNeighborsClassifier(),max_samples=0.5, max_features=0.5)
		
		#ensemble bagging tree
		self.clfs['btree'] = BaggingClassifier(tree.DecisionTreeClassifier(),max_samples=0.5, max_features=0.5)
		
		#Combine the other three CLFs
		self.clfs['combi'] = CombiCLF()
		
		#high prob B-knn/B-Tree
		self.clfs['pknn'] =HighProb(self.clfs['bknn'],p=0.7)
		self.clfs['ptree']=HighProb(self.clfs['btree'],p=0.7)
		
		self.trained=False

	def cross_validation_clfs(self,x,y,xcontrol,num_cv=5):
		
		out = 'cross validation algorithms (cv=%d):\n' % num_cv
				 
		scores = self.cross_val_score(self.clfs['ldac'], x, y, num_cv=num_cv)
		out += "LDAC:	%0.2f (+/- %0.2f)\n" % (scores.mean(), scores.std() * 2)
		
		scores = self.cross_val_score(self.clfs['btree'], x, y, num_cv=num_cv)
		out += "B-Tree:	%0.2f (+/- %0.2f)\n" % (scores.mean(), scores.std() * 2)
		
		scores = self.cross_val_score(self.clfs['bknn'], x, y, num_cv=num_cv)
		out += "B-KNN:	%0.2f (+/- %0.2f)\n" % (scores.mean(), scores.std() * 2)
		
		self.clfs['combi'].fit(x,y)
		scores = self.cross_val_score(self.clfs['combi'], x, y, num_cv=num_cv)
		out += "Combi:	%0.2f (+/- %0.2f) -> subset=%0.2f\n" % (scores.mean(),scores.std()*2,self.clfs['combi'].get_size_subset(xcontrol))

		self.clfs['ptree'].fit(x,y)
		scores = self.cross_val_score(self.clfs['ptree'], x, y, num_cv=num_cv)
		out += "P-Tree:	%0.2f (+/- %0.2f) -> subset=%0.2f\n" % (scores.mean(),scores.std()*2,self.clfs['ptree'].get_size_subset(xcontrol))

		self.clfs['pknn'].fit(x,y)
		scores = self.cross_val_score(self.clfs['pknn'], x, y, num_cv=num_cv)
		out += "P-KNN:	%0.2f (+/- %0.2f) -> subset=%0.2f\n" % (scores.mean(),scores.std()*2,self.clfs['pknn'].get_size_subset(xcontrol))
		
		print out
		
	def cross_val_score(self,clf,x,y,num_cv=5):
		"""cross validation using k-fold"""
		
		from sklearn.cross_validation import KFold
		
		scores=[]
		kf = KFold(len(x), n_folds=num_cv)
		for train, test in kf:
			clf.fit(x[train],y[train])
			scores.append( clf.score(x[test],y[test]) )
		scores=np.array(scores)
		return scores	

	def fit(self,x,y):
		
		for k in self.clfs.keys():
			self.clfs[k].fit(x,y)
		
		self.trained = True

	def predict(self,clf_name,x):
		
		if not self.trained: raise ValueError('CLF not trained, run self.fit()')
		
		if clf_name in self.clfs.keys():
			return self.clfs[clf_name].predict(x)
		else:
			raise NameError('object has no clf named %s' % clf_name)

	def score(self,clf_name,x,y):
		
		if not self.trained: raise ValueError('CLF not trained, run self.fit()')
		
		if clf_name in self.clfs.keys():
			return self.clfs[clf_name].score(x,y)
		else:
			raise NameError('object has no clf named %s' % clf_name)

	def performance(self,x,y):
		
		if not self.trained: raise ValueError('CLF not trained, run self.fit()')
		
		out = 'performance algorithms:\n'
		for k in sorted(self.clfs.keys()):
			if getattr(self.clfs[k],"get_size_subset",None)==None:
				out += "%s:	%0.2f\n" % (k,self.clfs[k].score(x,y))
			else:		
				out += "%s:	%0.2f -> subset=%0.2f\n" % (k,self.clfs[k].score(x,y),self.clfs[k].get_size_subset(x))

		print out		
		
			
def main():
	print ''

	#load datalist from file
	datalist = Data_Handle(load=1).get_datalist()
	
	#randomize sample
	np.random.shuffle(datalist)
	
	#get lists (names,features,etc...)
	runner_names,feature_names,features,result = DataML().get_lists(datalist)
	
	#prepare data for classifiers
	x,y = prepareData(features,result,limit=0.1)
	
	#split in train and test samples (not random!!!)
	xtrain,xcontrol,ytrain,ycontrol = cross_validation.train_test_split(x,y,test_size=0.2,random_state=42)
	print 'Samples:\ntrain: %d\ncontrol: %d\n' % (len(x),len(xcontrol))	
	
	clf = Classifier()
	clf.cross_validation_clfs(xtrain,ytrain,xcontrol,num_cv=5)
	clf.fit(xtrain,ytrain)
	clf.performance(xcontrol,ycontrol)
		
		
if __name__ == "__main__":
    main()			
		
	




	
	

