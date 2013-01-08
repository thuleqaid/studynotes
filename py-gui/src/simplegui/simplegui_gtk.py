import pygtk as _pygtk
_pygtk.require('2.0')
import gtk as _gtk

class BasicApp(object):
    def gengui(self):
        self.window=_gtk.Window(gtk.WINDOW_TOPLEVEL)
    def show(self):
        self.window.show()
    def run(self):
        self.gengui()
        self.show()
        _gtk.main()