import re
import os.path
# Version 3.0
class FileParser(object):
    def __init__(self,path=''):
        self._path=''
        self._info={} # key=$funcname,value=dict(key=$testcase,value=tuple($vars))
        self.setPath(path)
    def setPath(self,path):
        if os.path.exists(path):
            self._path=path
            self.parse()
    def parse(self):
        pass
    def warning(self):
        outtext='File:'+self._path+"\n"
        for key in sorted(self._info.iterkeys()):
            key2list=sorted(self._info[key].iterkeys())	# list for test cases of function(key)
            if len(key2list)>1:
                cvars=[]	# list for checked vars
                wvars=[]	# list for vars which are designed to the same values across all the test cases
                for key2 in key2list:
                    val2=self._info[key][key2]	# list of vars for the current test case
                    for key3 in val2:
                        bCheck=True
                        iCount=0
                        if key3[0] not in cvars:
                            for val22 in self._info[key].values():
                                for itemkey in val22:
                                    if itemkey[0]==key3[0]:
                                        if itemkey[1]==key3[1]:	# initial values are equal
                                            if itemkey[2]==key3[2]:	# expected values are equal or both are 'INIT'
                                                iCount+=1
                                            elif itemkey[2]=='INIT' and itemkey[1]==key3[2]:
                                                iCount+=1
                                            elif key3[2]=='INIT' and itemkey[2]==key3[1]:
                                                iCount+=1
                                            else:
                                                bCheck=False
                                                break
                                        else:
                                            bCheck=False
                                            break
                                if not bCheck:
                                    break
                            cvars.append(key3[0])
                            if bCheck and iCount>1:
                                wvars.append(key3[0])
                if len(wvars)>0:
                    outtext+="\t\tFunction:"+key+"\n"
                    outtext+="\t\t\t"+"\n\t\t\t".join(wvars)+"\n"
        return outtext
    def __str__(self):
        outtext='File:'+self._path+"\n"
        for key in sorted(self._info.iterkeys()):
            outtext+="\tFunction:"+key+"\n"
            for (key2,val2) in sorted(self._info[key].iteritems()):
                outtext+="\t\tTest:"+key2+"\n"
                for item in sorted(val2,cmp=lambda x,y:cmp(len(y),len(x)) or cmp(x[0],y[0])):
                    outtext+="\t\t\t"+str(item)+"\n"
        return outtext

class PTUFileParser(FileParser):
    def __init__(self,path=''):
        super(PTUFileParser,self).__init__(path)
    def parse(self):
        self._info={}
        reempty=re.compile(r'^\s*$')
        fh=open(self._path,'rU')
        funcname,testcase='',''
        for line in fh.readlines():
            if reempty.search(line):
                pass
            else:
                line=line.rstrip()
                elements=re.split(r'\t',line)
                if elements[0]=='*PTU File*':
                    # ptu filename
                    pass
                elif elements[0]=='**SRC File**':
                    # src filename
                    pass
                elif elements[0]=='=Function=':
                    # funcname
                    funcname=elements[1]
                    self._info[funcname]={}
                elif elements[0]=='==Test==':
                    # testcase
                    testcase=elements[1]
                    self._info[funcname][testcase]=[]
                else:
                    # vars
                    self._info[funcname][testcase].append(tuple(elements))
        fh.close()

class XLSFileParser(FileParser):
    def __init__(self,path=''):
        super(XLSFileParser,self).__init__(path)
    def parse(self):
        self._info={}
        reempty=re.compile(r'^\s*$')
        fh=open(self._path,'rU')
        funcname,testcase='',''
        for line in fh.readlines():
            if reempty.search(line):
                pass
            else:
                line=line.rstrip()
                elements=re.split(r'\t',line)
                if elements[0]=='':
                    if elements[1]=='':
                        if elements[2]=='':
                            # vars
                            if len(elements)>=7:
                                # del test result
                                del elements[6]
                            self._info[funcname][testcase].append(tuple(elements[3:]))
                        else:
                            # testcase name
                            testcase=elements[2]
                            self._info[funcname][testcase]=[]
                    else:
                        # function name
                        funcname=elements[1]
                        self._info[funcname]={}
                else:
                    # filename
                    pass
        fh.close()

class XLSCheck(object):
    def __init__(self,xlsfile,ptufile,ignore_params=True):
        self._xls=XLSFileParser(xlsfile)
        self._ptu=PTUFileParser(ptufile)
        self._ignore_params=ignore_params
        self.initinfo()
        self.compare()
    def output_xls(self):
        return str(self._xls)
    def output_ptu(self):
        return str(self._ptu)
    def warning_xls(self):
        return self._xls.warning()
    def warning_ptu(self):
        return self._ptu.warning()
    def output_result(self):
        outtext=''
        for key in sorted(self._info.iterkeys()):
            outtext+=key+"\n"
            bTravel=False	# True if any error message has outputed
            multi={}	# record test cases' relations between ptu and xls
            bMulti=False	# True if one ptu case responsible for multiple xls sheet
            if self._info[key]['__flag__']:
                for key2 in sorted(self._info[key].iterkeys()):
                    if key2 != '__flag__':
                        if self._info[key][key2]['__flag__'] == '':
                            outtext+="\t"+key2+"\tMiss\n"
                            bTravel=True
                        else:
                            if self._info[key][key2]['__flag__'] in multi:
                                bMulti=True
                            else:
                                multi[self._info[key][key2]['__flag__']]=[]
                            multi[self._info[key][key2]['__flag__']].append(key2)
                            sublist=[x for x in sorted(self._info[key][key2].iterkeys()) if x != '__flag__' and not self._info[key][key2][x]]
                            if len(sublist)>0:
                                outtext+="\t"+key2+"\t"+self._info[key][key2]['__flag__']+"\n"
                                outtext+="\t\t"+"\tError\n\t\t".join(sublist)+"\tError\n"
                                bTravel=True
            else:
                outtext+="\tStatus:Miss\n"
                bTravel=True
            if bMulti:
                outtext+="\tWarning:1ToX\n"
                for key2 in sorted(multi.iterkeys()):
                    if len(multi[key2])>1:
                        outtext+="\t\t"+key2+"\t"+",".join(multi[key2])+"\n"
                bTravel=True
            if not bTravel:
                outtext+="\tStatus:OK\n"
        return outtext
    def __str__(self):
        outtext=''
        for key in sorted(self._info.iterkeys()):
            outtext+=key+"\t"+str(self._info[key]['__flag__'])+"\n"
            for key2 in sorted(self._info[key].iterkeys()):
                if key2 != '__flag__':
                    outtext+="\t"+key2+"\t"+self._info[key][key2]['__flag__']+"\n"
                    for key3 in sorted(self._info[key][key2].iterkeys()):
                        if key3 != '__flag__':
                            outtext+="\t\t"+key3+"\t"+str(self._info[key][key2][key3])+"\n"
        return outtext
    def initinfo(self):
        # construct result dict
        self._info={}
        for key in sorted(self._xls._info.iterkeys()):
            self._info[key]={}
            self._info[key]['__flag__']=False
            for (key2,val2) in sorted(self._xls._info[key].iteritems()):
                self._info[key][key2]={}
                self._info[key][key2]['__flag__']=''
                for item in val2:
                    if self._ignore_params:
                        if len(item)>3:
                            pass
                        else:
                            self._info[key][key2][item[0]]=False
                    else:
                        self._info[key][key2][item[0]]=False
    def compare(self):
        for key in sorted(self._xls._info.iterkeys()):
            if key in self._ptu._info:
                self._info[key]['__flag__']=True
                for (key2,val2) in sorted(self._xls._info[key].iteritems()):
                    # construct dict for function(key)'s testcase(key2) of xls file
                    set1={}
                    for item in val2:
                        if self._ignore_params and len(item)>3:
                            pass
                        else:
                            varkey=item[0].replace('->','.')
                            if item[2]=='INIT':
                                set1[varkey]=(item[1],item[1])
                            else:
                                set1[varkey]=(item[1],item[2])
                    for (key3,val3) in sorted(self._ptu._info[key].iteritems()):
                        # construct dict for function(key)'s testcase(key3) of ptu file
                        set2={}
                        for item in val3:
                            varkey=item[0].replace('->','.')
                            if item[1]=='=':
                                if item[2]=='INIT':
                                    set2[varkey]=('-','-')
                                elif item[2]=='=':
                                    set2[varkey]=('-','-')
                                else:
                                    set2[varkey]=('-',item[2])
                            else:
                                if item[2]=='INIT':
                                    set2[varkey]=(item[1],item[1])
                                elif item[2]=='=':
                                    set2[varkey]=(item[1],'-')
                                else:
                                    set2[varkey]=(item[1],item[2])
                        # compare set1 and set2
                        set3=[]
                        bCompare=True
                        for key4 in set1.keys():
                            if key4 in set2:
                                if set1[key4][0]==set2[key4][0] and set1[key4][1]==set2[key4][1]:
                                    # init and expect value are equal between the two dict
                                    pass
                                else:
                                    bCompare=False
                                    break
                            else:
                                # vars in dict(set1) does not exist in dict(set2)
                                set3.append(key4)
                        if bCompare:
                            #testcase matches between the two file
                            for key4 in self._info[key][key2]:
                                if key4=='__flag__':
                                    self._info[key][key2][key4]=key3
                                elif key4 not in set3:
                                    self._info[key][key2][key4]=True

if __name__=='__main__':
    import logging
    log=logging.getLogger()
    #log.setLevel(logging.DEBUG)	# output warning,info,debug
    log.setLevel(logging.INFO)	# output warning,info
    #log.setLevel(logging.WARNING)	# output warning
    logh=logging.FileHandler('result.txt',mode='w')
    logf=logging.Formatter('%(message)s')
    logh.setFormatter(logf)
    log.addHandler(logh)
    check=XLSCheck('xls.txt','ptu.txt')
    log.warning("====================\n=======Result=======\n====================")
    log.warning(check.output_result())
    log.info("\n====================\n======Detail_P======\n====================")
    log.info(check.output_ptu())
    log.info("\n====================\n======Detail_X======\n====================")
    log.info(check.output_xls())
    log.debug("\n====================\n=====Warnings_P=====\n====================")
    log.debug(check.warning_ptu())
    log.debug("\n====================\n=====Warnings_X=====\n====================")
    log.debug(check.warning_xls())
