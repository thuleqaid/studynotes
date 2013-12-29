from imp import find_module
from threading import Lock
from os.path import exists,isfile,split,dirname
from logging import getLogger
from logging.config import fileConfig

__PACKAGE_NAME__=split(dirname(__file__))[1]
__PACKAGE_VERSION__='0.0.1'

def singleton(cls, *args, **kw):
    instance={}
    inslocker=Lock()
    def _singleton(*args, **kw):
        if cls in instance:
            return instance[cls]
        inslocker.acquire()
        try:
            if cls in instance:
                return instance[cls]
            else:
                instance[cls]=cls(*args, **kw)
        finally:
            inslocker.release()
        return instance[cls]
    return _singleton

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
class LogUtil(object):
    CONFFILE='logging.conf'
    def __init__(self):
        if exists(self.CONFFILE) and isfile(self.CONFFILE):
            fileConfig(self.CONFFILE)
        else:
            pass
    def logger(self,logname):
        return getLogger(logname)

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
        return eval('gui.%s'%(classname,))
    def _loadUI(self):
        from sys import modules
        name='%s.%s'%(__PACKAGE_NAME__,supported_ui[self._ui][0])
        global gui
        __import__(name)
        gui=modules[name]
