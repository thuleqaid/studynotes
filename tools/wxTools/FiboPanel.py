import wx
import IMix

def fibo(n):
	if n==0:
		return 0
	elif n==1:
		return 1
	else:
		return fibo(n-1)+fibo(n-2)

class FiboPanel(IMix.IProgPanel):
	def __init__(self,parent,id=wx.ID_ANY,pos=wx.DefaultPosition,size=wx.DefaultSize,style=wx.TAB_TRAVERSAL,name='FiboPanel'):
		super(FiboPanel,self).__init__(parent,id,pos,size,style,name)
	def DoLayout(self):
		self.input=wx.SpinCtrl(self,value='35',min=1)
		self.output=wx.TextCtrl(self)
		self.noblock=wx.Button(self,label='Non-Blocking')
		self.Bind(wx.EVT_BUTTON,self.OnButton,self.noblock)

		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		gridsz=wx.GridSizer(2,2,5,5)
		gridsz.Add(wx.StaticText(self,label='fib(n):'))
		gridsz.Add(self.input,0,wx.EXPAND)
		gridsz.Add(wx.StaticText(self,label='result:'))
		gridsz.Add(self.output,0,wx.EXPAND)
		hsizer.Add(self.noblock,0,wx.ALL,5)
		self._sizer.Add(gridsz,0,wx.EXPAND|wx.ALL,10)
		self._sizer.Add(hsizer,0,wx.ALIGN_CENTER_HORIZONTAL)
	def OnButton(self,event):
		input=self.input.GetValue()
		self.output.SetValue('')
		self.StartBusy()
		task=IMix.IWXThread((fibo,int(input),),(FiboPanel.SetResult,self,))
		task.start()
	def SetResult(self,n):
		self.output.SetValue(str(n))
		self.StopBusy()
