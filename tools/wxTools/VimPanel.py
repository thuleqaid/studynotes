import wx
import os
import re
import pickle
import ConfigParser
import IMix
import IUtils
import VimExternal

class VimPanel(IMix.IProgPanel):
	D_INDEX_FILE='cscope.index'
	D_LANG_LIST=('C/C++','Python')
	P_LANG_LIST=(re.compile(r'\.(c|c\+\+|cc|cp|cpp|cxx|h|h\+\+|hh|hp|hpp|hxx)$'),
				 re.compile(r'\.(py|pyx|pxd|pxi|scons)$'))
	def __init__(self,parent,settingfile):
		self.settings=settingfile
		self.taskcount=0
		self.LoadConfig()
		super(VimPanel,self).__init__(parent,name='VimPanel')
	def DoLayout(self):
		sizer1=wx.BoxSizer(wx.HORIZONTAL)
		sizer2=wx.BoxSizer(wx.HORIZONTAL)
		btn1=wx.Button(self,label='Add')
		btn2=wx.Button(self,label='Delete')
		self.listb=wx.ListBox(self)
		listfont=wx.Font(11,family=wx.FONTFAMILY_MODERN,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL)
		self.listb.SetFont(listfont)
		sizer1.Add(btn1)
		sizer1.Add(btn2)
		sizer2.Add(self.listb,1,wx.EXPAND)
		self._sizer.Add(sizer1)
		self._sizer.Add(sizer2,1,wx.EXPAND)
		self.Bind(wx.EVT_BUTTON,self.OnBtnAdd,btn1)
		self.Bind(wx.EVT_BUTTON,self.OnBtnDel,btn2)
		self.Bind(wx.EVT_LISTBOX_DCLICK,self.OnListBoxDClick,self.listb)
		if not self.cscope:
			btn1.Disable()
		for item in self.listdata:
			self.AppendList(item)
	def LoadConfig(self):
		config=ConfigParser.RawConfigParser()
		config.read(self.settings)
		if config.has_option('VimPanel','Vim'):
			vim=os.path.join(os.getcwdu(),config.get('VimPanel','Vim'))
		else:
			vim=None
		if config.has_option('VimPanel','Ctags'):
			ctags=os.path.join(os.getcwdu(),config.get('VimPanel','Ctags'))
		else:
			ctags=os.path.join(os.getcwdu(),u'bin',u'ctags.exe')
		if not os.path.exists(ctags):
			ctags=None
		if config.has_option('VimPanel','Cscope'):
			cscope=os.path.join(os.getcwdu(),config.get('VimPanel','Cscope'))
		else:
			cscope=os.path.join(os.getcwdu(),u'bin',u'cscope.exe')
		if not os.path.exists(cscope):
			cscope=None
		if config.has_option('VimPanel','List'):
			self.listfile=os.path.join(os.getcwdu(),config.get('VimPanel','List'))
		else:
			self.listfile=os.path.join(os.getcwdu(),'vimlist.dat')
		self.InitTools(vim,ctags,cscope)
		self.LoadList()
	def InitTools(self,vim,ctags,cscope):
		if cscope:
			self.cscope=IUtils.SimpleExternalTools(cscope)
			self.cscope.SetManualParam(('-Rbc','-i',self.__class__.D_INDEX_FILE))
		else:
			self.cscope=None
		if vim:
			self.vim=VimExternal.VimExternalTools(vim)
			if ctags:
				self.ctags=IUtils.SimpleExternalTools(ctags)
				self.ctags.SetManualParam(('-R',))
		else:
			self.vim=None
			self.ctags=None
	def LoadList(self):
		if os.path.exists(self.listfile):
			fd=open(self.listfile,'r')
			self.listdata=pickle.load(fd)
			fd.close()
		else:
			self.listdata=[]
	def SaveList(self):
		fd=open(self.listfile,'w')
		pickle.dump(self.listdata,fd)
		fd.close()
	def AppendList(self,item):
		txt="%-32s%s" % (item[0],item[1])
		self.listb.InsertItems((txt,),self.listb.GetCount())
	def OnBtnAdd(self,event):
		dd=SrcDirDialog(self,"Select Source Folder",self.__class__.D_LANG_LIST)
		if wx.ID_OK==dd.ShowModal() and dd.GetPath():
			srcpath=dd.GetPath()
			desc=dd.GetDesc()
			if not desc:
				desc=os.path.split(srcpath)[1]
		#dd=wx.DirDialog(self,message='Select Source Folder')
		#if wx.ID_OK==dd.ShowModal():
			#srcpath=dd.GetPath()
			#ddd=wx.TextEntryDialog(self,message='Description')
			#if wx.ID_OK==ddd.ShowModal():
				#desc=ddd.GetValue()
			#else:
				#desc=os.path.split(srcpath)[1]
			self.StartBusy()
			self.cscope.SetWorkingDir(srcpath)
			if self.vim:
				self.ctags.SetWorkingDir(srcpath)
				self.taskcount=2
			else:
				self.taskcount=1
			self.cscopeindex(srcpath,dd.GetListItem(),self.__class__.D_INDEX_FILE)
			task=IMix.IWXThread((IUtils.SimpleExternalTools.Run,self.cscope,),(VimPanel.StopBusy,self,))
			task.start()
			if self.vim:
				task=IMix.IWXThread((IUtils.SimpleExternalTools.Run,self.ctags,),(VimPanel.StopBusy,self,))
				task.start()
			item=tuple((desc,srcpath,))
			self.AppendList(item)
			self.listdata.append(item)
			self.SaveList()
	def OnBtnDel(self,event):
		sels=self.listb.GetSelections()
		if sels:
			self.listb.Delete(sels[0])
			del self.listdata[sels[0]]
			self.SaveList()
	def OnListBoxDClick(self,event):
		if self.vim:
			sels=self.listb.GetSelections()
			if sels:
				self.StartBusy()
				self.vim.SetWorkingDir(self.listdata[sels[0]][1])
				task=IMix.IWXThread((VimExternal.VimExternalTools.Run,self.vim,),(VimPanel.StopBusy,self,))
				task.start()
	def GetSelectedItem(self):
		sels=self.listb.GetSelections()
		if sels:
			return self.listdata[sels[0]]
		else:
			return None
	def StartBusy(self):
		if self.taskcount<1:
			self.taskcount=1
		super(VimPanel,self).StartBusy()
	def StopBusy(self):
		self.taskcount-=1
		if self.taskcount<1:
			super(VimPanel,self).StopBusy()
	def cscopeindex(self,rootpath,lang='C/C++',indexfile='cscope.files'):
		if lang not in self.__class__.D_LANG_LIST:
			return False
		pidx=self.__class__.D_LANG_LIST.index(lang)
		pat=self.__class__.P_LANG_LIST[pidx]
		outlist=[]
		if os.path.exists(rootpath) and os.path.isdir(rootpath):
			for dirpath,dirnames,filenames in os.walk(rootpath):
				for fname in filenames:
					if pat.search(fname):
						outlist.append(os.path.relpath(os.path.join(dirpath,fname),rootpath))
		fh=open(os.path.join(rootpath,indexfile),'w')
		fh.write("\n".join(outlist))
		fh.close()

class SrcDirDialog(wx.Dialog):
	def __init__(self,parent,title,lst,pos=wx.DefaultPosition,size=(320,160),style=wx.DEFAULT_DIALOG_STYLE):
		wx.Dialog.__init__(self, parent, -1, title, pos, size, style)
		self._desc=wx.TextCtrl(self,-1,"")
		self._srcpath=wx.TextCtrl(self,-1,"")
		self._list=wx.ComboBox(self,-1,choices=lst,style=wx.CB_READONLY)
		self._list.SetSelection(0)
		btn1=wx.Button(self,label='...')
		self.Bind(wx.EVT_BUTTON,self.OnBtnOpen,btn1)
		ok=wx.Button(self,wx.ID_OK,"OK")
		cancel=wx.Button(self,wx.ID_CANCEL,"Cancel")
		sizer=wx.GridBagSizer(5,5)
		sizer.Add(wx.StaticText(self,-1,"SourcePath:"),(0,0))
		sizer.Add(self._srcpath,(0,1),(1,2),flag=wx.EXPAND)
		sizer.Add(btn1,(0,3))
		sizer.Add(wx.StaticText(self,-1,"Description:"),(1,0))
		sizer.Add(self._desc,(1,1),(1,3),flag=wx.EXPAND)
		sizer.Add(wx.StaticText(self,-1,"Language:"),(2,0))
		sizer.Add(self._list,(2,1),(1,3),flag=wx.EXPAND)
		sizer.Add(ok,(3,2))
		sizer.Add(cancel,(3,3))
		self.SetSizer(sizer)
		self.Layout()
	def GetPath(self):
		return self._srcpath.GetValue()
	def GetDesc(self):
		return self._desc.GetValue()
	def GetListItem(self):
		return self._list.GetStringSelection()
	def OnBtnOpen(self,event):
		dd=wx.DirDialog(self,message='Select Source Folder')
		if wx.ID_OK==dd.ShowModal():
			srcpath=dd.GetPath()
			self._srcpath.SetValue(srcpath)
