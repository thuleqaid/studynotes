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
        self.window=None
    def show(self):
        if self.window:
            self.window.show()
    def run(self):
        app=self.InnerApp(self)
        app.MainLoop()

class SimpleWindow(object):
    class InnerSimpleWindow(_wx.Frame):
        def __init__(self,outter):
            self._outter=outter
            super(SimpleWindow.InnerSimpleWindow,self).__init__(None,_wx.ID_ANY,"")
            self._outter.setWidgets(self)
            self.Bind(_wx.EVT_CLOSE,self.onCloseEvent)
        def onCloseEvent(self, event):
            if event.CanVeto():
                if self._outter.acceptClose():
                    self._outter.doClose()
                    self.Destroy()
                else:
                    event.Veto()
            else:
                self.Destroy()
    def __init__(self):
        self._window=SimpleWindow.InnerSimpleWindow(self)
    def setTitle(self,title):
        self._window.SetTitle(title)
    def getTitle(self):
        return self._window.GetTitle()
    def setSize(self,width,height):
        self._window.SetSize((width,height,))
    def getSize(self):
        return self._window.GetSize()
    def doClose(self):
        pass
    def acceptClose(self):
        return True
    def setWidgets(self,container):
        pass
    def show(self):
        self._window.Show()
