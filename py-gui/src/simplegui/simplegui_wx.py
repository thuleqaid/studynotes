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

class Widget(object):
    def __init__(self):
        self._widget=None
    def getWidget(self):
        return self._widget

class Layout(object):
    def __init__(self):
        self._layout=None
    def getLayout(self):
        return self._layout

class IWindow(Widget):
    def __init__(self):
        super(IWindow,self).__init__()
        self._closeCheck=(IWindow._defaultCloseCheck,self,)
        self._closeAction=(IWindow._defaultCloseAction,self,)
    def setTitle(self,title):
        pass
    def getTitle(self):
        pass
    def setSize(self,width,height):
        pass
    def getSize(self):
        pass
    def setCbCloseCheck(self,checkfunc):
        self._closeCheck=tuple(checkfunc)
    def setCbCloseAction(self,actionfunc):
        self._closeAction=tuple(actionfunc)
    def setLayout(self,layout):
        if isinstance(layout,Layout):
            self._widget.SetSizer(layout.getLayout())
        else:
            self._widget.SetSizer(layout)
    def show(self):
        pass
    def _doCloseCheck(self):
        if self._closeCheck:
            if len(self._closeCheck)>1:
                return self._closeCheck[0](*self._closeCheck[1:])
            else:
                return self._closeCheck[0]()
        else:
            return True
    def _doCloseAction(self):
        if self._closeAction:
            if len(self._closeAction)>1:
                self._closeAction[0](*self._closeAction[1:])
            else:
                self._closeAction[0]()
    def _defaultCloseCheck(self):
        return True
    def _defaultCloseAction(self):
        pass

class SimpleWindow(IWindow):
    class InnerSimpleWindow(_wx.Frame):
        def __init__(self,outter):
            self._outter=outter
            super(SimpleWindow.InnerSimpleWindow,self).__init__(None,_wx.ID_ANY,"")
            self.Bind(_wx.EVT_CLOSE,self.onCloseEvent)
        def onCloseEvent(self, event):
            if event.CanVeto():
                if self._outter._doCloseCheck():
                    self._outter._doCloseAction()
                    self.Destroy()
                else:
                    event.Veto()
            else:
                self.Destroy()
    def __init__(self):
        super(SimpleWindow,self).__init__()
        self._widget=SimpleWindow.InnerSimpleWindow(self)
    def setTitle(self,title):
        self._widget.SetTitle(title)
    def getTitle(self):
        return self._widget.GetTitle()
    def setSize(self,width,height):
        self._widget.SetSize((width,height,))
    def getSize(self):
        return self._widget.GetSize()
    def show(self):
        self._widget.Show()

class BoxLayout(Layout):
    HORIZONTAL=1
    VERTICAL=2
    def __init__(self,orient=HORIZONTAL):
        if orient==BoxLayout.VERTICAL:
            self._layout=_wx.BoxSizer(_wx.VERTICAL)
        else:
            self._layout=_wx.BoxSizer(_wx.HORIZONTAL)
    def add(self,widget):
        if isinstance(widget,Widget):
            self._layout.Add(widget.getWidget())
        else:
            self._layout.Add(widget)

class Button(Widget):
    class InnerButton(_wx.Button):
        def __init__(self,outter,parent,label):
            self._outter=outter
            if isinstance(parent,IWindow):
                super(Button.InnerButton,self).__init__(parent.getWidget(),_wx.ID_ANY,label)
            else:
                super(Button.InnerButton,self).__init__(parent,_wx.ID_ANY,label)
    def __init__(self,parent,label=""):
        super(Button,self).__init__()
        self._widget=Button.InnerButton(self,parent,label)
