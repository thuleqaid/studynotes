# -*- coding:utf-8 -*-
from logutil import LogUtil

class BaseFunction(object):
    def __init__(self):
        self._log=LogUtil().logger('Data')
    def addParam(self,ptype,pname,**kv):
        self._params.append({})
        self._params[-1]['type']=repr(ptype)
        self._params[-1]['name']=repr(pname)
        for k,v in kv.items():
            self._params[-1][k]=v

class BaseVariable(object):
    def __init__(self,vtype,vname,**kv):
        self._log=LogUtil().logger('Data')
        self._type=vtype
        self._name=vname
        self._data={}
        for k,v in kv.items():
            self._data[k]=v

class BaseMatrix(object):
    def __init__(self,ivars,ovars,irules,orules):
        self._log=LogUtil().logger('Data')
        self._checkdata(ivars,ovars,irules,orules)
    def __init__(self,ivars,ovars,rules):
        self._log=LogUtil().logger('Data')
        self._checkdata(ivars,ovars,rules)
    def _checkdata(self,ivars,ovars,irules,orules):
        if len(irules)!=len(orules):
            self._log.error('Rule Count for Input And Output Are Not Equal')
            return
        if len(irules)<1:
            self._log.error('No Rules')
            return
        if len(ivars)!=len(irules[0]) or len(ovars)!=len(orules[0]):
            self._log.error('The Number Of I/O Variables Is Wrong')
            return
        rules=[]
        for i in range(len(irules)):
            rules.append([])
            rules[-1].extend(irules[i])
            rules[-1].extend(orules[i])
        self._setdata(ivars,ovars,rules)
    def _checkdata(self,ivars,ovars,rules):
        if len(rules)<1:
            self._log.error('No Rules')
            return
        if len(ivars)+len(ovars)!=len(rules[0]):
            self._log.error('The Number Of I/O Variables Is Wrong')
            return
        self._setdata(ivars,ovars,rules)
    def _setdata(self,ivars,ovars,rules):
        def rulecmp(objx,objy):
            maxidx=len(ivars)
            def _itemcmp(objx,objy,idx):
                ret=cmp(objx[idx]['value'],objy[idx]['value'])
                if ret!=0:
                    if objx[idx]['value']=='__ELSE__' or objy[idx]['value']=='__NOTCARE__':
                        ret=1
                    elif objy[idx]['value']=='__ELSE__' or objx[idx]['value']=='__NOTCARE__':
                        ret=-1
                return ret
            def _rulecmp(objx,objy):
                i=0
                ret=0
                while i<maxidx and ret==0:
                    ret=_itemcmp(objx,objy,i)
                    i+=1
                return ret
            return _rulecmp(objx,objy)
        tmprules=list(rules)
        tmprules.sort(cmp=rulecmp)
        self._rules=list(tmprules)
        self._ivars=list(ivars)
        self._ovars=list(ovars)
        self._icnt=len(self._ivars)

if __name__ == '__main__':
    ivars=({'value':'a','comment':''},
           {'value':'b','comment':''},
           {'value':'c','comment':''},
          )
    ovars=({'value':'x','comment':''},
          )
    rules=(({'value':'1'},{'value':'2'},{'value':'1'},{'value':'1'}),
           ({'value':'2'},{'value':'3'},{'value':'1'},{'value':'1'}),
           ({'value':'2'},{'value':'3'},{'value':'2'},{'value':'1'}),
           ({'value':'__ELSE__'},{'value':'1'},{'value':'1'},{'value':'1'}),
           ({'value':'1'},{'value':'__NOTCARE__'},{'value':'1'},{'value':'1'}),
          )
    m=BaseMatrix(ivars,ovars,rules)
