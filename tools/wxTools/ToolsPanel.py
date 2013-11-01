import wx
import IMix
import IGui

class MyFileDropTarget(wx.FileDropTarget):
	def __init__(self, window):
		super(MyFileDropTarget,self).__init__()
		self.window = window
	def OnDropFiles(self, x, y, filenames):
		self.window.InsertItems(filenames,self.window.GetCount())

class CompressDialog(IGui.IDialog):
	def __init__(self,parent):
		super(CompressDialog,self).__init__(parent,title='Compress Option')
	def DoLayout(self):
		label = wx.StaticText(self, -1, "This is a wx.Dialog")
		self._sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		box = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, -1, "Field #1:")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		text = wx.TextCtrl(self, -1, "", size=(80,-1))
		box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
		self._sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		box = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, -1, "Field #2:")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		text = wx.TextCtrl(self, -1, "", size=(80,-1))
		box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
		self._sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

class ToolsPanel(IMix.IProgPanel):
	def __init__(self,parent,id=wx.ID_ANY,pos=wx.DefaultPosition,size=wx.DefaultSize,style=wx.TAB_TRAVERSAL,name='FiboPanel'):
		super(ToolsPanel,self).__init__(parent,id,pos,size,style,name)
	def DoLayout(self):
		self.listbox=wx.ListBox(self, style=wx.LB_EXTENDED|wx.LB_HSCROLL|wx.LB_NEEDED_SB)
		self.listbox.SetDropTarget(MyFileDropTarget(self.listbox))
		self.btnUp=wx.Button(self,label='MoveUp')
		self.btnDown=wx.Button(self,label='MoveDown')
		self.btnDel=wx.Button(self,label='Remove')
		self.btnClr=wx.Button(self,label='Clear')
		self.Bind(wx.EVT_BUTTON,self.OnBtnUp,self.btnUp)
		self.Bind(wx.EVT_BUTTON,self.OnBtnDown,self.btnDown)
		self.Bind(wx.EVT_BUTTON,self.OnBtnRm,self.btnDel)
		self.Bind(wx.EVT_BUTTON,self.OnBtnClr,self.btnClr)

		self.btnCompress=wx.Button(self,label='Compress')
		self.Bind(wx.EVT_BUTTON,self.OnBtnCompress,self.btnCompress)
		
		hsizer1=wx.BoxSizer(wx.HORIZONTAL)
		hsizer2=wx.BoxSizer(wx.HORIZONTAL)
		hsizer3=wx.BoxSizer(wx.HORIZONTAL)
		hsizer1.Add(wx.StaticText(self,label='Drop files here:'),flag=wx.ALIGN_CENTER_VERTICAL)
		hsizer2.Add(self.btnUp,0,wx.ALL,5)
		hsizer2.Add(self.btnDown,0,wx.ALL,5)
		hsizer2.Add(self.btnDel,0,wx.ALL,5)
		hsizer2.Add(self.btnClr,0,wx.ALL,5)
		hsizer3.Add(self.btnCompress,0,wx.ALL,5)
		self._sizer.Add(hsizer1)
		self._sizer.Add(self.listbox,1,wx.EXPAND|wx.ALL)
		self._sizer.Add(hsizer2)
		self._sizer.Add(hsizer3)
	def OnBtnUp(self,event):
		sels=self.listbox.GetSelections()
		if len(sels)==1 and sels[0]>0:
			items=self.listbox.GetStrings()
			items[sels[0]],items[sels[0]-1]=items[sels[0]-1],items[sels[0]]
			self.listbox.Set(items)
			self.listbox.SetSelection(sels[0]-1)
	def OnBtnDown(self,event):
		sels=self.listbox.GetSelections()
		if len(sels)==1 and sels[0]<self.listbox.GetCount()-1:
			items=self.listbox.GetStrings()
			items[sels[0]],items[sels[0]+1]=items[sels[0]+1],items[sels[0]]
			self.listbox.Set(items)
			self.listbox.SetSelection(sels[0]+1)
	def OnBtnRm(self,event):
		sels=self.listbox.GetSelections()
		for sel in sels[::-1]:
			self.listbox.Delete(sel)
	def OnBtnClr(self,event):
		self.listbox.Clear()
	def OnBtnCompress(self,event):
		dlg = CompressDialog(self)
		val = dlg.ShowModal()
		if val == wx.ID_OK:
			print 'ok'
		dlg.Destroy()
	def OnButton(self,event):
		#input=self.input.GetValue()
		#self.output.SetValue('')
		#self.StartBusy()
		#task=IMix.IWXThread((fibo,int(input),),(FiboPanel.SetResult,self,))
		#task.start()
		pass
	def SetResult(self,n):
		#self.output.SetValue(str(n))
		#self.StopBusy()
		pass
