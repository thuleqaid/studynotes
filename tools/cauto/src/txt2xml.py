# -*- coding:utf-8 -*-
import re
from lxml import etree
from logutil import LogUtil

class Txt2Xml(object):
    D_FIELDSEP='\t'
    D_CASTCHAR='(U1*)'
    D_FLAGSTR1=u'■関数宣言'.encode('utf-8')
    D_FLAGSTR21=u'■自動変数'.encode('utf-8')
    D_FLAGSTR22=u'■完了'.encode('utf-8')
    D_FLAGSTR31=u'■入出力表'.encode('utf-8')
    D_FLAGSTR32=u'■完了'.encode('utf-8')
    D_FLAGSTR33=u'入力'.encode('utf-8')
    D_FLAGSTR34=u'出力'.encode('utf-8')
    D_FLAGSTR41=u'■外部関数'.encode('utf-8')
    D_FLAGSTR42=u'■完了'.encode('utf-8')
    D_FLAGSTR51=u'■外部変数'.encode('utf-8')
    D_FLAGSTR52=u'■完了'.encode('utf-8')
    D_MARK1=u'戻り値'.encode('utf-8')
    D_MARK2=u'○'.encode('utf-8')
    D_MARK3=u'×'.encode('utf-8')
    D_MARK4=u'△'.encode('utf-8')
    D_MARK5=u'-'.encode('utf-8')
    D_MARK6=u'上記以外'.encode('utf-8')

    def __init__(self):
        self._log=LogUtil().logger('Txt2Xml')

    def loadTxt(self,filename,fileencode):
        self._log.info('File:%s Encode:%s'%(filename,fileencode))
        fh=open(filename,'rU')
        data=fh.read()
        fh.close()
        data8=data.decode(fileencode).encode('utf-8')

        self.initData()
        self.splitTxt(data8)
        self.parseTxt()

    def toXml(self,filename):
        root=etree.Element('root')

        func=etree.SubElement(root,'function')
        self._xmlFunc(func,self._funcvars[0])

        for i in range(len(self._funcvars)-1):
            func=etree.SubElement(root,'ex-function')
            self._xmlFunc(func,self._funcvars[i+1])

        if len(self._exvardecl)>0:
            exvar=etree.SubElement(root,'ex-var')
            for data in self._exvardecl:
                self._xmlVar(exvar,data)

        if len(self._vardecl)>0:
            autovar=etree.SubElement(root,'auto-var')
            for data in self._vardecl:
                self._xmlVar(autovar,data)

        matrix=etree.SubElement(root,'matrix')
        self._xmlMatrix(matrix)

        with open(filename,'w') as fh:
            fh.write(etree.tostring(root,pretty_print=True,encoding='utf-8'))

    def _xmlFunc(self,element,funcdata):
        for idx,data in enumerate(funcdata):
            sub=etree.SubElement(element,'param%d'%(idx,))
            sub.set('type',data[0])
            sub.set('name',data[1])
    def _xmlVar(self,element,vardata):
        subvar=etree.SubElement(element,'var')
        subvar.set('type',vardata[0])
        subvar.set('name',vardata[1])
        if len(vardata)==3:
            subvar.set('value',vardata[2])
        elif len(vardata)==5:
            subvar.set('method',vardata[2])
            subvar.set('value',vardata[3])
            subvar.set('size',vardata[4])
    def _xmlMatrix(self,element):
        if len(self._invars)>0:
            invar=etree.SubElement(element,'in-var')
            for idx,v in enumerate(self._invars):
                inv=etree.SubElement(invar,'var%d'%(idx,))
                inv.set('name',v)
        if len(self._outvars)>0:
            outvar=etree.SubElement(element,'out-var')
            for idx,v in enumerate(self._outvars):
                outv=etree.SubElement(outvar,'var%d'%(idx,))
                outv.set('name',v)
        for i in range(len(self._incond)):
            item=etree.SubElement(element,'rule%d'%(i,))
            if len(self._incond[i])>0:
                irule=etree.SubElement(item,'in-rule')
                for idx,value in enumerate(self._incond[i]):
                    ivalue=etree.SubElement(irule,'value%d'%(idx,))
                    ivalue.set('value',value)
            if len(self._outcond[i])>0:
                orule=etree.SubElement(item,'out-rule')
                for idx,value in enumerate(self._outcond[i]):
                    ovalue=etree.SubElement(orule,'value%d'%(idx,))
                    ovalue.set('value',value)

    def initData(self):
        # output for splitTxt
        self._funcs=()
        self._extvars=()
        self._autovars=()
        self._iomatrix=()
        # output for parseTxt
        self._funcvars=[]
        self._exvardecl=[]
        self._vardecl=[]
        self._invars=[]
        self._outvars=[]
        self._incond=[]
        self._outcond=[]

    def splitTxt(self,data8):
        flag=0 #0:init
        step=0
        flagtable=((self.D_FLAGSTR1,1),
                   (self.D_FLAGSTR21,2),
                   (self.D_FLAGSTR31,3),
                   (self.D_FLAGSTR41,4),
                   (self.D_FLAGSTR51,5))
        donetable=[]
        funcdeclare=''
        autovars=[]
        iomatrix=[]
        extfunc=[]
        extvars=[]
        for lineno,line in enumerate(data8.splitlines()):
            if flag==0:
                for item in flagtable:
                    if line.startswith(item[0]):
                        self._log.debug('Found Start-tag:%d at line:%d'%(item[1],lineno))
                        if item[1] not in donetable:
                            flag=item[1]
                            donetable.append(flag)
                            step=0
                            break
                        else:
                            self._log.warning('Found Duplicated Start-tag:%d'%(item[1],))
            if flag==1:
                # function declare
                if step==0:
                    step=1
                elif step>=1:
                    funcdeclare=line.strip()
                    self._log.debug('Found End-tag:%d at line:%d'%(flag,lineno))
                    flag=0
            elif flag==2:
                # auto vars
                if step<2:
                    step+=1
                elif step>=2:
                    if line.startswith(self.D_FLAGSTR22):
                        self._log.debug('Found End-tag:%d at line:%d'%(flag,lineno))
                        flag=0
                    else:
                        autovars.append(line.strip())
            elif flag==3:
                # i/o matrix
                if step==0:
                    step+=1
                else:
                    iomatrix.append(line)
                    if self.D_FLAGSTR32 in line:
                        self._log.debug('Found End-tag:%d at line:%d'%(flag,lineno))
                        flag=0
            elif flag==4:
                # extern function
                if step==0:
                    step+=1
                else:
                    if line.startswith(self.D_FLAGSTR42):
                        self._log.debug('Found End-tag:%d at line:%d'%(flag,lineno))
                        flag=0
                    else:
                        extfunc.append(line.strip())
            elif flag==5:
                # extern vars
                if step<2:
                    step+=1
                else:
                    if line.startswith(self.D_FLAGSTR52):
                        self._log.debug('Found End-tag:%d at line:%d'%(flag,lineno))
                        flag=0
                    else:
                        extvars.append(line.strip())
        self._autovars=tuple(autovars)
        self._iomatrix=tuple(iomatrix)
        funcs=[]
        funcs.append(funcdeclare)
        funcs.extend(extfunc)
        self._funcs=tuple(funcs)
        self._extvars=tuple(extvars)

    def parseTxt(self):
        for func in self._funcs:
            self._funcvars.append(self.parseFuncDecl(func))
        self.parseExtVars()
        self.parseAutoVars()
        self.parseIOMatrix()

    def parseFuncDecl(self,fdec):
        self._log.info('Parse Function Declaration:%s'%(fdec,))
        pos_l=fdec.find('(')
        pos_r=fdec.rfind(')')
        outdata=[]
        if pos_l<0 or pos_r!=len(fdec)-1:
            self._log.warning('cannot find proper "(" and ")"')
        else:
            outdata.append(self._parseFuncParam(fdec[:pos_l]))
            for param in fdec[pos_l+1:pos_r].split(','):
                outdata.append(self._parseFuncParam(param))
        return tuple(outdata)
    def _parseFuncParam(self,data):
        self._log.debug('Parse Function Parameter:%s'%(data,))
        ptype=''
        pname=''
        sdata=data.strip()
        rpat=re.compile(r'(?P<type>.+[^a-zA-Z0-9_])(?P<name>[a-zA-Z0-9_]+)')
        rret=rpat.search(sdata)
        if rret:
            ptype=rret.group('type').strip()
            pname=rret.group('name').strip()
        return tuple((ptype,pname))

    def parseExtVars(self):
        for line in self._extvars:
            self._log.debug('Parse External Parameter:%s'%(line,))
            parts=line.split(self.D_FIELDSEP)
            if len(parts)<2:
                self._log.warning('Input Check Error, Skip')
            else:
                self._exvardecl.append((parts[0],parts[1]))
    def parseAutoVars(self):
        for line in self._autovars:
            self._log.debug('Parse Internal Parameter:%s'%(line,))
            parts=line.split(self.D_FIELDSEP)
            if len(parts)<2:
                self._log.warning('Input Check Error, Skip')
            else:
                if len(parts)==2:
                    parts.append('0')
                if parts[2]=='memset':
                    if len(parts)<4:
                        parts.append('')
                    if parts[3]=='':
                        parts[3]='0'
                    if len(parts)<5:
                        parts.append('')
                    if parts[4]=='':
                        parts[4]='sizeof(%s)'%(parts[0],)
                    self._vardecl.append(tuple(parts[0:5]))
                elif parts[2]=='memcpy':
                    if len(parts)<4:
                        parts.append('')
                    if parts[3]=='':
                        self._log.warning('No Source Buffer Found, Change To memset')
                        parts[2]='memset'
                        parts[3]='0'
                    if len(parts)<5:
                        parts.append('')
                    if parts[4]=='':
                        parts[4]='sizeof(%s)'%(parts[0],)
                    self._vardecl.append(tuple(parts[0:5]))
                else:
                    self._vardecl.append(tuple(parts[0:3]))

    def parseIOMatrix(self):
        inidx,outidx=0,0
        parts=self._iomatrix[0].split(self.D_FIELDSEP)
        if self.D_FLAGSTR34 in parts:
            inidx=parts.index(self.D_FLAGSTR34)
        else:
            self._log.error('No Output Found')
            return
        parts=self._iomatrix[-1].split(self.D_FIELDSEP)
        if self.D_FLAGSTR32 in parts:
            outidx=parts.index(self.D_FLAGSTR32)
        else:
            self._log.error('Cannot Figure Out Count Of In/Out Vars')
            return
        parts=self._iomatrix[1].split(self.D_FIELDSEP)
        if len(parts)<=outidx:
            self._log.error('Not Enough In/Out Vars')
            return
        else:
            if self.D_MARK1 in parts:
                parts[parts.index(self.D_MARK1)]='__RET__'
            for i in range(inidx):
                self._invars.append(parts[i].strip())
            for i in range(outidx-inidx+1):
                self._outvars.append(parts[i+inidx].strip())
        for line in self._iomatrix[2:-1]:
            self._log.debug('Parse I/O Matrix:%s'%(line.decode('utf-8'),))
            parts=line.split(self.D_FIELDSEP)
            for markfrom,markto in ((self.D_MARK2,'__CALL__'),
                                    (self.D_MARK3,'__NOCALL__'),
                                    (self.D_MARK4,'__NOTCARE__'),
                                    (self.D_MARK5,'__NOACT__'),
                                    (self.D_MARK6,'__ELSE__')):
                while markfrom in parts:
                    parts[parts.index(markfrom)]=markto
            self._incond.append([])
            self._outcond.append([])
            for i in range(inidx):
                self._incond[-1].append(parts[i].strip())
            for i in range(outidx-inidx+1):
                self._outcond[-1].append(parts[i+inidx].strip())

if __name__ == '__main__':
    t=Txt2Xml()
    t.loadTxt('../test/test_push_queue.txt','cp932')
    t.toXml('../ignore/test_push_queue.xml')
