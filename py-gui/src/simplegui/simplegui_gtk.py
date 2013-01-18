# -*- coding: utf-8 -*-
import pygtk as _pygtk
_pygtk.require('2.0')
import gtk as _gtk
import simplegui_utils_gtk as _utils

class BasicApp(object):
    def gengui(self):
        self.window=None
    def show(self):
        if self.window:
            self.window.show()
    def run(self):
        self.gengui()
        self.show()
        _gtk.main()

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
            self._layout=_gtk.VBox()
        else:
            self._layout=_gtk.HBox()
    def add(self,widget):
        if isinstance(widget,Widget):
            self._layout.pack_start(widget.getWidget())
        elif isinstance(widget,Layout):
            self._layout.pack_start(widget.getLayout())
        else:
            self._layout.pack_start(widget)

class GridLayout(Layout):
    def __init__(self,rows,cols):
        super(GridLayout,self).__init__()
        self._layout=_gtk.Table(rows,cols,True)
    def add(self,widget,row,col,rowspan=1,colspan=1):
        if isinstance(widget,Widget):
            self._layout.attach(widget.getWidget(),col,col+colspan,row,row+rowspan)
        elif isinstance(widget,Layout):
            self._layout.attach(widget.getLayout(),col,col+colspan,row,row+rowspan)
        else:
            self._layout.attach(widget,col,col+colspan,row,row+rowspan)

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
            self._widget.add(layout.getLayout())
        else:
            self._widget.add(layout)
    def show(self):
        pass

class SimpleWindow(IWindow):
    def __init__(self):
        super(SimpleWindow,self).__init__()
        self._widget=_gtk.Window(_gtk.WINDOW_TOPLEVEL)
        self._widget.connect("delete_event",self._delete_event)
        self._widget.connect("destroy",self._destroy)
    def _destroy(self,widget,data=None):
        # delete_event returns False -> destroy
        _gtk.main_quit()
    def _delete_event(self,widget,event,data=None):
        # click "close" on title bar -> delete_event
        if _utils.runFunc(True,self._closeCheck):
            _utils.runFunc(None,self._closeAction)
            return False
        else:
            return True
    def setTitle(self,title):
        self._widget.set_title(_utils.utf8ToStr(title))
    def getTitle(self):
        return _utils.strToUtf8(self._widget.get_title())
    def setSize(self,width,height):
        if width<=0:
            width=1
        if height<=0:
            height=1
        self._widget.resize(width,height)
    def getSize(self):
        return self._widget.get_size()
    def show(self):
        self._widget.show_all()

class Label(Widget):
    def __init__(self,parent,label=""):
        super(Label,self).__init__()
        self._widget=_gtk.Label(_utils.utf8ToStr(label))
    def setTitle(self,title):
        self._widget.set_text(_utils.utf8ToStr(title))
    def getTitle(self):
        return _utils.strToUtf8(self._widget.get_text())

class TextEntry(Widget):
    def __init__(self,parent,label=""):
        super(TextEntry,self).__init__()
        self._widget=_gtk.Entry()
        self.setTitle(label)
        self._widget.connect("changed",self.onTextEdited)
        self._widget.connect("activate",self.onReturnPressed)
        self._widget.connect("focus-in-event",self.onFocusInEvent)
        self._widget.connect("focus-out-event",self.onFocusOutEvent)
        self._focusIn=None
        self._focusOut=None
        self._textEdited=None
        self._returnPressed=None
    def setTitle(self,title):
        self._widget.set_text(_utils.utf8ToStr(title))
    def getTitle(self):
        return _utils.strToUtf8(self._widget.get_text())
    def onFocusInEvent(self,event):
        _utils.runFunc(None,self._focusIn)
    def onFocusOutEvent(self,event):
        _utils.runFunc(None,self._focusOut)
    def onTextEdited(self,event):
        _utils.runFunc(None,self._textEdited)
    def onReturnPressed(self,event):
        _utils.runFunc(None,self._returnPressed)
    def setEnabled(self,flag):
        self._widget.set_editable(flag)
    def getEnabled(self):
        return self._widget.get_editable()
    def setCbFocusIn(self,func):
        self._focusIn=tuple(func)
    def setCbFocusOut(self,func):
        self._focusOut=tuple(func)
    def setCbTextEdited(self,func):
        self._textEdited=tuple(func)
    def setCbReturnPressed(self,func):
        self._returnPressed=tuple(func)

class Button(Widget):
    def __init__(self,parent,label=""):
        super(Button,self).__init__()
        self._widget=_gtk.Button(_utils.utf8ToStr(label))
        self._widget.connect("clicked",self.onClickEvent)
        self._click=None
    def onClickEvent(self,widget,data=None):
        _utils.runFunc(None,self._click)
    def setTitle(self,title):
        self._widget.set_label(_utils.utf8ToStr(title))
    def getTitle(self):
        return _utils.strToUtf8(self._widget.get_label())
    def setEnabled(self,flag):
        self._widget.set_sensitive(flag)
    def getEnabled(self):
        return self._widget.get_sensitive()
    def setCbClick(self,clickfunc):
        self._click=tuple(clickfunc)
