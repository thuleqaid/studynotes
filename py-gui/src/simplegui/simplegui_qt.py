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
            self._widget.setLayout(layout.getLayout())
        else:
            self._widget.setLayout(layout)
    def show(self):
        pass

class SimpleWindow(IWindow):
    class InnerSimpleWindow(_QtGui.QDialog):
        def __init__(self,outter):
            self._outter=outter
            super(SimpleWindow.InnerSimpleWindow,self).__init__(None)
        def closeEvent(self, event):
            if self._outter.acceptClose():
                self._outter.doClose()
                event.accept()
            else:
                event.ignore()
    def __init__(self):
        super(SimpleWindow,self).__init__()
        self._widget=SimpleWindow.InnerSimpleWindow(self)
    def setTitle(self,title):
        self._widget.setWindowTitle(title)
    def getTitle(self):
        return self._widget.windowTitle()
    def setSize(self,width,height):
        self._widget.resize(width,height)
    def getSize(self):
        size=self._widget.size()
        return (size.width(),size.height())
    def show(self):
        self._widget.show()
