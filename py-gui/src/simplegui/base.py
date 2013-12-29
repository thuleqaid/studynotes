# -*- coding: utf-8 -*-

def fgetwrapobj(self):
    if not hasattr(self,'_wrapobj'):
        self._wrapobj=None
    return self._wrapobj
def fsetwrapobj(self,value):
    if self._wrapobj is None:
        if isinstance(value,BaseWidget):
            self._wrapobj=value
def addwrapper(new):
    print 'y'
    if new.__name__!='__new__':
        return new
    def __new__(cls,*args,**kw):
        cls.wrapobj=property(fget=fgetwrapobj,fset=fsetwrapobj)
        return super(cls.__class__,cls).__new__(cls,*args,**kw)
    return __new__

class BaseApp(object):
    def build(self):
        return None
    def show(self):
        mainwindow=self.build()
        if isinstance(mainwindow,BaseToplevelWidget):
            mainwindow.show()
    def run(self):
        pass

'''
class InnerWidget(XXXUI.XXXWIDGET):
    @addwrapper
    def __new__(self): pass
    def __init__(self,wrapper,*args,**kw):
        self.wrapobj=wrapper
'''
class BaseWidget(object):
    DEFAULT_INNER_CLASS=None
    def __init__(self,innercls=DEFAULT_INNER_CLASS,*args,**kw):
        self._innercls=innercls
        self.createWidget(*args,**kw)
    def createWidget(self,*args,**kw):
        self._widget=None
    @property
    def widget(self):
        return self._widget
class BaseToplevelWidget(BaseWidget):
    def show(self):
        pass
