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
        elif isinstance(layout,_QtGui.QLayout):
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
        bestsize=self._widget.minimumSize()
        if width<=0:
            width=bestsize.width()
        if height<=0:
            height=bestsize.height()
        self._widget.resize(width,height)
    def getSize(self):
        size=self._widget.size()
        return (size.width(),size.height())
    def show(self):
        self._widget.show()

class BoxLayout(Layout):
    HORIZONTAL=1
    VERTICAL=2
    def __init__(self,orient=HORIZONTAL):
        super(BoxLayout,self).__init__()
        if orient==BoxLayout.VERTICAL:
            self._layout=_QtGui.QVBoxLayout()
        else:
            self._layout=_QtGui.QHBoxLayout()
    def add(self,widget):
        if isinstance(widget,Widget):
            self._layout.addWidget(widget.getWidget())
        elif isinstance(widget,Layout):
            self._layout.addLayout(widget.getLayout())
        elif isinstance(widget,_QtGui.QWidget):
            self._layout.addWidget(widget)
        elif isinstance(widget,_QtGui.QLayout):
            self._layout.addLayout(widget)

class GridLayout(Layout):
    def __init__(self,rows,cols):
        super(GridLayout,self).__init__()
        self._layout=_QtGui.QGridLayout()
    def add(self,widget,row,col,rowspan=1,colspan=1):
        if isinstance(widget,Widget):
            self._layout.addWidget(widget.getWidget(),row,col,rowspan,colspan)
        elif isinstance(widget,Layout):
            self._layout.addLayout(widget.getLayout(),row,col,rowspan,colspan)
        elif isinstance(widget,_QtGui.QWidget):
            self._layout.addWidget(widget,row,col,rowspan,colspan)
        elif isinstance(widget,_QtGui.QLayout):
            self._layout.addLayout(widget,row,col,rowspan,colspan)

class Button(Widget):
    class InnerButton(_QtGui.QPushButton):
        def __init__(self,outter,parent,label):
            self._outter=outter
            if isinstance(parent,IWindow):
                super(Button.InnerButton,self).__init__(label,parent.getWidget())
            else:
                super(Button.InnerButton,self).__init__(label,parent)
    def __init__(self,parent,label=""):
        super(Button,self).__init__()
        self._widget=Button.InnerButton(self,parent,label)
