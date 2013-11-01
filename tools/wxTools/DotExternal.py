import os
import subprocess
import IUtils
import cscope_parser

class DotExternalTools(IUtils.IExternalTools):
	def __init__(self,toolpath):
		super(DotExternalTools,self).__init__(toolpath)
		self._srcpath=''
		self._parser=cscope_parser.CscopeParser(cache=True)
		self._funcs=[]
		self._dir=1
	def SetWorkingDir(self,srcpath,filename=u'cscope.out'):
		dbfile=os.path.join(srcpath,filename)
		if os.path.exists(dbfile) and os.path.isfile(dbfile):
			self._srcpath=dbfile
			self._parser.SetDBFile(self._srcpath)
			self._funcs=[]
			self._dir=0
	def SetFuncs(self,funcs,dir=1,allowrepeat_func=True,allowrepeat_all=False,maxlevel=0,exfuncs=()):
		self._funcs=funcs[:]
		self._dir=dir
		self._allow1=allowrepeat_func
		self._allow2=allowrepeat_all
		self._maxlevel=maxlevel
		self._exfuncs=exfuncs[:]
	def DoRun(self):
		if self._srcpath:
			self._parser.DoParse()
			if self._dir>=0:
				self._parser.TrackUp(self._funcs,allowrepeat_func=self._allow1,allowrepeat_all=self._allow2)
			else:
				self._parser.TrackDown(self._funcs,allowrepeat_func=self._allow1,allowrepeat_all=self._allow2,maxlevel=self._maxlevel,exfuncs=self._exfuncs)
			try:
				for func in self._funcs:
					params=[]
					params.append(self._tools)
					params.append('-Tpng')
					if self._dir>=0:
						params.append(func+u'#d.dot')
					else:
						params.append(func+u'#c.dot')
					params.append('-o')
					if self._dir>=0:
						params.append(func+u'#d.png')
					else:
						params.append(func+u'#c.png')
					subprocess.check_call(params)
				if len(self._funcs)>1:
					params=[]
					params.append(self._tools)
					params.append('-Tpng')
					if self._dir>=0:
						params.append(u'_ALL_#d.dot')
					else:
						params.append(u'_ALL_#c.dot')
					params.append('-o')
					if self._dir>=0:
						params.append(u'_ALL_#d.png')
					else:
						params.append(u'_ALL_#c.png')
					subprocess.check_call(params)
			except subprocess.CalledProcessError as err:
				self._errorflag=True
				self.RunError(err)
