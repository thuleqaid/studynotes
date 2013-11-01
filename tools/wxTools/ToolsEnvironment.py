import wx
import os
import IGui
import IUtils
import IMix
import FiboPanel
import VimPanel
import CallGraphPanel
import ToolsPanel
class ToolsEnvironmentApp(wx.App):
	def OnInit(self):
		self.frame=ToolsEnvironmentFrame(None,title='ToolsEnvironment Application')
		self.SetTopWindow(self.frame)
		self.frame.Show()
		return True

class ToolsEnvironmentFrame(IGui.IFrame):
	def __init__(self,parent,id=wx.ID_ANY,title='',
				pos=wx.DefaultPosition,size=(640,480),
				style=wx.DEFAULT_FRAME_STYLE,
				name='ToolsEnvironmentFrame'):
		super(ToolsEnvironmentFrame,self).__init__(parent,id,title,
									pos,size,style,name)
	def InitMainPanel(self):
		return ToolsEnvironmentNB(self)
	def InitTaskBarIcon(self):
		try:
			tbicon=MyTaskBarIcon(self)
		except:
			tbicon=None
		return tbicon
	def InitStatusBar(self):
		self.CreateStatusBar(6)
	def SetStatusBarInfo(self,text,index=0):
		count=self.GetStatusBar().GetFieldsCount()
		index=index%count
		self.SetStatusText(text,index)

class ToolsEnvironmentNB(IGui.INotebook):
	def __init__(self,parent,id=wx.ID_ANY,pos=wx.DefaultPosition,size=(21,21),style=wx.BK_DEFAULT,name='ToolsEnvironmentNB'):
		super(ToolsEnvironmentNB,self).__init__(parent,id,pos,size,style,name)
	def DoLayout(self):
		#self.AddPage(FiboPanel.FiboPanel(self),'Fibo')
		#self.AddPage(IGui.IPanel(self),'IPanel')
		#self.AddPage(IMix.IProgPanel(self),'IProgPanel')
		self.vimpanel=VimPanel.VimPanel(self,os.path.join(os.getcwdu(),u'Tools.ini'))
		self.AddPage(self.vimpanel,'VimPanel')
		self.cgpanel=CallGraphPanel.CallGraphPanel(self,os.path.join(os.getcwdu(),u'Tools.ini'))
		self.AddPage(self.cgpanel,'CallGraphPanel')
		#self.AddPage(ToolsPanel.ToolsPanel(self),'Tools')
		pass
	def OnPageChanged(self, event):
		old = event.GetOldSelection()
		new = event.GetSelection()
		if old >= 0:
			if isinstance(self.GetPage(old),VimPanel.VimPanel):
				item=self.vimpanel.GetSelectedItem()
				self.cgpanel.SetSrcpath(item)
		event.Skip()

class MyTaskBarIcon(IGui.ITaskBarIcon):
	def __init__(self,frame):
		self.TBMENU_RESTORE=wx.NewId()
		self.TBMENU_CLOSE=wx.NewId()
		super(MyTaskBarIcon,self).__init__(frame)
	def RegisterIcon(self):
		image=wx.Image('appicon.ico')
		self.SetIcon(self.MakeIcon(image),"Tools")
	def RegisterEvt(self):
		self.Bind(wx.EVT_MENU,self.OnTaskBarActivate,id=self.TBMENU_RESTORE)
		self.Bind(wx.EVT_MENU,self.OnTaskBarClose,id=self.TBMENU_CLOSE)
	def RegisterMenu(self,menu):
		menu.Append(self.TBMENU_RESTORE,'Restore')
		menu.Append(self.TBMENU_CLOSE,'Close')
	def OnTaskBarClose(self,event):
		wx.CallAfter(self._frame.Close)

if __name__=='__main__':
	app=ToolsEnvironmentApp(False)
	app.MainLoop()

