# -*- coding: utf-8 -*-
import PyQt4.QtCore as _QtCore
def runFunc(defaultret,params):
    ret=defaultret
    if params:
        if len(params)>1:
            ret=params[0](*params[1:])
        else:
            ret=params[0]()
    return ret

def utf8ToStr(data):
    return _QtCore.QString.fromUtf8(data)

def strToUtf8(data):
    return data.toUtf8().data()
