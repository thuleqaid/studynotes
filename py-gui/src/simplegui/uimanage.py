from imp import find_module
from utils import singleton, LogUtil
from os.path import split,dirname

__PACKAGE_NAME__=split(dirname(__file__))[1]

supported_ui={'QT4':('simplegui_qt','PyQt4',),
              'WX':('simplegui_wx','wx',),
              'GTK2':('simplegui_gtk','pygtk','gtk')}

def uiList():
    return supported_ui.keys()

def isUiValid(uiname):
    if uiname in supported_ui:
        for pkg in supported_ui[uiname][1:]:
            try:
                find_module(pkg)
            except ImportError:
                break
        else:
            return True
    return False

@singleton
class UiManage(object):
    def __new__(self,uiname=''):
        if isUiValid(uiname):
            obj=object.__new__(self)
            obj._ui=uiname
            return obj
        else:
            for ui in uiList():
                if isUiValid(ui):
                    obj=object.__new__(self)
                    obj._ui=ui
                    return obj
    def __init__(self,uiname=''):
        self._log=LogUtil().logger('UiManage')
        self._log.info('create UiManage(%s)'%(self._ui,))
        self._loadUI()
    def uiClass(self,classname):
        return eval('self._gui.%s'%(classname,))
    def _loadUI(self):
        from sys import modules
        name='%s.%s'%(__PACKAGE_NAME__,supported_ui[self._ui][0])
        __import__(name)
        self._gui=modules[name]
