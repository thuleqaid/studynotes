# -*- coding:utf-8 -*-
import base

class FunctionC(base.BaseFunction):
    def __init__(self):
        super(FunctionC,self).__init__()
    def toString(self):
        pcnt=len(self._params)-1
        params=[]
        for i in range(pcnt):
            if self._params[i+1]['type']==self._params[i+1]['name']:
                params.append('%s'%(self._params[i+1]['type'],))
            else:
                params.append('%s %s'%(self._params[i+1]['type'],self._params[i+1]['name']))
        outstr='%s %s(%s)'%(self._params[0]['type'],self._params[0]['name'],','.join(params))
        return outstr

class VariableC(base.BaseVariable):
    def __init__(self,vtype,vname,kv):
        super(VariableC,self).__init__(vtype,vname,kv)

class MatrixC(base.BaseMatrix):
    def __init__(self,ivars,ovars,irules,orules):
        super(MatrixC,self).__init__(ivars,ovars,irules,orules)

class ManageC(base.BaseManage):
    def __init__(self):
        super(ManageC,self).__init__()
        self._functions=[]
        self._exvars=[]
        self._autovars=[]
        self._matrix=None
        self._tagtab='\t'
        self._tagextern='extern'
        self._tagtypecast='(char*)'
        self._flagif=True
    def addFunction(self,data):
        func=FunctionC()
        for param in data:
            ptype=param['type']
            pname=param['name']
            kv={}
            for k,v in param.items():
                if k not in ('type','name'):
                    kv[k]=v
            func.addParam(ptype,pname,kv)
        self._functions.append(func)
    def addVariable(self,data):
        vtype=data['type']
        vname=data['name']
        kv={}
        for k,v in data.items():
            if k not in ('type','name'):
                kv[k]=v
        variable=VariableC(vtype,vname,kv)
        if 'value' in kv:
            self._autovars.append(variable)
        else:
            self._exvars.append(variable)
    def setMatrix(self,ivars,ovars,irules,orules):
        self._matrix=MatrixC(ivars,ovars,irules,orules)
    def outputFile(self,filename,encode='utf-8'):
        pass

class ManageC0(ManageC):
    def __init__(self):
        super(ManageC0,self).__init__()
    def outputFile(self,filename,encode='utf-8'):
        with open(filename,'wb') as fh:
            data=self.outputExFunc()
            fh.write(data.decode('utf-8').encode(encode))
            data=self.outputExVar()
            fh.write(data.decode('utf-8').encode(encode))
            data=self.outputFunc()
            fh.write(data.decode('utf-8').encode(encode))
    def outputExFunc(self):
        outstr=''
        for i in range(len(self._functions)-1):
            outstr+='%s %s;\n'%(self._tagextern,self._functions[i+1].toString())
        return outstr
    def outputExVar(self):
        outstr=''
        for v in self._exvars:
            outstr+='%s %s %s;\n'%(self._tagextern,v.type,v.name)
        return outstr
    def outputFunc(self):
        vdecl,vinit=self._outputAutoVar()
        rdecl,rret=self._outputRet()
        outstr='%s\n{\n'%(self._functions[0].toString(),)
        outstr+=vdecl
        outstr+=rdecl
        outstr+=vinit
        outstr+=self._outputMatrix()
        outstr+=rret
        outstr+='}\n'
        return outstr
    def _outputAutoVar(self):
        vdecl=''
        vinit=''
        for v in self._autovars:
            vdecl+='%s%s %s;\n'%(self._tagtab,v.type,v.name)
            method=v.getData('method')
            if method=='memset':
                vinit+='%s%s(%s&%s,%s,%s);\n'%(self._tagtab,method,self._tagtypecast,v.name,v.getData('value'),v.getData('size'))
            elif method=='memcpy':
                vinit+='%s%s(%s&%s,%s%s,%s);\n'%(self._tagtab,method,self._tagtypecast,v.name,self._tagtypecast,v.getData('value'),v.getData('size'))
            else:
                vinit+='%s%s = %s;\n'%(self._tagtab,v.name,v.getData('value'))
        return vdecl,vinit
    def _outputRet(self):
        rdecl=''
        rret=''
        ilist=self._matrix.getIVars()
        olist=self._matrix.getOVars()
        if '__RET__' in olist:
            for retvar in ('ret','rc','retcode','funcret'):
                if (retvar not in olist) and (retvar not in ilist):
                    break
            else:
                self._log.error('Cannot choose variable name for function''s return value')
            self._retvar=retvar
            rdecl='%s%s %s;\n'%(self._tagtab,self._functions[0].type,retvar)
            rret='%sreturn %s;\n'%(self._tagtab,retvar)
        return rdecl,rret
    def _outputMatrix(self):
        outstr=''
        ilist=self._matrix.getIVars()
        olist=self._matrix.getOVars()
        iolist=ilist+olist
        icnt=len(ilist)
        pairs=self._matrix.getPairs()
        cstack=[]
        cstep=1
        for ridx,rule in enumerate(self._matrix.iterRules()):
            self._log.debug('Rule:%s'%(repr(rule),))
            self._log.debug('Stack:%s'%(repr(cstack),))
            clen=len(cstack)
            if clen>0:
                self._flagif=False
                iidx=0
                while iidx<clen and rule[iidx]['value']==cstack[iidx]:
                    iidx+=1
                for i in range(clen-iidx):
                    cond=cstack.pop(-1)
                    if cond!='__NOTCARE__':
                        cstep-=1
                        outstr+=self._tagtab * cstep + '}\n'
                oidx=icnt
                if iidx>0:
                    for pidx,pair in enumerate(pairs):
                        if iidx>pair[0]:
                            oidx=pair[1]+1
                        else:
                            break
            else:
                self._flagif=True
                iidx=0
                oidx=icnt
            for pair in pairs:
                if iidx>pair[0]:
                    continue
                src,conds,step=self._outputInput(iolist,rule,cstep,iidx,pair[0]-1)
                cstack.extend(conds)
                cstep+=step
                outstr+=src
                outstr+=self._outputOutput(iolist,rule,cstep,oidx,pair[1]-1)
                iidx=pair[0]
                oidx=pair[1]
                if rule[iidx]['value']=='__NOTCARE__':
                    outstr+=self._outputOutput(iolist,rule,cstep,oidx,oidx)
                    src,conds,step=self._outputInput(iolist,rule,cstep,iidx,iidx)
                    cstack.extend(conds)
                    cstep+=step
                    outstr+=src
                else:
                    src,conds,step=self._outputInput(iolist,rule,cstep,iidx,iidx)
                    cstack.extend(conds)
                    cstep+=step
                    outstr+=src
                iidx+=1
                oidx+=1
            if iidx<icnt:
                src,conds,step=self._outputInput(iolist,rule,cstep,iidx,icnt-1)
                cstack.extend(conds)
                cstep+=step
                outstr+=src
            outstr+=self._outputOutput(iolist,rule,cstep,oidx,len(iolist)-1)
        while len(cstack)>0:
            cond=cstack.pop(-1)
            if cond!='__NOTCARE__':
                cstep-=1
                outstr+=self._tagtab * cstep + '}\n'
        return outstr
    def _outputInput(self,varlist,rule,sstep,startidx,stopidx):
        self._log.debug('Input [%d]->[%d]'%(startidx,stopidx))
        outstr=''
        cond=[]
        step=0
        if startidx>stopidx:
            return outstr,tuple(cond),step
        if stopidx<0:
            return outstr,tuple(cond),step
        for i in range(startidx,stopidx+1):
            prefix=self._tagtab * (sstep+step)
            value=rule[i]['value']
            cond.append(value)
            step+=1
            if value=='__NOTCARE__':
                step-=1
            elif value=='__ELSE__':
                outstr+='%selse\n%s{\n'%(prefix,prefix)
            else:
                if self._flagif:
                    outstr+='%sif (%s == %s)\n%s{\n'%(prefix,value,varlist[i],prefix)
                else:
                    outstr+='%selse if (%s == %s)\n%s{\n'%(prefix,value,varlist[i],prefix)
            self._flagif=True
        return outstr,tuple(cond),step
    def _outputOutput(self,varlist,rule,sstep,startidx,stopidx):
        self._log.debug('Output [%d]->[%d]'%(startidx,stopidx))
        outstr=''
        if startidx>stopidx:
            return outstr
        if stopidx<0:
            return outstr
        prefix=self._tagtab * sstep
        for i in range(startidx,stopidx+1):
            value=rule[i]['value']
            if value=='__NOACT__':
                pass
            elif value=='__NOCALL__':
                pass
            elif value=='__CALL__':
                outstr+='%s%s;\n'%(prefix,varlist[i],)
            else:
                if varlist[i]=='__RET__':
                    outstr+='%s%s = %s;\n'%(prefix,self._retvar,value)
                else:
                    outstr+='%s%s = %s;\n'%(prefix,varlist[i],value)
        return outstr

class ManageC1(ManageC0):
    def __init__(self):
        super(ManageC1,self).__init__()
    def _optimizeRules(self,level=0):
        rules=self._matrix.ruleValues()
        pairs=self._matrix.getPairs()
        ilist=self._matrix.getIVars()
        icnt=len(ilist)
        iocnt=len(rules[0])
        outlist=[]
        for rule in rules:
            outlist.append([])
            iidx,oidx=0,icnt
            for pair in pairs:
                if rule[pair[0]]=='__NOTCARE__':
                    for i in range(iidx,pair[0]):
                        if rule[i]!='__NOTCARE__':
                            outlist[-1].append(('i',i))
                    for i in range(oidx,pair[1]+1):
                        outlist[-1].append(('o',i))
                    iidx=pair[0]+1
                    oidx=pair[1]+1
                else:
                    for i in range(iidx,pair[0]):
                        if rule[i]!='__NOTCARE__':
                            outlist[-1].append(('i',i))
                    for i in range(oidx,pair[1]):
                        outlist[-1].append(('o',i))
                    iidx=pair[0]
                    oidx=pair[1]+1
            for i in range(iidx,icnt):
                if rule[i]!='__NOTCARE__':
                    outlist[-1].append(('i',i))
            for i in range(oidx,iocnt):
                outlist[-1].append(('o',i))
            plevel=0
            for i in range(icnt):
                if rule[i]!='__NOTCARE__':
                    plevel+=1
                    outlist[-1].append(('c',plevel))
        for ii in range(len(outlist)-1):
            i=len(outlist)-i-2
            rule1=outlist[i]
            rule2=outlist[i+1]
            level=0
            for j in range(min(len(rule1),len(rule2))):
                if rule1[j]==rule2[j] and rules[i][rule1[j][1]]==rules[i+1][rule1[j][1]]:
                    if rule1[j][0]=='i':
                        level+=1
                else:
                    break
            for k in range(j):
                outlist[i+1].pop(0)
            for k in range(level):
                outlist[i].pop(-1)
        if level>=1:
            pass
        if level>=2:
            pass
        return tuple(outlist)

    def _outputMatrix(self):
        outlist=self._optimizeRules()
        outstr=''
        ilist=self._matrix.getIVars()
        olist=self._matrix.getOVars()
        iolist=ilist+olist
        cstep=1
        self._flagif=True
        for ridx,rule in enumerate(self._matrix.iterRules()):
            self._log.debug('Rule:%s'%(repr(rule),))
            for outformat in outlist[ridx]:
                if outformat[0]=='i':
                    src,conds,step=self._outputInput(iolist,rule,cstep,outformat[1],outformat[1])
                    outstr+=src
                    cstep+=1
                elif outformat[0]=='o':
                    outstr+=self._outputOutput(iolist,rule,cstep,outformat[1],outformat[1])
                elif outformat[0]=='c':
                    cstep-=1
                    outstr+=self._tagtab * cstep + '}\n'
            self._flagif=False
        return outstr

class WriteMacroC(object):
    def __init__(self,matrix,srcfile,rstfile):
        super(WriteMacroC,self).__init__(matrix,srcfile,rstfile)
    def genSrcFile(self):
        pass

class LoadMacroC(object):
    def __init__(self,rstfile):
        super(LoadMacroC,self).__init__(rstfile)

class TestC(object):
    def __init__(self,matrix,macro,srcfile,rstfile):
        super(TestC,self).__init__(matrix,macro,srcfile,rstfile)
    def genSrcFile(self):
        # ToDo:output file header
        # ToDo:output test function's header
        # ToDo:output test cases
        for idxlist,comb in self.genCombination():
            rule=self.checkRule(idxlist,comb)
        # ToDo:output test result
        # ToDo:output dummy function
        pass
    def genCriterion(self):
        return ((0,1),(0,1),(0,1))
    def _checkRule(self,idx,value,ruleidxlist):
        return tuple(ruleidxlist)
