# -*- coding:utf-8 -*-
from lxml import etree
from logutil import LogUtil
from langc import *

class XmlReader(object):
    def __init__(self):
        self._log=LogUtil().logger('XmlReader')
    def loadXml(self,filename):
        self._log.info('Reading XML File:%s'%(filename,))
        self._initdata()
        tagstack=[]
        for action,elem in etree.iterparse(filename,events=('start','end')):
            if action=='start':
                tag=elem.tag
                tagstack.append(tag)
                self.starttag(':'.join(tagstack),elem)
            else:
                self.endtag(':'.join(tagstack),elem)
                tagstack.pop(-1)
    def getInfo(self,infoobj):
        if not isinstance(infoobj,ManageC):
            return False
        for func in self._funcs:
            infoobj.addFunction(func)
        for var in self._vars:
            infoobj.addVariable(var)
        infoobj.setMatrix(self._invars,
                     self._outvars,
                     self._incond,
                     self._outcond)
        return True

    def _initdata(self):
        self._funcs=[]
        self._funcs.append([])
        self._vars=[]
        self._invars=[]
        self._outvars=[]
        self._incond=[]
        self._outcond=[]

    def starttag(self,path,elem):
        if path.startswith('root:function:param'):
            self._log.debug(path)
            self._funcs[0].append(elem.attrib)
        elif path=='root:ex-function':
            self._log.debug(path)
            self._funcs.append([])
        elif path.startswith('root:ex-function:param'):
            self._log.debug(path)
            self._funcs[-1].append(elem.attrib)
        elif path.startswith('root:ex-var:var'):
            self._log.debug(path)
            self._vars.append(elem.attrib)
        elif path.startswith('root:auto-var:var'):
            self._log.debug(path)
            self._vars.append(elem.attrib)
        elif path.startswith('root:matrix:in-var:var'):
            self._log.debug(path)
            self._invars.append(elem.attrib)
        elif path.startswith('root:matrix:out-var:var'):
            self._log.debug(path)
            self._outvars.append(elem.attrib)
        elif path.startswith('root:matrix:rule'):
            if path.endswith('in-rule'):
                self._incond.append([])
            elif path.endswith('out-rule'):
                self._outcond.append([])
            if ':in-rule:value' in path:
                self._log.debug(path)
                self._incond[-1].append(elem.attrib)
            elif ':out-rule:value' in path:
                self._log.debug(path)
                self._outcond[-1].append(elem.attrib)
    def endtag(self,path,elem):
        if path=='root:function':
            self._log.debug(path)
        elif path=='root:ex-function':
            self._log.debug(path)
        elif path=='root:ex-var':
            self._log.debug(path)
        elif path=='root:auto-var':
            self._log.debug(path)
        elif path=='root:matrix:in-var':
            self._log.debug(path)
        elif path=='root:matrix:out-var':
            self._log.debug(path)
        elif path.startswith('root:matrix:rule'):
            if ':in-rule:value' in path:
                self._log.debug(path)
            elif ':out-rule:value' in path:
                self._log.debug(path)

if __name__ == '__main__':
    x=XmlReader()
    x.loadXml('../ignore/test_push_queue.xml')
    mc=ManageC1()
    x.getInfo(mc)
    mc.outputFile('../ignore/test.c')
