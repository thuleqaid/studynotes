import threading
import os
import subprocess

class IThread(threading.Thread):
	def __init__(self,threadfunc,finalfunc):
		#threadfunc=(func,arg1,arg2,...)
		#finalfunc=(func,arg1,arg2,...)
		super(IThread,self).__init__()
		self._threadfunc=tuple(threadfunc)
		self._finalfunc=tuple(finalfunc)
	def RunThreadFunc(self):
		ret=None
		if self._threadfunc:
			if len(self._threadfunc)>1:
				ret=self._threadfunc[0](*self._threadfunc[1:])
			else:
				ret=self._threadfunc[0]()
		return ret
	def RunFinalFunc(self,val):
		param=[]
		if self._finalfunc:
			if len(self._finalfunc)>1:
				param[:]=self._finalfunc[1:]
				if val:
					param.append(val)
				self._threadfunc[0](*self._threadfunc[1:])
			else:
				if val:
					self._threadfunc[0](val)
				else:
					self._threadfunc[0]()
	def run(self):
		ret=self.RunThreadFunc()
		self.RunFinalFunc(ret)

class IExternalTools(object):
	def __init__(self,toolpath=u'',checkavailble=True):
		self._currentpath=os.getcwdu()
		self._tools=u''
		self._param=[]
		self._manualparam=[]
		self._errorflag=False
		self.SetExePath(toolpath,checkavailble)
	def SetExePath(self,exepath,checkavailble=True):
		if checkavailble:
			if os.path.exists(exepath) and os.path.isfile(exepath):
				self._tools=exepath
				self._param=[]
				self._manualparam=[]
				self._errorflag=False
		else:
			self._tools=exepath
			self._param=[]
			self._manualparam=[]
			self._errorflag=False
	def SetManualParam(self,params):
		self._manualparam[:]=params[:]
	def ClearManualParam(self):
		self._manualparam=[]
	def ChgDir(self,destpath):
		if os.path.exists(destpath) and os.path.isdir(destpath):
			os.chdir(destpath)
	def RestoreDir(self):
		self.ChgDir(self._currentpath)
	def PreRun(self):
		pass
	def PostRun(self):
		pass
	def RunError(self,err):
		pass
	def IsError(self):
		return self._errorflag
	def DoRun(self):
		params=[]
		params.append(self._tools)
		params.extend(self._param)
		if self._manualparam:
			params.extend(self._manualparam)
		try:
			subprocess.check_call(params)
		except subprocess.CalledProcessError as err:
			self._errorflag=True
			self.RunError(err)
	def Run(self):
		self.PreRun()
		self.DoRun()
		self.PostRun()

class SimpleExternalTools(IExternalTools):
	def __init__(self,toolpath,checkavailble=True):
		super(SimpleExternalTools,self).__init__(toolpath,checkavailble)
		self._srcpath=''
	def SetWorkingDir(self,srcpath):
		if os.path.exists(srcpath) and os.path.isdir(srcpath):
			self._srcpath=srcpath
	def PreRun(self):
		if self._srcpath:
			self.ChgDir(self._srcpath)
	def PostRun(self):
		if self._srcpath:
			self.RestoreDir()
