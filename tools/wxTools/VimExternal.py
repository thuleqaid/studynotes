import os
import tempfile
import IUtils

class VimExternalTools(IUtils.IExternalTools):
	def __init__(self,toolpath):
		super(VimExternalTools,self).__init__(toolpath)
		self._srcpath=''
		self._tmpfile=''
		self._tmpdir=''
		self.RemoveTempFile()
	def SetWorkingDir(self,srcpath):
		if os.path.exists(srcpath) and os.path.isdir(srcpath):
			self._srcpath=srcpath
	def MakeTempFile(self):
		self._tmpfile=tempfile.NamedTemporaryFile(dir=self._tmpdir,delete=False)
		self._tmpfile.write(':STag '+self._srcpath+"\n")
		self._tmpfile.close()
	def RemoveTempFile(self):
		cwd=os.getcwdu()
		self._tmpdir=os.path.join(cwd,'temp')
		if (os.path.exists(self._tmpdir) and os.path.isdir(self._tmpdir)):
			for f in os.listdir(self._tmpdir):
				os.remove(os.path.join(self._tmpdir,f))
		else:
			os.mkdir(self._tmpdir)
	def PreRun(self):
		if self._srcpath:
			self._tmpfile=''
			self._param=[]
			self.MakeTempFile()
			self._param.append('-s')
			self._param.append(self._tmpfile.name)
