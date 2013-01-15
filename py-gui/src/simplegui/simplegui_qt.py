import PyQt4.QtGui as _QtGui

class BasicApp(object):
    def gengui(self):
        self.window=None
    def show(self):
        if self.window:
            self.window.show()
    def run(self):
        app=_QtGui.QApplication([])
        self.gengui()
        self.show()
        app.exec_()

class SimpleWindow(object):
    class InnerSimpleWindow(_QtGui.QDialog):
        def __init__(self,outter):
            self._outter=outter
            super(SimpleWindow.InnerSimpleWindow,self).__init__(None)
            self._outter.setWidgets(self)
        def closeEvent(self, event):
            if self._outter.acceptClose():
                self._outter.doClose()
                event.accept()
            else:
                event.ignore()
    def __init__(self):
        self._window=SimpleWindow.InnerSimpleWindow(self)
    def setTitle(self,title):
        self._window.setWindowTitle(title)
    def getTitle(self):
        return self._window.windowTitle()
    def setSize(self,width,height):
        self._window.resize(width,height)
    def getSize(self):
        size=self._window.size()
        return (size.width(),size.height())
    def doClose(self):
        pass
    def acceptClose(self):
        return True
    def setWidgets(self,container):
        pass
    def show(self):
        self._window.show()
