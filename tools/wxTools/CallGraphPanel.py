import wx
import re
import os
import pickle
import ConfigParser
import IMix
import IUtils
import DotExternal
class CallGraphPanel(IMix.IProgPanel):
	def __init__(self,parent,settingfile):
		self.settings=settingfile
		self.splitptn=re.compile(r'([^0-9A-Za-z_]|\n)+')
		self.taskcount=0
		self.LoadConfig()
		super(CallGraphPanel,self).__init__(parent,name='CallGraphPanel')
	def LoadConfig(self):
		config=ConfigParser.RawConfigParser()
		config.read(self.settings)
		if config.has_option('CallGraphPanel','Dot'):
			dot=config.get('CallGraphPanel','Dot')
			if not os.path.exists(dot):
				dot=None
		else:
			dot=None
		if config.has_option('CallGraphPanel','Explorer'):
			explorer=config.get('CallGraphPanel','Explorer')
			if not os.path.exists(explorer):
				explorer=u'explorer.exe'
		else:
			explorer=u'explorer.exe'
		self.InitTools(dot,explorer)
	def InitTools(self,dot,explorer):
		self.start=IUtils.SimpleExternalTools(explorer,checkavailble=False)
		self.dot=DotExternal.DotExternalTools(dot)
	def DoLayout(self):
		self.srcpath=wx.StaticText(self,label='None')
		self.input=wx.TextCtrl(self,style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE)
		btn0=wx.Button(self,label='Open')
		btn1=wx.Button(self,label='Called')
		btn2=wx.Button(self,label='Calls')
		btn3=wx.Button(self,label='Clear')
		self.chk1=wx.CheckBox(self,label='AllowRepeatFunc')
		self.chk2=wx.CheckBox(self,label='AllowRepeatAll')
		self.spin=wx.SpinCtrl(self,min=0,max=99,initial=0)
		self.exinput=wx.TextCtrl(self,style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE)
		self.exinput.SetValue("memset,memcpy,memcmy")
		sizer1=wx.BoxSizer(wx.HORIZONTAL)
		sizer2=wx.BoxSizer(wx.HORIZONTAL)
		sizer3=wx.BoxSizer(wx.HORIZONTAL)
		sizer1.Add(btn0)
		sizer1.Add((8,8))
		sizer1.Add(wx.StaticText(self,label='SrcBase:'),flag=wx.ALIGN_CENTER_VERTICAL)
		sizer1.Add(self.srcpath,flag=wx.ALIGN_CENTER_VERTICAL)
		sizer2.Add(btn1)
		sizer2.Add(btn2)
		sizer2.Add((8,8))
		sizer2.Add(btn3)
		sizer2.Add((16,16))
		sizer2.Add(wx.StaticText(self,label='MaxDepth(ForCalls):'))
		sizer2.Add(self.spin)
		sizer3.Add(self.chk1)
		sizer3.Add(self.chk2)
		self._sizer.Add(sizer1)
		self._sizer.Add(self.input,1,wx.EXPAND)
		self._sizer.Add(sizer2)
		self._sizer.Add(sizer3)
		self._sizer.Add(wx.StaticText(self,label='Exclude Function List(ForCalls):'))
		self._sizer.Add(self.exinput,1,wx.EXPAND)
		self.Bind(wx.EVT_BUTTON,self.OnBtnOpen,btn0)
		self.Bind(wx.EVT_BUTTON,self.OnBtnCalled,btn1)
		self.Bind(wx.EVT_BUTTON,self.OnBtnCalls,btn2)
		self.Bind(wx.EVT_BUTTON,self.OnBtnClear,btn3)
		if not self.start:
			btn0.Disable()
	def SetSrcpath(self,srcpath):
		if srcpath:
			self.srcbase=srcpath
			txt="%-32s%s" % (srcpath[0],srcpath[1])
			self.srcpath.SetLabel(txt)
		else:
			self.srcpath.SetLabel('None')
	def GetFuncList(self):
		return self._getFuncList(self.input)
	def GetExFuncList(self):
		return self._getFuncList(self.exinput)
	def _getFuncList(self,inputctl):
		txt=self.splitptn.sub(',',inputctl.GetValue())
		items=txt.strip(',').split(',')
		return items
	def GenGraph(self,type):
		if self.srcpath.GetLabel() != 'None':
			items=self.GetFuncList()
			self.StartBusy()
			self.dot.SetWorkingDir(self.srcbase[1])
			if type==1:
				self.dot.SetFuncs(items,1,self.chk1.IsChecked(),self.chk2.IsChecked())
			else:
				items2=self.GetExFuncList()
				self.dot.SetFuncs(items,-1,self.chk1.IsChecked(),self.chk2.IsChecked(),self.spin.GetValue(),items2)
			task=IMix.IWXThread((DotExternal.DotExternalTools.Run,self.dot,),(CallGraphPanel.StopBusy,self,))
			task.start()
	def OnBtnOpen(self,event):
		if self.srcpath.GetLabel() != 'None':
			self.StartBusy()
			self.start.SetManualParam((self.srcbase[1],))
			task=IMix.IWXThread((IUtils.SimpleExternalTools.Run,self.start,),(CallGraphPanel.StopBusy,self,))
			task.start()
	def OnBtnCalled(self,event):
		self.GenGraph(1)
	def OnBtnCalls(self,event):
		self.GenGraph(2)
	def OnBtnClear(self,event):
		self.input.Clear()
	def StartBusy(self):
		if self.taskcount<1:
			self.taskcount=1
		super(CallGraphPanel,self).StartBusy()
	def StopBusy(self):
		self.taskcount-=1
		if self.taskcount<1:
			super(CallGraphPanel,self).StopBusy()

