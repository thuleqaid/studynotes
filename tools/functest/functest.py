from os.path import exists,isdir,join,abspath,split,normpath
from os import listdir,makedirs,getcwdu,chdir
import subprocess
from shutil import copyfile
import re
import cparser
import driverparser
from logutil import LogUtil

class TestManager(object):
    def __init__(self,tokenmanager=cparser.tokenmanager):
        self._log=LogUtil().logger('TestManager')
        self._tm=tokenmanager
        self._dp=driverparser.DriverParser()
        self._vc=VcProj()
    def generateProj(self,info):
        '''
        @param info:{'driverfile':"xxx",
                     'srcpath':"xxx",
                     'tokpath':"xxx",
                     'autovc':True/False,
                     'vcproj':"xxx",
                     'mcdc':True/False,
                     'tplpath':"xxx", # folder for template files
                     'vcpath':"xxx",
                     'testrtpath':"xxx', # used when mcdc==True
                    }
        '''
        if self._checkParam(info):
            self._dp.parse(info['driverfile'])
            # only one source file contains target_func?
            fdict=cparser.getFuncInfo(info['srcpath'],info['tokpath'],self._dp.target_func)
            fileset=set()
            for finfo in fdict[self._dp.target_func]:
                fileset.add(finfo['srcfile'])
            if len(fileset)>1:
                self._log.error('Found function[%s] in multiple files:%s'%(self._dp.target_func,str(fileset)))
                return False
            tokfile=fdict[self._dp.target_func][0]['tokfile']
            cinfo={'FB':(self._dp.target_func,),'DMY':[]}

            # copy driver file
            copieddir=normpath(info['driverfile'][0:info['driverfile'].rfind('.')])
            if not exists(copieddir) or not isdir(copieddir):
                makedirs(copieddir)
            driverfile=split(info['driverfile'])[1]
            copyfile(info['driverfile'],join(copieddir,driverfile))

            # new source filename for the test
            copiedfile=join(copieddir,self._dp.target_func+'.c')
            cinfo['OF']=copiedfile

            # function rename ?
            dmyinfo={}
            dmyptn=re.compile(r'^dummy(?P<index>\d*)_(?P<name>.+)')
            for dfunc in self._dp.dummy_func:
                rret=dmyptn.search(dfunc)
                if rret:
                    fname=rret.group('name')
                    fidx=rret.group('index')
                    if fidx:
                        cnt=int(fidx)
                    else:
                        cnt=-1
                    if fname not in dmyinfo:
                        dmyinfo[fname]=[]
                    dmyinfo[fname].append(cnt)
            for dfunc,cnts in dmyinfo.items():
                tmplist=[dfunc,]
                for cnt in sorted(cnts):
                    if cnt>=0:
                        tmplist.append('dummy%d_%s'%(cnt,dfunc))
                if -1 in cnts:
                    tmplist.append('dummy_%s'%(dfunc,))
                cinfo['DMY'].append(tuple(tmplist))

            # copy source file
            cparser.copyFile(tokfile,cinfo)

            # copy other template files
            tplfile='common_func_c'
            outfile='common_func.c'
            copyfile(join(info['tplpath'],tplfile),join(copieddir,outfile))

            # generate files based on template
            tplfile='test_main_c'
            outfile='test_main.c'
            self._genMain(self._dp.driver_func,join(info['tplpath'],tplfile),join(copieddir,outfile))
            incstr=''.join(cparser.copyFile(tokfile,{}))
            tplfile='drvinputfileread_h'
            outfile='drvinputfileread.h'
            self._genHeader(incstr,join(info['tplpath'],tplfile),join(copieddir,outfile))

            # set files to be linked
            filelist=['.\\common_func.c',
                      '.\\test_main.c',
                      '.\\%s.c'%(self._dp.target_func,),
                      '.\\%s'%(driverfile,),
                     ]

            flag_mcdc=info.get('mcdc',False)
            if flag_mcdc and 'testrtpath' not in info:
                flag_mcdc=False
            if flag_mcdc:
                outfile='TP.obj'
                copyfile(join(info['tplpath'],outfile),join(copieddir,outfile))
                filelist.append('.\\TP.obj')

            # generate *.vcproj
            tplfile='xxx_vcproj'
            outfile='xxx.vcproj'
            if info.get('autovc',False):
                searchpath=split(fileset.pop())[0]
                self._vc.autoVcproj(searchpath,join(info['tplpath'],tplfile),join(copieddir,outfile),filelist)
            else:
                self._vc.generateVcproj(info['vcproj'],join(info['tplpath'],tplfile),join(copieddir,outfile),filelist)

            if flag_mcdc:
                tplfile='xxx_rsp'
                outfile='xxx.rsp'
                self._genRsp(self._vc._incpath,self._vc._compileoption,self._dp.target_func,join(info['tplpath'],tplfile),join(copieddir,outfile))
                self._switchTestRT(True,info['tplpath'],info['vcpath'],info['testrtpath'])
                self._compileTestRT(copieddir,info['vcpath'])
                self._switchTestRT(False,info['tplpath'],info['vcpath'],info['testrtpath'])

            self._buildProj(copieddir,info['vcpath'])
            self._runProj(copieddir)
            return True
        else:
            return False

    def _checkParam(self,info):
        mustfield=('driverfile',
                   'srcpath',
                   'tokpath',
                   'tplpath',
                   'vcpath',
                  )
        for mf in mustfield:
            if mf not in info:
                return False
        if not info.get('autovc',False):
            if 'vcproj' not in info:
                return False
        return True
    def _genMain(self,testfunc,tplfile,outfile):
        fin=open(tplfile,'rU')
        fout=open(outfile,'w')
        for line in fin.readlines():
            if '#Declaration#' in line:
                line='extern void %s(void);\n'%(testfunc,)
            elif '#Call#' in line:
                line='\t%s();\n'%(testfunc,)
            fout.write(line)
        fout.close()
        fin.close()
    def _genHeader(self,incstr,tplfile,outfile):
        fin=open(tplfile,'rU')
        fout=open(outfile,'w')
        for line in fin.readlines():
            if '#include#' in line:
                line='%s\n'%(incstr,)
            fout.write(line)
        fout.close()
        fin.close()
    def _genRsp(self,incstr,costr,funcname,tplfile,outfile):
        fin=open(tplfile,'rU')
        lines=fin.read()
        fin.close()
        outinc=incstr.replace(';','" /I "')
        outinc='/I "'+outinc+'"'
        outco=costr.replace(';','" /D "')
        outco='/D "'+outco+'"'
        lines=lines.decode('utf-16')
        lines=lines.replace('${inc_path}',outinc)
        lines=lines.replace('${compile_option}',outco)
        lines=lines.replace('${target_file}',funcname+'.c')
        fout=open(outfile,'w')
        fout.write(lines.encode('utf-16'))
        fout.close()
        outdir=split(outfile)[0]
        outfile2='TestRtInstrList.txt'
        fout=open(join(outdir,outfile2),'w')
        fout.write('%s\.(c|obj)\n'%(funcname,))
        fout.close()
        outfile2='%s.xtp'%(funcname,)
        fout=open(join(outdir,outfile2),'w')
        fout.write('%s.fdc\natlout.spt\n'%(funcname,))
        fout.close()
    def _switchTestRT(self,flag,tplpath,vcdir,testrtdir):
        if flag:
            folder='TestRT_ON'
        else:
            folder='TestRT_OFF'
        folder=join(tplpath,folder)
        for outfile in ('cl.exe','link.exe'):
            copyfile(join(folder,outfile),join(vcdir,outfile))
        for outfile in ('tdpGen.log','tp.ini','tpcpp.ini'):
            copyfile(join(folder,outfile),join(testrtdir,outfile))
    def _compileTestRT(self,projdir,vcdir):
        cwd=getcwdu()
        cmd=[join(vcdir,'cl.exe'),'@xxx.rsp','/nologo','/errorReport:prompt','>log_compile.txt']
        chdir(projdir)
        debugdir='Debug'
        if not exists(debugdir) or not isdir(debugdir):
            makedirs(debugdir)
        try:
            subprocess.call(cmd)
        except subprocess.CalledProcessError as e:
            self._log.error('Unknown Error During Build With TestRealTime')
        finally:
            chdir(cwd)
    def _buildProj(self,projdir,vcdir):
        cwd=getcwdu()
        folderdir=normpath(vcdir)
        parts=split(folderdir)
        while not parts[1]:
            folderdir=parts[0]
            parts=split(folderdir)
        folderdir=parts[0]
        cmd=[join(folderdir,'vcpackages','vcbuild.exe'),'xxx.vcproj','debug']
        chdir(projdir)
        try:
            subprocess.call(cmd)
        except subprocess.CalledProcessError as e:
            self._log.error('Unknown Error During Build Project')
        finally:
            chdir(cwd)
    def _runProj(self,projdir):
        cwd=getcwdu()
        chdir(projdir)
        exefile=join('Debug','xxx.exe')
        if exists(exefile):
            cmd=[exefile,]
            try:
                subprocess.call(cmd)
            except subprocess.CalledProcessError as e:
                self._log.error('Unknown Error During Run Exe')
        else:
            self._log.error('Compile/Link Error')
        chdir(cwd)

class VcProj(object):
    def __init__(self):
        self._log=LogUtil().logger('TestManager')
    def autoVcproj(self,searchpath,tplfile,outfile,filelist):
        srcvcproj=self._findVcproj(searchpath)
        if srcvcproj:
            self.generateVcproj(srcvcproj,tplfile,outfile,filelist)
    def generateVcproj(self,infile,tplfile,outfile,filelist):
        if exists(infile):
            info=self._getVcprojInfo(infile)
            self.manualVcproj(info[0],info[1],tplfile,outfile,filelist)
    def manualVcproj(self,incpath,compileoption,tplfile,outfile,filelist):
        self._genVcproj(outfile,incpath,compileoption,filelist,tplfile)
    def _genVcproj(self,outfile,incpath,compileoption,filelist,tplfile):
        self._log.debug('Generate .vcproj file:%s'%(outfile,))
        incpath=incpath.strip(' ;')
        incpath=re.sub(r';+',r';',incpath)
        compileoption=compileoption.strip(' ;')
        compileoption=re.sub(r';+',r';',compileoption)
        fin=open(tplfile,'rU')
        fout=open(outfile,'w')
        for line in fin.readlines():
            if 'AdditionalIncludeDirectories=""' in line:
                self._log.debug('Set IncludePath:%s'%(incpath,))
                fout.write('\t\t\t\tAdditionalIncludeDirectories="%s"\n'%(incpath,))
            elif 'PreprocessorDefinitions=""' in line:
                self._log.debug('Set CompileOption:%s'%(compileoption,))
                fout.write('\t\t\t\tPreprocessorDefinitions="%s"\n'%(compileoption,))
            elif '<Files>' in line:
                self._log.debug('Set File:%s'%(str(filelist),))
                fout.write(line)
                for filename in filelist:
                    line='\t\t<File\n\t\t\tRelativePath="%s"\n\t\t\t>\n\t\t</File>\n'%(filename,)
                    fout.write(line)
            else:
                fout.write(line)
        self._incpath=incpath
        self._compileoption=compileoption
        fout.close()
        fin.close()
    def _getVcprojInfo(self,vcprojfile,part='Debug|Win32'):
        self._log.debug('Read .vcproj file:%s, part:%s'%(vcprojfile,part))
        fin=open(vcprojfile,'rU')
        incpath=''
        compileoption=''
        flag=False
        for line in fin.readlines():
            if flag:
                if not incpath and 'AdditionalIncludeDirectories' in line:
                    startidx=line.find('"')
                    stopidx=line.rfind('"')
                    incpath=line[startidx+1:stopidx]
                    self._log.debug('IncludePath:%s'%(incpath,))
                elif not compileoption and 'PreprocessorDefinitions' in line:
                    startidx=line.find('"')
                    stopidx=line.rfind('"')
                    compileoption=line[startidx+1:stopidx]
                    self._log.debug('CompileOption:%s'%(compileoption,))
            else:
                if part in line:
                    flag=True
        fin.close()
        return incpath,compileoption
    def _findVcproj(self,startfolder):
        if exists(startfolder) and isdir(startfolder):
            sdir=abspath(startfolder)
            while True:
                self._log.debug('Find .vcproj file in folder:%s'%(sdir,))
                for curfile in listdir(sdir):
                    if curfile.upper().endswith('.VCPROJ'):
                        self._log.debug('Found .vcproj file:%s'%(join(sdir,curfile)))
                        return join(sdir,curfile)
                # move to parent dir
                while True:
                    parts=split(sdir)
                    if parts[0]==sdir:
                        # sdir is root dir(e.g d:/)
                        self._log.error('Cannot find .vcproj file until root folder')
                        return ''
                    sdir=parts[0]
                    if parts[1]=='':
                        # sdir endswith '/'
                        pass
                    else:
                        break
        else:
            return ''

if __name__ == '__main__':
    srcpath="D:/15CY_MU/component/navi/func_core/mu/modules"
    tokpath="ignore/tokens"
    tm=TestManager()
    tm._tm.parseFolder(srcpath,tokpath)
    info={'driverfile':"ignore/Driver5_mum_prgUpdCallback.c",
          'srcpath':srcpath,
          'tokpath':tokpath,
          'autovc':False,
          'vcproj':"D:/gitroot/functest/ignore/tpl/stc_modules_stc.vcproj",
          'mcdc':True,
          'tplpath':"D:/gitroot/functest/ignore/tpl",
          'vcpath':"C:/Program Files/Microsoft Visual Studio 8/VC/bin",
          'testrtpath':"C:/Program Files/Rational/TestRealTime/targets/cvisual8express_denso2",
         }
    tm.generateProj(info)
