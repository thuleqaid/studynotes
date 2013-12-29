# -*- coding: utf-8 -*-
import PyQt4.QtGui as _QtGui
import PyQt4.QtCore as _QtCore
import simplegui_utils_qt as _utils
import base

class BasicApp(base.BaseApp):
    def run(self):
        app=_QtGui.QApplication([])
        self.show()
        app.exec_()

class InnerMessageBox(_QtGui.QMessageBox):
    #@base.addwrapper
    #def __new__(self): pass
    def __init__(self,wrapper,*args,**kw):
        super(self.__class__,self).__init__(*args,**kw)
        self.wrapobj=wrapper
class MessageBox(base.BaseToplevelWidget):
    DEFAULT_INNER_CLASS=InnerMessageBox
    ICON_NONE=_QtGui.QMessageBox.NoIcon
    ICON_INFORMATION=_QtGui.QMessageBox.Information
    ICON_QUESTION=_QtGui.QMessageBox.Question
    ICON_WARNING=_QtGui.QMessageBox.Warning
    ICON_CRITICAL=_QtGui.QMessageBox.Critical
    BUTTON_OK=_QtGui.QMessageBox.Ok
    BUTTON_OK_CANCEL=_QtGui.QMessageBox.Ok|_QtGui.QMessageBox.Cancel
    BUTTON_YES_NO=_QtGui.QMessageBox.Yes|_QtGui.QMessageBox.No
    #RET_YES=_QtGui.QMessageBox.NoIconwx.ID_YES
    #RET_NO=_QtGui.QMessageBox.NoIconwx.ID_NO
    #RET_OK=_QtGui.QMessageBox.NoIconwx.ID_OK
    #RET_CANCEL=_QtGui.QMessageBox.NoIconwx.ID_CANCEL
    def __init__(self,innercls=DEFAULT_INNER_CLASS,*args,**kw):
        super(self.__class__,self).__init__(innercls,*args,**kw)
    def createWidget(self,*args,**kw):
        self._log.debug(str(kw))
        defaultdict={'parent':None,
                     'title':self.__class__.__name__,
                     'text':'',
                     'icon':self.__class__.ICON_NONE,
                     'button':self.__class__.BUTTON_OK}
        for k in defaultdict.keys():
            defaultdict[k]=kw.get(k,defaultdict[k])
        self._log.debug(str(defaultdict))
        self._widget=self._innercls(self,
                                    defaultdict['icon'],
                                    defaultdict['title'],
                                    defaultdict['text'],
                                    buttons=defaultdict['button'],
                                    parent=defaultdict['parent'])
    def show(self):
        ret=self._widget.exec_()
        #ret=self._widget.show()
        #self._log.debug('Ret:%d'%(ret,))
        return ret

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
            self._widget.setLayout(layout.getLayout())
        elif isinstance(layout,_QtGui.QLayout):
            self._widget.setLayout(layout)
    def show(self):
        pass

class SimpleWindow(IWindow):
    class InnerSimpleWindow(_QtGui.QDialog):
        def __init__(self,outter):
            self._outter=outter
            super(SimpleWindow.InnerSimpleWindow,self).__init__(None)
        def closeEvent(self, event):
            if _utils.runFunc(True,self._outter._closeCheck):
                _utils.runFunc(None,self._outter._closeAction)
                event.accept()
            else:
                event.ignore()
    def __init__(self):
        super(SimpleWindow,self).__init__()
        self._widget=SimpleWindow.InnerSimpleWindow(self)
    def setTitle(self,title):
        self._widget.setWindowTitle(_utils.utf8ToStr(title))
    def getTitle(self):
        return _utils.strToUtf8(self._widget.windowTitle())
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

class Label(Widget):
    class InnerLabel(_QtGui.QLabel):
        def __init__(self,outter,parent,label):
            self._outter=outter
            if isinstance(parent,IWindow):
                super(Label.InnerLabel,self).__init__(label,parent.widget)
            else:
                super(Label.InnerLabel,self).__init__(label,parent)
    def __init__(self,parent,label=""):
        super(Label,self).__init__()
        self._widget=Label.InnerLabel(self,parent,_utils.utf8ToStr(label))
    def setTitle(self,title):
        self._widget.setText(_utils.utf8ToStr(title))
    def getTitle(self):
        return _utils.strToUtf8(self._widget.text())

class TextEntry(Widget):
    class InnerTextEntry(_QtGui.QLineEdit):
        def __init__(self,outter,parent,label):
            self._outter=outter
            if isinstance(parent,IWindow):
                super(TextEntry.InnerTextEntry,self).__init__(label,parent.widget)
            else:
                super(TextEntry.InnerTextEntry,self).__init__(label,parent)
            self.connect(self,_QtCore.SIGNAL("textEdited(const QString&)"),self.textEdited)
            self.connect(self,_QtCore.SIGNAL("returnPressed()"),self.returnPressed)
        def focusInEvent(self,event):
            _utils.runFunc(None,self._outter._focusIn)
        def focusOutEvent(self,event):
            _utils.runFunc(None,self._outter._focusOut)
        def textEdited(self,text):
            _utils.runFunc(None,self._outter._textEdited)
        def returnPressed(self):
            _utils.runFunc(None,self._outter._returnPressed)
    def __init__(self,parent,label=""):
        super(TextEntry,self).__init__()
        self._widget=TextEntry.InnerTextEntry(self,parent,_utils.utf8ToStr(label))
        self._focusIn=None
        self._focusOut=None
        self._textEdited=None
        self._returnPressed=None
    def setTitle(self,title):
        self._widget.setText(_utils.utf8ToStr(title))
    def getTitle(self):
        return _utils.strToUtf8(self._widget.text())
    def setEnabled(self,flag):
        self._widget.setReadOnly(flag)
    def getEnabled(self):
        return self._widget.isReadOnly()
    def setCbFocusIn(self,func):
        self._focusIn=tuple(func)
    def setCbFocusOut(self,func):
        self._focusOut=tuple(func)
    def setCbTextEdited(self,func):
        self._textEdited=tuple(func)
    def setCbReturnPressed(self,func):
        self._returnPressed=tuple(func)

class Button(Widget):
    class InnerButton(_QtGui.QPushButton):
        def __init__(self,outter,parent,label):
            self._outter=outter
            if isinstance(parent,IWindow):
                super(Button.InnerButton,self).__init__(label,parent.widget)
            else:
                super(Button.InnerButton,self).__init__(label,parent)
        def mousePressEvent(self,event):
            _utils.runFunc(None,self._outter._click)
    def __init__(self,parent,label=""):
        super(Button,self).__init__()
        self._widget=Button.InnerButton(self,parent,_utils.utf8ToStr(label))
        self._click=None
    def setTitle(self,title):
        self._widget.setText(_utils.utf8ToStr(title))
    def getTitle(self):
        return _utils.strToUtf8(self._widget.text())
    def setEnabled(self,flag):
        self._widget.setEnabled(flag)
    def getEnabled(self):
        return self._widget.isEnabled()
    def setCbClick(self,clickfunc):
        self._click=tuple(clickfunc)
