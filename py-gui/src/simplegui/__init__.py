from imp import find_module
from threading import Lock
from os.path import exists,isfile
from logging import getLogger
from logging.config import fileConfig

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

supported_ui={'QT4':('PyQt4',),
              'WX':('wx',),
              'GTK2':('pygtk','gtk')}

def uiList():
    return supported_ui.keys()

def isUiValid(uiname):
    if uiname in supported_ui:
        for pkg in supported_ui[uiname]:
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

