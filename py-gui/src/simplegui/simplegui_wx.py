# -*- coding: utf-8 -*-
import wx as _wx
import simplegui_utils_qt as _utils

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

class BoxLayout(Layout):
    HORIZONTAL=1
    VERTICAL=2
    def __init__(self,orient=HORIZONTAL):
        super(BoxLayout,self).__init__()
        if orient==BoxLayout.VERTICAL:
            self._layout=_wx.BoxSizer(_wx.VERTICAL)
        else:
            self._layout=_wx.BoxSizer(_wx.HORIZONTAL)
    def add(self,widget):
        if isinstance(widget,Widget):
            self._layout.Add(widget.getWidget())
        elif isinstance(widget,Layout):
            self._layout.Add(widget.getLayout())
        else:
            self._layout.Add(widget)

class GridLayout(Layout):
    def __init__(self,rows,cols):
        super(GridLayout,self).__init__()
        self._layout=_wx.GridBagSizer()
    def add(self,widget,row,col,rowspan=1,colspan=1):
        if isinstance(widget,Widget):
            self._layout.Add(widget.getWidget(),(row,col),(rowspan,colspan))
        elif isinstance(widget,Layout):
            self._layout.Add(widget.getLayout(),(row,col),(rowspan,colspan))
        else:
            self._layout.Add(widget,(row,col),(rowspan,colspan))

class IWindow(Widget):
    def __init__(self):
        super(IWindow,self).__init__()
        self._closeCheck=None
        self._closeAction=None
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

class SimpleWindow(IWindow):
    class InnerSimpleWindow(_wx.Frame):
        def __init__(self,outter):
            self._outter=outter
            super(SimpleWindow.InnerSimpleWindow,self).__init__(None,_wx.ID_ANY,"")
            self.Bind(_wx.EVT_CLOSE,self.onCloseEvent)
        def onCloseEvent(self, event):
            if event.CanVeto():
                if _utils.runFunc(True,self._outter._closeCheck):
                    _utils.runFunc(None,self._outter._closeAction)
                    self.Destroy()
                else:
                    event.Veto()
            else:
                self.Destroy()
    def __init__(self):
        super(SimpleWindow,self).__init__()
        self._widget=SimpleWindow.InnerSimpleWindow(self)
    def setTitle(self,title):
        self._widget.SetTitle(_utils.utf8ToStr(title))
    def getTitle(self):
        return _utils.strToUtf8(self._widget.GetTitle())
    def setSize(self,width,height):
        bestsize=self._widget.GetBestSize()
        if width<=0:
            width=bestsize.GetWidth()
        if height<=0:
            height=bestsize.GetHeight()
        self._widget.SetSize((width,height,))
    def getSize(self):
        return self._widget.GetSize()
    def show(self):
        self._widget.Show()

class Button(Widget):
    class InnerButton(_wx.Button):
        def __init__(self,outter,parent,label):
            self._outter=outter
            if isinstance(parent,IWindow):
                super(Button.InnerButton,self).__init__(parent.getWidget(),_wx.ID_ANY,label)
            else:
                super(Button.InnerButton,self).__init__(parent,_wx.ID_ANY,label)
            self.Bind(_wx.EVT_BUTTON,self.onClickEvent)
        def onClickEvent(self,event):
            _utils.runFunc(None,self._outter._click)
    def __init__(self,parent,label=""):
        super(Button,self).__init__()
        self._widget=Button.InnerButton(self,parent,label)
        self._click=None
    def setTitle(self,title):
        self._widget.SetLabel(_utils.utf8ToStr(title))
    def getTitle(self):
        return _utils.strToUtf8(self._widget.GetLabel())
    def setEnabled(self,flag):
        self._widget.Enable(flag)
    def getEnabled(self):
        return self._widget.IsEnabled()
    def setCbClick(self,clickfunc):
        self._click=tuple(clickfunc)
