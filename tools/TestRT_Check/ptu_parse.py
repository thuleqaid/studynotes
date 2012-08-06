import re
import os.path

class PTU_SECTION(object):
    def __init__(self,info):
        self.setInfo(info)
    def setInfo(self,info):
        self.initvar()
        self.parse(info)
    def initvar(self):
        pass
    def parse(self,info):
        pass

class PTU_TEST(PTU_SECTION):
    def __init__(self,statements):
        super(PTU_TEST,self).__init__(statements)
    def initvar(self):
        self._vars={}
    def parse(self,statements):
        revar=re.compile(r'^\s*VAR\s+(?P<var>\S+?)\s*,\s*INIT\s*=\s*(?P<init>.+?)\s*,\s*EV\s*=\s*(?P<ev>.+?)\s*$',re.I)
        for state in statements:
            rrevar=revar.search(state)
            if rrevar:
                self._vars[rrevar.group('var')]=(rrevar.group('init'),rrevar.group('ev'))
    def __str__(self):
        outtext=""
        for (key,val) in sorted(self._vars.iteritems()):
            outtext+=key+"\t"+val[0]+"\t"+val[1]+"\n"
        return outtext
        
class PTU_SERVICE(PTU_SECTION):
    def __init__(self,statements):
        super(PTU_SERVICE,self).__init__(statements)
    def initvar(self):
        self._tests={}
    def parse(self,statements):
        retstart=re.compile(r'^\s*TEST\s+(?P<test>\S+)',re.I)
        retstop=re.compile(r'^\s*END\s+TEST',re.I)
        flag_intest=False
        for state in statements:
            if not flag_intest:
                rretstart=retstart.search(state)
                if rretstart:
                    testname=rretstart.group('test')
                    flag_intest=True
                    testsrc=[state,]
            else:
                testsrc.append(state)
                if retstop.search(state):
                    flag_intest=False
                    self._tests[testname]=PTU_TEST(tuple(testsrc))
    def __str__(self):
        outtext=""
        for (key,val) in sorted(self._tests.iteritems()):
            outtext+="==Test==\t"+key+"\n"+str(val)
        return outtext

class PTU_Parser(PTU_SECTION):
    def __init__(self,filename=''):
        super(PTU_Parser,self).__init__(filename)
    def parse(self,filename):
        if os.path.exists(filename):
            self._ptufile=filename
            self.parseFile()
    def parseFile(self):
        resrc=re.compile(r'^--%c\s+attolstart\s+"(?P<src>.+?)"',re.I)
        refstart=re.compile(r'^SERVICE\s+(?P<funcname>\S+)',re.I)
        refstop=re.compile(r'^END\s+SERVICE',re.I)
        recomment=re.compile(r'^(\s*--|\s*$)',re.I)
        flag_header=False
        flag_infunc=False
        fh=open(self._ptufile,'rU')
        for line in fh.readlines():
            if not flag_header:
                rresrc=resrc.search(line)
                if rresrc:
                    flag_header=True
                    self._srcfile=rresrc.group('src')
            else:
                if not recomment.search(line):
                    line=line.rstrip()
                    if not flag_infunc:
                        rrefstart=refstart.search(line)
                        if rrefstart:
                            flag_infunc=True
                            funcname=rrefstart.group('funcname')
                            functest=[line,]
                    else:
                        rrefstop=refstop.search(line)
                        functest.append(line)
                        if rrefstop:
                            flag_infunc=False
                            self._funcs[funcname]=PTU_SERVICE(tuple(functest))
        fh.close()
    def initvar(self):
        self._ptufile=''
        self._srcfile=''
        self._funcs={}
    def __str__(self):
        outtext="*PTU File*\t"+self._ptufile+"\n"
        outtext+="**SRC File**\t"+self._srcfile+"\n"
        for (key,val) in sorted(self._funcs.iteritems()):
            outtext+="=Function=\t"+key+"\n"+str(val)+"\n"
        return outtext

if __name__=='__main__':
    refile=re.compile(r'\.ptu$',re.I)
    fh=open('ptu.txt','w')
    for items in os.walk('.'):
        for filename in items[2]:
            if refile.search(filename):
                ptufile=os.path.join(items[0],filename)
                p=PTU_Parser(ptufile)
                fh.write(str(p))
    fh.close()