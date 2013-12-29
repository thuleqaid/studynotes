# -*- coding: utf-8 -*-
import wx as _wx
import simplegui_utils_wx as _utils
import base

class BasicApp(base.BaseApp):
    class InnerApp(_wx.App):
        def __init__(self,outter):
            self._outter=outter
            _wx.App.__init__(self)
        def OnInit(self):
            self._outter.show()
            return True
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

class IWindow(base.BaseToplevelWidget):
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

class Label(Widget):
    class InnerLabel(_wx.StaticText):
        def __init__(self,outter,parent,label):
            self._outter=outter
            if isinstance(parent,IWindow):
                super(Label.InnerLabel,self).__init__(parent.widget,_wx.ID_ANY,label)
            else:
                super(Label.InnerLabel,self).__init__(parent,_wx.ID_ANY,label)
    def __init__(self,parent,label=""):
        super(Label,self).__init__()
        self._widget=Label.InnerLabel(self,parent,_utils.utf8ToStr(label))
    def setTitle(self,title):
        self._widget.SetLabel(_utils.utf8ToStr(title))
    def getTitle(self):
        return _utils.strToUtf8(self._widget.GetLabel())

class InnerTextEntry(_wx.TextCtrl):
    def __init__(self,outter,parent,label,style):
        self._outter=outter
        style=style | _wx.TE_PROCESS_ENTER
        if isinstance(parent,IWindow):
            super(InnerTextEntry,self).__init__(parent.widget,_wx.ID_ANY,label,style=style)
        else:
            super(InnerTextEntry,self).__init__(parent,_wx.ID_ANY,label,style=style)
        self.Bind(_wx.EVT_SET_FOCUS,self.focusInEvent)
        self.Bind(_wx.EVT_KILL_FOCUS,self.focusOutEvent)
        self.Bind(_wx.EVT_TEXT,self.textEdited)
        self.Bind(_wx.EVT_TEXT_ENTER,self.returnPressed)
    def focusInEvent(self,event):
        _utils.runFunc(None,self._outter._focusIn)
    def focusOutEvent(self,event):
        _utils.runFunc(None,self._outter._focusOut)
    def textEdited(self,event):
        _utils.runFunc(None,self._outter._textEdited)
    def returnPressed(self,event):
        _utils.runFunc(None,self._outter._returnPressed)

class TextEntry(Widget):
    def __init__(self,parent,label=""):
        super(TextEntry,self).__init__()
        self._widget=InnerTextEntry(self,parent,_utils.utf8ToStr(label),0)
        self._focusIn=None
        self._focusOut=None
        self._textEdited=None
        self._returnPressed=None
    def setTitle(self,title):
        self._widget.ChangeValue(_utils.utf8ToStr(title))
    def getTitle(self):
        return _utils.strToUtf8(self._widget.GetValue())
    def setEnabled(self,flag):
        self._widget.Enable(flag)
    def getEnabled(self):
        return self._widget.IsEnabled()
    def setCbFocusIn(self,func):
        self._focusIn=tuple(func)
    def setCbFocusOut(self,func):
        self._focusOut=tuple(func)
    def setCbTextEdited(self,func):
        self._textEdited=tuple(func)
    def setCbReturnPressed(self,func):
        self._returnPressed=tuple(func)

class Button(Widget):
    class InnerButton(_wx.Button):
        def __init__(self,outter,parent,label):
            self._outter=outter
            if isinstance(parent,IWindow):
                super(Button.InnerButton,self).__init__(parent.widget,_wx.ID_ANY,label)
            else:
                super(Button.InnerButton,self).__init__(parent,_wx.ID_ANY,label)
            self.Bind(_wx.EVT_BUTTON,self.onClickEvent)
        def onClickEvent(self,event):
            _utils.runFunc(None,self._outter._click)
    def __init__(self,parent,label=""):
        super(Button,self).__init__()
        self._widget=Button.InnerButton(self,parent,_utils.utf8ToStr(label))
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
