import wx

class IFrame(wx.Frame):
	def __init__(self,parent,id=wx.ID_ANY,title='',pos=wx.DefaultPosition,size=wx.DefaultSize,style=wx.DEFAULT_FRAME_STYLE,name='IFrame'):
		super(IFrame,self).__init__(parent,id,title,pos,size,style,name)
		self._panel=self.InitMainPanel()
		sizer=wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self._panel,1,wx.EXPAND)
		self.SetSizer(sizer)
		self.InitMenuBar()
		self.InitToolBar()
		self.InitStatusBar()
		self._tbicon=self.InitTaskBarIcon()
		self.Bind(wx.EVT_CLOSE,self.OnCloseWindow)
		self.Bind(wx.EVT_ICONIZE,self.OnIconizeWindow)
	def OnCloseWindow(self,event):
		if self._tbicon is not None:
			self._tbicon.Destroy()
		self.Destroy()
	def OnIconizeWindow(self,event):
		if self._tbicon is not None:
			self.Hide()
	def InitMainPanel(self):
		pass
	def InitMenuBar(self):
		pass
	def InitToolBar(self):
		pass
	def InitStatusBar(self):
		pass
	def InitTaskBarIcon(self):
		return None


class INotebook(wx.Notebook):
	def __init__(self,parent,id=wx.ID_ANY,pos=wx.DefaultPosition,size=wx.DefaultSize,style=0,name='INotebook'):
		super(INotebook,self).__init__(parent,id,pos,size,style,name)
		self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
		self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
		self.DoLayout()
	def OnPageChanging(self, event):
		event.Skip()
	def OnPageChanged(self, event):
		event.Skip()
	def DoLayout(self):
		pass


class IPanel(wx.Panel):
	def __init__(self,parent,id=wx.ID_ANY,pos=wx.DefaultPosition,size=wx.DefaultSize,style=wx.TAB_TRAVERSAL,name='IPanel'):
		super(IPanel,self).__init__(parent,id,pos,size,style,name)
		self.InitSizer()
		self.DoLayout()
	def InitSizer(self):
		self._sizer=wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self._sizer)
	def DoLayout(self):
		pass

class IDialog(wx.Dialog):
	def __init__(self, parent, id=wx.ID_ANY, title='Dialog', pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE):
		pre = wx.PreDialog()
		pre.Create(parent, id, title, pos, size, style)
		self.PostCreate(pre)
		self.InitSizer()
	def InitSizer(self):
		self._sizer=wx.BoxSizer(wx.VERTICAL)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self._sizer,1,wx.EXPAND)
		line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
		sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
		btnsizer = wx.StdDialogButtonSizer()
		btn = wx.Button(self, wx.ID_OK)
		btn.SetDefault()
		btnsizer.AddButton(btn)
		btn = wx.Button(self, wx.ID_CANCEL)
		btnsizer.AddButton(btn)
		btnsizer.Realize()
		sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self.SetSizer(sizer)
		self.DoLayout()
		sizer.Fit(self)
	def DoLayout(self):
		pass

class ITaskBarIcon(wx.TaskBarIcon):
	def __init__(self,frame):
		super(ITaskBarIcon,self).__init__()
		self._frame=frame
		self.RegisterIcon()
		self.RegisterEvt()
		self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK,self.OnTaskBarActivate)
	def CreatePopupMenu(self):
		menu=wx.Menu()
		self.RegisterMenu(menu)
		return menu
	def MakeIcon(self,image):
		if 'wxMSW' in wx.PlatformInfo:
			image=image.Scale(16,16)
		elif 'wxGTK' in wx.PlatformInfo:
			image=image.Scale(22,22)
		icon=wx.IconFromBitmap(image.ConvertToBitmap())
		return icon
	def OnTaskBarActivate(self,event):
		if self._frame.IsIconized():
			self._frame.Iconize(False)
		if not self._frame.IsShown():
			self._frame.Show(True)
		self._frame.Raise()
	def RegisterIcon(self):
		pass
	def RegisterEvt(self):
		pass
	def RegisterMenu(self,menu):
		pass
