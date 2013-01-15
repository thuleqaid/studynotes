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

class SimpleWindow(object):
    def __init__(self):
        self._window=_gtk.Window(_gtk.WINDOW_TOPLEVEL)
        self._window.connect("delete_event",self._delete_event)
        self._window.connect("destroy",self._destroy)
        self.setWidgets(self._window)
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
    def getWidgets(self):
        return self._window
    def setTitle(self,title):
        self._window.set_title(title)
    def getTitle(self):
        return self._window.get_title()
    def setSize(self,width,height):
        self._window.resize(width,height)
    def getSize(self):
        return self._window.get_size()
    def doClose(self):
        pass
    def acceptClose(self):
        return True
    def setWidgets(self,container):
        pass
    def show(self):
        self._window.show()
