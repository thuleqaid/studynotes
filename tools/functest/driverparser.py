from cparser import tokenmanager as tm
from logutil import LogUtil

class DriverParser(object):
    def __init__(self,tokenmanager=tm):
        self._log=LogUtil().logger('DriverParser')
        self._tm=tokenmanager
        self._dfile=''
        self._tfile=''
        self._funcdriver=''
        self._functarget=''
        self._funcdmy=()
    def parse(self,driverfile):
        tfile=driverfile+self._tm.D_EXT_TOK
        if self._tm.genTokenFile(driverfile,tfile):
            fblist=self._tm.getFunctionList(tfile)
            fdlist=self._tm.getFunctionDeclarationList(tfile)
            fbset=set()
            for func in fblist:
                parts=func.split(':')
                funcname=parts[5]
                #fullfuncname=parts[6]
                fbset.add(funcname)
            fdset=set()
            for func in fdlist:
                parts=func.split(':')
                funcname=parts[5]
                #fullfuncname=parts[6]
                fdset.add(funcname)
            driverfunc=tuple(fbset-fdset)
            testfunc=tuple(fdset-fbset)
            if len(driverfunc)!=1 or len(testfunc)!=1:
                self._log.error('Driver file format error')
                return False
            else:
                self._dfile=driverfile
                self._tfile=tfile
                self._funcdriver=driverfunc[0]
                self._functarget=testfunc[0]
                self._funcdmy=tuple(fdset & fbset)
                return True
        return False
    @property
    def driver_func(self):
        return self._funcdriver
    @property
    def target_func(self):
        return self._functarget
    @property
    def dummy_func(self):
        return tuple(self._funcdmy)

def formatExcelText(funcname,finfo):
    '''
    @param funcname:
    @param finfo: cparser.getTestFuncInfo()[funcname][idx]
    @ret   text for Excel
    '''
    log=LogUtil().logger('DriverParser')
    outtxt=''
    # target function
    fdecl=finfo['decl']
    funcstr=' %s '%(funcname,)
    didx=fdecl.find(funcstr)
    functype=fdecl[0:didx]
    didx+=len(funcstr)
    startidx=fdecl.find('(',didx)
    stopidx=fdecl.rfind(')')
    parts=fdecl[startidx+1:stopidx].strip().split(' ')
    params=[]
    while ',' in parts:
        didx=parts.index(',')
        params.append(parts[0:didx])
        parts=parts[didx+1:]
    outtxt+='%s\n'%(fdecl,)
    outtxt+='ret = %s(%s);\n\n'%(funcname,','.join([x[-1] for x in params if len(x)>1]))
    for x in params:
        if len(x)>1:
            outtxt+='%s\t%s\tlocal\tmemset((char*)&%s,0x7c,sizeof(%s));\n'%(x[-1],' '.join(x[0:-1]),x[-1],' '.join(x[0:-1]))
    outtxt+='\nret\t%s\tlocal\tmemset((char*)&ret,0x7c,sizeof(%s));\n\n'%(functype,functype)
    # dummy function
    fcalls=finfo['calls']
    fothers=finfo['calldecl']
    flog={}
    for fcall in fcalls:
        parts=fcall.split(':')
        funcstr=' '+parts[0]+' '
        funccnt=int(parts[1])
        flog[fcall]=[]
        for fother in fothers:
            if funcstr in fother:
                if len(flog[fcall])<1:
                    didx=fother.find(funcstr)
                    if funccnt>1:
                        for i in range(funccnt):
                            outname=fother[0:didx+1]+'dummy'+str(i+1)+'_'+fother[didx+1:]
                            outtxt+='%s\t%s\tfunction\n'%(outname,fother[0:didx])
                    else:
                        outname=fother
                        outtxt+='%s\t%s\tfunction\n'%(outname,fother[0:didx])
                else:
                    # multiple function body for one dummy function
                    pass
                flog[fcall].append(fother)
    for key,value in sorted(flog.iteritems()):
        if len(value)==0:
            log.debug('No Function Body[%s] Found'%(key,))
            outtxt+='%s\t\tfunction\n'%(key,)
        elif len(value)>1:
            tmpset=set(value)
            if len(tmpset)>1:
                log.debug('Muliple Function Bodies[%s] Found:%s'%(key,str(tmpset)))
    return outtxt

if __name__ == '__main__':
    dp=DriverParser()
    driverfile='ignore/Driver2_mum_rpc_call.c'
    dp.parse(driverfile)
    print(dp.driver_func)
    print(dp.target_func)
    print(dp.dummy_func)
