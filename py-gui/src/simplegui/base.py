# -*- coding: utf-8 -*-
from utils import LogUtil
from uimanage import UiManage

def fgetwrapobj(self):
    if not hasattr(self,'_wrapobj'):
        self._wrapobj=None
    return self._wrapobj
def addwrapper(init):
    if init.__name__!='__init__':
        return init
    def __init__(cls,wrapper,*args,**kw):
        cls.wrapobj=property(fget=fgetwrapobj)
        cls._wrapobj=wrapper
        return init(cls,*args,**kw)
    return __init__

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
        super(self.__class__,self).__init__(*args,**kw)
        self.wrapobj=wrapper
'''
class BaseWidget(object):
    DEFAULT_INNER_CLASS=None
    def __init__(self,innercls=DEFAULT_INNER_CLASS,*args,**kw):
        self._log=LogUtil().logger('UI')
        self._innercls=innercls
        self._log.debug('InnerClass:%s'%(innercls.__name__,))
        self.createWidget(*args,**kw)
    def createWidget(self,*args,**kw):
        self._widget=None
    @property
    def widget(self):
        return self._widget
class BaseToplevelWidget(BaseWidget):
    def show(self):
        pass

'''
class InnerMessageBox(XXXUI.XXXWIDGET):
    @addwrapper
    def __init__(self,kw): pass
    def wrapshow(self):
        return MessageBox.RET_XXX
'''
class MessageBox(BaseToplevelWidget):
    ICON_NONE=0
    ICON_INFORMATION=1
    ICON_QUESTION=2
    ICON_WARNING=4
    ICON_CRITICAL=8
    BUTTON_OK=16
    BUTTON_OK_CANCEL=32
    BUTTON_YES_NO=64
    RET_YES=128
    RET_NO=256
    RET_OK=512
    RET_CANCEL=1024
    def __init__(self,*args,**kw):
        innercls=kw.pop('innercls',UiManage().uiClass('InnerMessageBox'))
        super(self.__class__,self).__init__(innercls,*args,**kw)
    def createWidget(self,*args,**kw):
        self._log.debug(str(kw))
        defaultdict={'parent':None,
                     'title':self.__class__.__name__,
                     'text':'',
                     'icon':self.__class__.ICON_NONE,
                     'button':self.__class__.BUTTON_OK}
        for k in defaultdict.keys():
            if k not in kw:
                kw[k]=defaultdict[k]
        self._log.debug(str(kw))
        self._widget=self._innercls(self,kw)
    def show(self):
        ret=self._widget.wrapshow()
        self._log.debug('Ret:%d'%(ret,))
        return ret
