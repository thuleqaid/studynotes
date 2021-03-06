import os
import re
import logging

# parsing cfg file
# cfg file: source codes formatted by gcc
#           generated by adding '--dump-tree-cfg'

class CfgFunc(object):
    def __init__(self,states,log=logging.getLogger()):
        self._log=log
        # regex patterns
        self._re_goto=re.compile(r'^\s+goto\s+(?P<label1><.+?>)(\s+\((?P<label2>.+?)\))?;$')
        self._re_switch=re.compile(r'^\s+switch\s+\((?P<var>.+)\)\s+<(?P<case>.+)>$')
        self._re_autovar=re.compile(r'\.\d+$')
        self._re_asign1=re.compile(r'^\s+(?P<dst>\S+)\s+=\s+(\(.+\)\s+)?(?P<src>\S+);$') # x = (type) y;
        self._re_asign2=re.compile(r'^\s+(?P<dst>\S+)\s+=\s+(?P<src1>\S+)\s+(?P<op>\S+)\s+(?P<src2>\S+);$') # x = y or z;
        self._re_asign3=re.compile(r'^\s+(?P<dst>\S+)\s+=\s+(?P<func>\S+)\s+\((?P<params>.*)\);$') # x = func (a, b, ..., z);
        self._re_asign4=re.compile(r'^\s+(?P<func>\S+)\s+\((?P<params>.*)\);$') # func (a, b, ..., z);
        self._re_digit=re.compile(r'^\s*(?P<num>[+-]?(0[xX][0-9a-fA-F]+|[0-9.]+B?))\s*$')
        self._re_variable=re.compile(r'^\s*[&*]?(?P<var>[a-zA-Z0-9_]+)')
        # parse func name and params
        self._parsefuncdecl(states[0])
        # parse func source
        self._parsebody(states[2:-1])
    def _parsefuncdecl(self,funcdecl):
        self._log.debug('CfgFunc:ParseFuncDecl:'+funcdecl)
        self._info={'variable':{},'func':{}}
        i=funcdecl.index('(')
        j=funcdecl.rindex(')')
        self._funcname=funcdecl[0:i-1]
        self._params=[]
        if j<=i+1:
            # no params
            pass
        else:
            params=funcdecl[i+1:j]
            for part in params.split(','):
                i=part.rindex(' ')
                paramname=part[i+1:]
                self._params.append(paramname)
                self._info['variable'][paramname]={'set':[],'get':[],'cond':[],'func':[]} #set:[(label,src_var1,src_varN)...],get:[(label,dst_var)...],cond:[(label,gotolabel,condition)...],func:[(label,funcname,index of param(1..N))...]
    def _parsebody(self,states):
        # func source is consisted by local vars declaration block and several code blocks
        # local vars declaration block goes first without a label if exists
        # the first line of a code block is "Label:" with nothing else
        self._log.debug('CfgFunc:ParseFuncBody:'+":".join(states))
        sects=[]
        self._localvars={'manual':[],'auto1':[],'auto2':[],'global':[]} # manual:source vars, auto1:gcc generated normal vars, auto2:gcc generated critical vars(used in condition statement or return statement)
        self._edges=[]
        self._block={}
        self._loop=[]
        self._prevlabel=''
        self._firstlabel=''
        self._lastlabel=''
        for line in states:
            if line:
                if line.startswith(' '):
                    pass
                else:
                    # new code block starts
                    if len(sects)>0:
                        self._parsesect(sects)
                        sects=[]
                sects.append(line)
        # parse the last code block
        self._parsesect(sects)
    def _parsesect(self,states):
        if states[0].startswith(' '):
            # local vars declaration block
            for line in states:
                varname=line[line.rindex(' ')+1:-1]
                if varname.find('[')>0:
                    varname=varname[:varname.find('[')]
                if self._re_autovar.search(varname):
                    self._localvars['auto1'].append(varname)
                else:
                    self._localvars['manual'].append(varname)
                self._info['variable'][varname]={'set':[],'get':[],'cond':[],'func':[]}
        else:
            # code block
            blocklabel=states[0][:-1]
            if not self._firstlabel:
                self._firstlabel=blocklabel
            if self._prevlabel:
                self._edges.append((self._prevlabel,blocklabel,""))
                self._prevlabel=''
            # code block patterns:
            # pattern 1:
            #  lines
            #  goto xxx;
            # pattern 2:
            #  lines
            #  if (...)
            #    goto xxx;
            #  else
            #    goto xxx;
            # pattern 3:
            #  lines
            #  switch (xxx) <xxx>
            # pattern 4:
            #  lines
            #  return ...
            # pattern 5:
            #  lines
            #
            #  next block
            if states[-1].startswith('  goto'):
                # pattern 1
                reret=self._re_goto.search(states[-1])
                if reret:
                    if reret.group('label2'):
                        label=reret.group('label2')
                    else:
                        label=reret.group('label1')
                    self._edges.append((blocklabel,label,""))
                    self._block[blocklabel]=tuple(states[1:-1])
                    if label in self._block:
                        self._loop.append((label,blocklabel))
                else:
                    # regex pattern error
                    self._log.error('CfgFunc:RegExPattern:'+states[-1])
            elif states[-1].startswith('    goto'):
                # pattern 2
                conditionindex=states[-4].find('(')
                if conditionindex>=0:
                    condition=states[-4][conditionindex+1:-1]
                    conditionname=condition[:condition.index(' ')]
                    conditionname2=self._findVar(conditionname)
                    if conditionname2:
                        if conditionname2 in self._localvars['auto1']:
                            self._localvars['auto2'].append(conditionname2)
                            self._localvars['auto1'].remove(conditionname2)
                        if conditionname2 not in self._info['variable']:
                            self._localvars['global'].append(conditionname2)
                            self._info['variable'][conditionname2]={'set':[],'get':[],'cond':[],'func':[]}
                    conditionnamex=condition[condition.rindex(' ')+1:]
                    conditionnamex2=self._findVar(conditionnamex)
                    if conditionnamex2:
                        if conditionnamex2 in self._localvars['auto1']:
                            self._localvars['auto2'].append(conditionnamex2)
                            self._localvars['auto1'].remove(conditionnamex2)
                        if conditionnamex2 not in self._info['variable']:
                            self._localvars['global'].append(conditionnamex2)
                            self._info['variable'][conditionnamex2]={'set':[],'get':[],'cond':[],'func':[]}
                    # True path
                    reret=self._re_goto.search(states[-3])
                    if reret:
                        if reret.group('label2'):
                            label=reret.group('label2')
                        else:
                            label=reret.group('label1')
                        self._edges.append((blocklabel,label,condition))
                        self._info['variable'][conditionname2]['cond'].append((blocklabel,label,condition))
                        if conditionnamex2:
                            self._info['variable'][conditionnamex2]['cond'].append((blocklabel,label,condition))
                        if label in self._block:
                            self._loop.append((label,blocklabel))
                    else:
                        # regex pattern error
                        self._log.error('CfgFunc:RegExPattern:'+states[-3])
                    # False path
                    reret=self._re_goto.search(states[-1])
                    if condition.find(' == ')>=0:
                        condition=condition.replace(' == ',' != ')
                    elif condition.find(' != ')>=0:
                        condition=condition.replace(' != ',' == ')
                    elif condition.find(' <= ')>=0:
                        condition=condition.replace(' <= ',' > ')
                    elif condition.find(' >= ')>=0:
                        condition=condition.replace(' >= ',' < ')
                    elif condition.find(' < ')>=0:
                        condition=condition.replace(' < ',' >= ')
                    elif condition.find(' > ')>=0:
                        condition=condition.replace(' > ',' <= ')
                    if reret:
                        if reret.group('label2'):
                            label=reret.group('label2')
                        else:
                            label=reret.group('label1')
                        self._edges.append((blocklabel,label,condition))
                        self._info['variable'][conditionname2]['cond'].append((blocklabel,label,condition))
                        if conditionnamex2:
                            self._info['variable'][conditionnamex2]['cond'].append((blocklabel,label,condition))
                        if label in self._block:
                            self._loop.append((label,blocklabel))
                    else:
                        # regex pattern error
                        self._log.error('CfgFunc:RegExPattern:'+states[-1])
                    self._block[blocklabel]=tuple(states[1:-4])
                else:
                    self._log.error('CfgFunc:if-CodeBlock:'+':'.join(states))
            elif states[-1].startswith('  switch'):
                # pattern 3
                reret=self._re_switch.search(states[-1])
                if reret:
                    var=reret.group('var')
                    conditionname2=self._findVar(var)
                    if conditionname2:
                        if conditionname2 in self._localvars['auto1']:
                            self._localvars['auto2'].append(conditionname2)
                            self._localvars['auto1'].remove(conditionname2)
                        if conditionname2 not in self._info['variable']:
                            self._localvars['global'].append(conditionname2)
                            self._info['variable'][conditionname2]={'set':[],'get':[],'cond':[],'func':[]}
                    cases=reret.group('case') # format:[default: <xx>, case x: <xx>, case x ... y: <xx>]
                    for item in cases.split(', '):
                        colon=item.index(':')
                        if item.startswith('case'):
                            self._edges.append((blocklabel,item[colon+2:],"%s == %s" % (var,item[5:colon])))
                            self._info['variable'][conditionname2]['cond'].append((blocklabel,item[colon+2:],"%s == %s" % (var,item[5:colon])))
                        elif item.startswith('default'):
                            self._edges.append((blocklabel,item[colon+2:],"%s == %s" % (var,item[0:colon])))
                            self._info['variable'][conditionname2]['cond'].append((blocklabel,item[colon+2:],"%s == %s" % (var,item[0:colon])))
                        else:
                            self._log.error('CfgFunc:RegExPattern:'+states[-1])
                    self._block[blocklabel]=tuple(states[1:-1])
                else:
                    self._log.error('CfgFunc:switch-CodeBlock:'+':'.join(states))
            elif states[-1].startswith('  return'):
                # pattern 4
                self._lastlabel=blocklabel
                self._block[blocklabel]=tuple(states[1:])
                if len(states[-1])>9:
                    var=states[-1][9:-1]
                    if var in self._localvars['auto1']:
                        self._localvars['auto2'].append(var)
                        self._localvars['auto1'].remove(var)
                else:
                    # void function
                    pass
            else:
                # pattern 5
                self._prevlabel=blocklabel
                self._block[blocklabel]=tuple(states[1:])
            for state in self._block[blocklabel]:
                ret1=self._re_asign1.search(state)
                ret2=self._re_asign2.search(state)
                ret3=self._re_asign3.search(state)
                ret4=self._re_asign4.search(state)
                if ret1:
                    dst=ret1.group('dst')
                    src=ret1.group('src')
                    dst2=self._findVar(dst)
                    if dst2 not in self._info['variable']:
                        self._localvars['global'].append(dst2)
                        self._info['variable'][dst2]={'set':[],'get':[],'cond':[],'func':[]}
                    self._info['variable'][dst2]['set'].append((blocklabel,dst,src))
                    src2=self._findVar(src)
                    if src2:
                        if src2 not in self._info['variable']:
                            self._localvars['global'].append(src2)
                            self._info['variable'][src2]={'set':[],'get':[],'cond':[],'func':[]}
                        self._info['variable'][src2]['get'].append((blocklabel,src,dst))
                elif ret2:
                    dst=ret2.group('dst')
                    src1=ret2.group('src1')
                    src2=ret2.group('src2')
                    src12=self._findVar(src1)
                    src22=self._findVar(src2)
                    dst2=self._findVar(dst)
                    if dst2 not in self._info['variable']:
                        self._localvars['global'].append(dst2)
                        self._info['variable'][dst2]={'set':[],'get':[],'cond':[],'func':[]}
                    self._info['variable'][dst2]['set'].append((blocklabel,dst,src1,src2))
                    if src12:
                        if src12 not in self._info['variable']:
                            self._localvars['global'].append(src12)
                            self._info['variable'][src12]={'set':[],'get':[],'cond':[],'func':[]}
                        self._info['variable'][src12]['get'].append((blocklabel,src1,dst))
                    if src22:
                        if src22 not in self._info['variable']:
                            self._localvars['global'].append(src22)
                            self._info['variable'][src22]={'set':[],'get':[],'cond':[],'func':[]}
                        self._info['variable'][src22]['get'].append((blocklabel,src2,dst))
                elif ret3:
                    dst=ret3.group('dst')
                    func=ret3.group('func')
                    params=ret3.group('params')
                    dst2=self._findVar(dst)
                    if dst2 not in self._info['variable']:
                        self._localvars['global'].append(dst2)
                        self._info['variable'][dst2]={'set':[],'get':[],'cond':[],'func':[]}
                    self._info['variable'][dst2]['set'].append((blocklabel,dst,func+'()',params))
                    pindex=1
                    for part in params.split(', '):
                        part2=self._findVar(part)
                        if part2:
                            if part2 not in self._info['variable']:
                                self._localvars['global'].append(part2)
                                self._info['variable'][part2]={'set':[],'get':[],'cond':[],'func':[]}
                            self._info['variable'][part2]['func'].append((blocklabel,part,func+'()',pindex))
                        pindex+=1
                    if func not in self._info['func']:
                        self._info['func'][func]=[]
                    self._info['func'][func].append((blocklabel,state))
                elif ret4:
                    func=ret4.group('func')
                    params=ret4.group('params')
                    pindex=1
                    for part in params.split(', '):
                        part2=self._findVar(part)
                        if part2:
                            if part2 not in self._info['variable']:
                                self._localvars['global'].append(part2)
                                self._info['variable'][part2]={'set':[],'get':[],'cond':[],'func':[]}
                            self._info['variable'][part2]['func'].append((blocklabel,part,func+'()',pindex))
                        pindex+=1
                    if func not in self._info['func']:
                        self._info['func'][func]=[]
                    self._info['func'][func].append((blocklabel,state))
                elif state.find('  return')>=0:
                    pass
                elif state.find('  // ')>=0:
                    pass
                else:
                    self._log.error('CfgFunc:RegExPattern:'+state)
    def _findVar(self,varname):
        oldlen=0
        outvar=''
        if varname=='':
            # empty string
            pass
        elif self._re_digit.search(varname):
            # numeric data
            pass
        else:
            for varkey in self._info['variable'].iterkeys():
                if varname.find(varkey)>=0 and len(varkey)>oldlen:
                    outvar=varkey
                    oldlen=len(outvar)
            if varname=='':
                # un-managed global variable
                gret=self._re_variable.search(varname)
                if gret:
                    outvar=gret.group('var')
                else:
                    self._log.error('CfgFunc:RegExVariable:'+varname)
        return outvar
    def toDot(self):
        outtext="digraph %s {\n\tnode [shape=\"box\"];\n" % self._funcname
        for item in self._edges:
            outtext+="\t%s -> %s" % (item[0],item[1])
            if item[2]:
                outtext+=" [label=\"%s\"]" % item[2]
            outtext+=";\n"
        outtext+="\tEntry -> %s;\n" % self._firstlabel
        if self._lastlabel:
            outtext+="\t%s -> Exit;\n" % self._lastlabel
            outtext+="\t%s [shape=\"Mdiamond\"];\n"%('Exit')
        for (key,value) in (sorted(self._block.iteritems())):
            value2='<'+key+'>\\l'+'\\l'.join(value)+'\\l'
            value2=value2.replace(r'"',r'\"')
            # fix parse error for firefox
            value2=value2.replace(r'&',r'&amp;amp;')
            outtext+="\t%s [label=\"%s\"];\n"%(key,value2)
        outtext+="\t%s [shape=\"ellipse\",label=\"%s\"];\n"%('Entry',self._funcname+'('+','.join(self._params)+')')
        outtext+="}\n"
        return outtext
    def __str__(self):
        outtext=self._funcname+"\n"
        for x in self._info['variable']:
            outtext+="\t"+x
            if x in self._localvars['global']:
                outtext+="\tGlobal"
            outtext+="\n"
            if len(self._info['variable'][x]['get'])>0:
                outtext+="\t\tGet:\n"
                outtext+="\t\t\t"+"\n\t\t\t".join([str(xx) for xx in self._info['variable'][x]['get']])
                outtext+="\n"
            if len(self._info['variable'][x]['set'])>0:
                outtext+="\t\tSet:\n"
                outtext+="\t\t\t"+"\n\t\t\t".join([str(xx) for xx in self._info['variable'][x]['set']])
                outtext+="\n"
            if len(self._info['variable'][x]['cond'])>0:
                outtext+="\t\tCond:\n"
                outtext+="\t\t\t"+"\n\t\t\t".join([str(xx) for xx in self._info['variable'][x]['cond']])
                outtext+="\n"
            if len(self._info['variable'][x]['func'])>0:
                outtext+="\t\tFunc:\n"
                outtext+="\t\t\t"+"\n\t\t\t".join([str(xx) for xx in self._info['variable'][x]['func']])
                outtext+="\n"
        for x in self._info['func']:
            outtext+="\t"+x+"\n"
            if len(self._info['func'][x])>0:
                outtext+="\t\t"+"\n\t\t".join([str(xx) for xx in self._info['func'][x]])
                outtext+="\n"
        outtext+="\n\t('First', '%s', '')" % self._firstlabel
        for x in self._edges:
            outtext+="\n\t"+str(x)
        outtext+="\n\t('%s', 'Last', '')" % self._lastlabel
        return outtext

class CfgParser(object):
    def __init__(self,cfgfile,log=logging.getLogger()):
        self._log=log
        self._status='NoFile'
        self._setfile(cfgfile)
    def _setfile(self,cfgfile):
        if os.path.exists(cfgfile):
            self._cfgfile=cfgfile
            self._status='FileOK'
            self._parsefile()
    def _parsefile(self):
        self._funcinfo={}
        pat_funcstart=re.compile(r'^(?P<funcname>[a-zA-Z0-9_]+)\s+\(')
        pat_funcstop=re.compile(r'^}')
        funcname=''
        with open(self._cfgfile,'rU') as cfg:
            b_infunc=False
            for line in cfg.readlines():
                line=line.rstrip()
                if b_infunc:
                    states.append(line)
                    if pat_funcstop.search(line):
                        self._funcinfo[funcname]=CfgFunc(tuple(states),self._log)
                        b_infunc=False
                else:
                    retpat=pat_funcstart.search(line)
                    if retpat:
                        states=[]
                        states.append(line)
                        b_infunc=True
                        funcname=retpat.group('funcname')
    def toDot(self):
        prefix=self._cfgfile[:-8]
        for (key,value) in self._funcinfo.items():
            with open(prefix+key+'.dot','w') as fh:
                fh.write(value.toDot())
    def __str__(self):
        outtext=''
        outtext+="Status:\t%s\n" % self._status
        outtext+="Functions:\n"+"\n".join([str(x) for x in self._funcinfo.values()])
        return outtext

def findAll():
    for (cpath,cdirs,cfiles) in os.walk('.'):
        for cfile in cfiles:
            if cfile.endswith('.cfg'):
                cfg=CfgParser(os.path.join(cpath,cfile))
                cfg.toDot()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
#    findAll()
    cfgfile='drl_info_ctl.c.012t.cfg'
    cfg=CfgParser(cfgfile)
#   cfgfile='pii_src/pii_event.c.012t.cfg'
#   cfg=CfgParser(cfgfile)
#   cfgfile='pii_src/pii_main.c.012t.cfg'
#   cfg=CfgParser(cfgfile)
    print(str(cfg))
    cfg.toDot()
