import pygtk as _pygtk
_pygtk.require('2.0')
import gtk as _gtk

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
            self._widget.add(layout.getLayout())
        else:
            self._widget.add(layout)
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
        if self._doCloseCheck():
            self._doCloseAction()
            return False
        else:
            return True
    def setTitle(self,title):
        self._widget.set_title(title)
    def getTitle(self):
        return self._widget.get_title()
    def setSize(self,width,height):
        self._widget.resize(width,height)
    def getSize(self):
        return self._widget.get_size()
    def show(self):
        self._widget.show()

class BoxLayout(Layout):
    HORIZONTAL=1
    VERTICAL=2
    def __init__(self,orient=HORIZONTAL):
        if orient==VERTICAL:
            self._layout=_gtk.VBox()
        else:
            self._layout=_gtk.HBox()
