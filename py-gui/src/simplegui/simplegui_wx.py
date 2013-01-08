import wx as _wx

class BasicApp(object):
    class InnerApp(_wx.App):
        def __init__(self,outter):
            self._outter=outter
            _wx.App.__init__(self)
        def OnInit(self):
            self._outter.gengui()
            self._outter.show()
            return True
    def gengui(self):
        self.window=_wx.Frame()
    def show(self):
        self.window.Show()
    def run(self):
        app=self.InnerApp(self)
        app.MainLoop()
