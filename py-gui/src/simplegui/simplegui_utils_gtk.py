# -*- coding: utf-8 -*-
def runFunc(defaultret,params):
    ret=defaultret
    if params:
        if len(params)>1:
            ret=params[0](*params[1:])
        else:
            ret=params[0]()
    return ret

def utf8ToStr(data):
    return data

def strToUtf8(data):
    return data
