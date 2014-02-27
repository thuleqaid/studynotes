import re
import os
from logutil import LogUtil
import cparser
import driverparser

class DmyRenameBase(object):
    '''
    Usage:
        1. dr=DmyRenameBase()
        2. dr.setSourcePath(srcpath,tokpath)
        3. dr.setFuncName(funcname)
        4. dr.setDmyFunc(dmyfuncs)
        5. dr.doRename()
        6. dr.doRestore()
    '''
    def __init__(self):
        self._log=LogUtil().logger('dummy')
        self._srcpath=''
        self._tokpath=''
        self._funcname=''
    def setSourcePath(self,srcpath,tokpath):
        if os.path.exists(srcpath) and os.path.isdir(srcpath):
            self._srcpath=srcpath
            if not os.path.exists(tokpath) or not os.path.isdir(tokpath):
                os.makedirs(tokpath)
            self._tokpath=tokpath
            return True
        else:
            self._log.error('Invalid source file dir[%s]'%(srcpath,))
            return False
    def setFuncName(self,funcname):
        if not funcname:
            self._funcname=''
            return False
        else:
            self._funcname=str(funcname)
            return True
    def setDmyFunc(self,dmyfuncs):
        if dmyfuncs:
            self._dmyfunc=tuple(dmyfuncs)
            return True
        else:
            return False
    def doRename(self):
        funcfiles=self.filterFiles(self.findFunc())
        if not funcfiles:
            return False
        for finfo in funcfiles:
            tokfile=finfo['tokfile']
            self.rename(tokfile,self._funcname,self._dmyfunc)
    def doRestore(self):
        if self._srcpath:
            cparser.unDummyFolder(self._srcpath)
    def filterFiles(self,funcfiles):
        return funcfiles
    def findFunc(self):
        if not self._funcname:
            return ()
        if not self._srcpath or not self._tokpath:
            return ()
        tm=cparser.tokenmanager
        ret=tm.findFunctionBySrc(self._srcpath,self._tokpath,self._funcname)
        if len(ret[self._funcname])<1:
            return ()
        else:
            return tuple(ret[self._funcname])

    def rename(self,tokfile,funcname,dmylist):
        info={'FB':funcname,
              'DMY':tuple(dmylist),
              }
        cparser.dummyFile(tokfile,info)

class DmyRename(DmyRenameBase):
    '''
    Usage:
        1. dr=DmyRename()
        2. dr.setSourcePath(srcpath,tokpath)
        3. dr.setDriverFile(drvfile)
        4. dr.doRename()
        5. dr.doRestore()
    '''
    def __init__(self):
        super(DmyRename,self).__init__()
        self._ptndmy=re.compile(r'dummy(?P<no>\d*)_(?P<name>.+)')
    def setDriverFile(self,drvpath):
        if os.path.exists(drvpath) and os.path.isfile(drvpath):
            dp=driverparser.DriverParser()
            if dp.parse(drvpath):
                self.setFuncName(dp.target_func)
                self.setDmyFunc(self._groupDmyFuncs(dp.dummy_func))
                return True
            else:
                self._log.error('Parse test driver file[%s] failed'%(srcpath,))
                self.setFuncName('')
                self.setDmyFunc(())
                return False
        else:
            self._log.error('Invalid test driver file dir[%s]'%(srcpath,))
            return False
    def _groupDmyFuncs(self,dmyfuncs):
        outdict={}
        for dmy in dmyfuncs:
            patret=self._ptndmy.search(dmy)
            if patret:
                name=patret.group('name')
                no=patret.group('no')
                if no:
                    no=int(no)
                else:
                    no=-1
                if name not in outdict:
                    outdict[name]=[]
                outdict[name].append(no)
        ret=[]
        for name,nos in outdict.items():
            tmp=['dummy%d_%s'%(x,name) for x in nos if x>=0]
            if -1 in nos:
                ret.append(tuple([name,]+tmp+['dummy_%s'%(name,),]))
            else:
                ret.append(tuple([name,]+tmp))
        return tuple(ret)
    def filterFiles(self,funcfiles):
        return funcfiles

class DmyCopy(DmyRename):
    '''
    Usage:
        1. dr=DmyCopy()
        2. dr.setSourcePath(srcpath,tokpath)
        3. dr.setDriverFile(drvfile)
        4. dr.doCopy(copyinfo)
    '''
    def __init__(self):
        super(DmyCopy,self).__init__()
        self._copydir=''
    def doRename(self):
        pass
    def doRestore(self):
        pass
    def doCopy(self,**copyinfo):
        '''
        @param copyinfo:{'VI':(),
                         'VD':(),
                         'FD':(),
                         'FB':(),
                         'OD':'out file dir',
                         'OF':'out filename without extension(.c)', # suffix number in the case of multiple outfile
                        }
        '''
        self._copydir=''
        funcbodys=copyinfo.get('FB',())
        if self._funcname and self._funcname not in funcbodys:
            funcbodys=tuple(list(funcbodys)+[self._funcname,])
        if len(funcbodys)<1:
            return False
        outdir=copyinfo.get('OD','')
        outfile=copyinfo.get('OF','')
        if not outdir:
            return False
        funcfiles=self.filterFiles(self.findFunc())
        if not funcfiles:
            return False
        self._copydir=outdir
        if not os.path.exists(outdir) or not os.path.isdir(outdir):
            os.makedirs(outdir)
        fileset=set()
        for finfo in funcfiles:
            fileset.add(finfo['tokfile'])
        cinfo={'FB':funcbodys,
               'DMY':(),
               'VI':copyinfo.get('VI',()),
               'VD':copyinfo.get('VD',()),
               }
        if len(fileset)>1:
            for i,tokfile in enumerate(list(fileset)):
                cinfo['OF']=os.path.join(outdir,outfile+str(i+1)+'.c')
                cparser.copyFile(tokfile,cinfo)
        else:
            cinfo['OF']=os.path.join(outdir,outfile+'.c')
            cparser.copyFile(fileset.pop(),cinfo)
    def filterFiles(self,funcfiles):
        return funcfiles
if __name__ == '__main__':
    #dr=DmyRename()
    dr=DmyCopy()
    dr.setSourcePath('d:/15CY_MU/mu_1cpu_0221/mu/modules','ignore/tokens')
    #dr.doRestore()
    dr.setDriverFile('ignore/Driver2_mum_rpc_call.c')
    dr.doCopy(OD='ignore/copy',OF='test')
    #dr.doRename()
