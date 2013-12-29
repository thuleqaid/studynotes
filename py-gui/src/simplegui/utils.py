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
