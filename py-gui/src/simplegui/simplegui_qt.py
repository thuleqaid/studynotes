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
            self._widget.setLayout(layout.getLayout())
        else:
            self._widget.setLayout(layout)
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
    class InnerSimpleWindow(_QtGui.QDialog):
        def __init__(self,outter):
            self._outter=outter
            super(SimpleWindow.InnerSimpleWindow,self).__init__(None)
        def closeEvent(self, event):
            if self._outter._doCloseCheck():
                self._outter._doCloseAction()
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
