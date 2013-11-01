import wx

import IGui
import IUtils

class IProgPanel(IGui.IPanel):
	def __init__(self,parent,id=wx.ID_ANY,pos=wx.DefaultPosition,size=wx.DefaultSize,style=wx.TAB_TRAVERSAL,name='IProgPanel'):
		super(IProgPanel,self).__init__(parent,id,pos,size,style,name)
	def InitSizer(self):
		self._sizer=wx.BoxSizer(wx.VERTICAL)
		self._timer=wx.Timer(self)
		self._prog=wx.Gauge(self,range=100)
		sizer=wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self._sizer,1,wx.EXPAND)
		sizer.Add(self._prog,0,wx.EXPAND)
		self.SetSizer(sizer)
		self.Bind(wx.EVT_TIMER,self.OnPulse,self._timer)
	def DoLayout(self):
		pass
	def OnPulse(self,event):
		self._prog.Pulse()
	def StartBusy(self):
		self._timer.Start(100)
		self.Enable(False)
	def StopBusy(self):
		self._timer.Stop()
		self._prog.SetValue(self._prog.GetRange())
		self._prog.SetValue(0)
		self.Enable(True)


class IWXThread(IUtils.IThread):
	def __init__(self,threadfunc,finalfunc):
		super(IWXThread,self).__init__(threadfunc,finalfunc)
	def RunFinalFunc(self,val):
		param=[]
		if self._finalfunc:
			param[:]=self._finalfunc[:]
			if val:
				param.append(val)
			wx.CallAfter(*param)
