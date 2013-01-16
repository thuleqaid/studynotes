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
    def setTitle(self,title):
        pass
    def getTitle(self):
        pass
    def setSize(self,width,height):
        pass
    def getSize(self):
        pass
    def doClose(self):
        pass
    def acceptClose(self):
        return True
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
        if self.acceptClose():
            self.doClose()
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
