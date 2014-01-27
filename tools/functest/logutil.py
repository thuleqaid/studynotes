from os.path import exists,isfile,join,dirname
from logging import getLogger
from logging.config import fileConfig
from threading import Lock

def singleton(cls, *args, **kw):
    instance={}
    inslocker=Lock()
    def _singleton():
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
    LOGDIR=dirname(__file__).replace('\\','/')
    CONFFILE=join(dirname(__file__),'logging.conf')
    def __init__(self):
        if exists(self.CONFFILE) and isfile(self.CONFFILE):
            fileConfig(self.CONFFILE,{'logdir':self.LOGDIR})
        else:
            pass
    def logger(self,logname):
        return getLogger(logname)
