import sys
sys.path.append('./plugins')
import copy
import ply.lex as lex
import ply.yacc as yacc
import logutil

class TxtSeqParser(object):
    tokens = (
            'LBRACKET', 'RBRACKET', 'SEMI',
            'SYNCLINE','ASYNCLINE','CALLLINE','ARROW','RETURN',
            'ACTIVATE', 'MEMO',
            'TEXT',
            )
    t_LBRACKET         = r'\['
    t_RBRACKET         = r'\]'
    t_SEMI             = r';'
    t_SYNCLINE         = r'=+'
    t_ASYNCLINE        = r'\++'
    t_CALLLINE         = r'-+'
    t_ARROW            = r'>'
    t_RETURN           = r'(?i)\#return'
    t_ACTIVATE         = r'(?i)\#activate'
    t_MEMO             = r'(?i)\#memo'
    t_TEXT             = r'[^\[\];=+\->\n\#]+'
    t_ignore           = ' \t\x0c\n'
    def t_error(self,t):
        self._log.critical('T_ERROR: %s'%(t.value[0],))
        t.lexer.skip(1)
    def p_seqfile(self,p):
        '''seqfile : item
                   | seqfile item'''
        pass
    def p_item(self,p):
        '''item : trigger
                | seqfull
                | seqopen
                | seqclose'''
        pass
    def p_trigger(self,p):
        '''trigger : ACTIVATE txt SEMI
                   | ACTIVATE txt memo SEMI'''
        self._log.debug('ACTIVATE %s'%(p[2],))
        ss=SeqStatement()
        ss.setType('ACTIVATE')
        ss.setTaskDst(p[2])
        if len(p)>4:
            ss.setMemo(p[3])
        self._data.append(ss)
    def p_seqfull(self,p):
        '''seqfull : tasksrc calltype txt btxt btxtlist SEMI
                   | tasksrc calltype txt btxt btxtlist memo SEMI'''
        self._log.debug('Full:%s %s %s'%(p[1][0],p[2],p[3]))
        ss=SeqStatement()
        ss.setType('SEQUENCE')
        ss.setTaskSrc(p[1][0])
        ss.setTaskDst(p[3])
        ss.setCall(p[2])
        ss.setFunction(p[4])
        ss.setParameter(p[1][1])
        ss.setReturn(p[5])
        if len(p)>7:
            ss.setMemo(p[7])
        self._data.append(ss)
    def p_seqopen(self,p):
        '''seqopen : tasksrc calltype txt btxt SEMI
                   | tasksrc calltype txt btxt memo SEMI'''
        self._log.debug('Open:%s %s %s'%(p[1][0],p[2],p[3]))
        ss=SeqStatement()
        ss.setType('SEQUENCE_OPEN')
        ss.setTaskSrc(p[1][0])
        ss.setTaskDst(p[3])
        ss.setCall(p[2])
        ss.setFunction(p[4])
        ss.setParameter(p[1][1])
        if len(p)>6:
            ss.setMemo(p[5])
        self._data.append(ss)
    def p_seqclose(self,p):
        '''seqclose : tasksrc RETURN txt SEMI
                    | tasksrc RETURN txt memo SEMI'''
        self._log.debug('Close:%s %s %s'%(p[1][0],p[2],p[3]))
        ss=SeqStatement()
        ss.setType('SEQUENCE_CLOSE')
        ss.setTaskSrc(p[3])
        ss.setTaskDst(p[1][0])
        ss.setReturn(p[1][1])
        if len(p)>5:
            ss.setMemo(p[4])
        self._data.append(ss)
    def p_tasksrc(self,p):
        ''' tasksrc : txt
                    | txt btxtlist'''
        if len(p)>2:
            p[0]=(p[1],p[2])
        else:
            p[0]=(p[1],'')
    def p_memo(self,p):
        '''memo : MEMO btxtlist'''
        p[0]=p[2]
    def p_txt(self,p):
        '''txt : TEXT'''
        p[0]=p[1].strip()
    def p_txtlist(self,p):
        '''txtlist : txt
                   | txtlist SEMI txt'''
        if len(p)>2:
            p[0]=p[1]+p[2]+p[3]
        else:
            p[0]=p[1]
    def p_btxt(self,p):
        '''btxt : LBRACKET txt RBRACKET'''
        p[0]=p[2]
    def p_btxtlist(self,p):
        '''btxtlist : LBRACKET txtlist RBRACKET'''
        p[0]=p[2]
    def p_calltype1(self,p):
        '''calltype : CALLLINE ARROW'''
        p[0]='Call#%d'%(len(p[1]),)
    def p_calltype2(self,p):
        '''calltype : SYNCLINE ARROW'''
        p[0]='SyncCall#%d'%(len(p[1]),)
    def p_calltype3(self,p):
        '''calltype : ASYNCLINE ARROW'''
        p[0]='AsyncCall#%d'%(len(p[1]),)
    def p_error(self,p):
        self._log.critical('P_ERROR: %s'%(p,))
    def __init__(self):
        self._log=logutil.LogUtil().logger('TxtSeqParser')
        self._data=[]
        lex.lex(module=self)
        yacc.yacc(module=self)
    def parse(self,txtfile):
        enc,bomlen=logutil.guessEncode(txtfile,'cp932','cp936')
        if not enc:
            return
        with open(txtfile,'r',encoding=enc) as fh:
            data=fh.read()
        self._parse(data)
    def _parse(self,data):
        self._data=[]
        yacc.parse(data)
    def sequence(self):
        if len(self._data)>0:
            return tuple(self._data)

class SeqStatement(object):
    def __init__(self):
        self._type=''
        self._tasksrc=''
        self._taskdst=''
        self._call=''
        self._function=''
        self._parameter=''
        self._return=''
        self._memo=''
    def getType(self):
        return self._type
    def getTaskSrc(self):
        return self._tasksrc
    def getTaskDst(self):
        return self._taskdst
    def getCall(self):
        return self._call
    def getFunction(self):
        return self._function
    def getParameter(self):
        return self._parameter
    def getReturn(self):
        return self._return
    def getFunction(self):
        return self._function
    def getMemo(self):
        return self._memo
    def setType(self,typestr):
        self._type=typestr
    def setTaskSrc(self,taskstr):
        self._tasksrc=taskstr
    def setTaskDst(self,taskstr):
        self._taskdst=taskstr
    def setCall(self,calltuple):
        self._call=calltuple
    def setFunction(self,funcname):
        self._function=funcname
    def setParameter(self,parameter):
        self._parameter=parameter
    def setReturn(self,returnstr):
        self._return=returnstr
    def setMemo(self,memo):
        self._memo=memo
    def __str__(self):
        outstr='[%s] [%s] [%s]'%(self._type,self._tasksrc,self._taskdst)
        return outstr

class TxtSeqManager(object):
    def __init__(self):
        self._log=logutil.LogUtil().logger('TxtSeqManager')
        self._parser=TxtSeqParser()
        self._sequence=()
        self._tasklist=()
    def parse(self,txtfile):
        self._parser.parse(txtfile)
        self._unpack()
    def getSepLen(self,lenfunc=None):
        maxlen=0
        if self._sequence:
            if not callable(lenfunc):
                lenfunc=self.simpleLenFunc
            for seq in self._sequence:
                if seq.getType() in ('SEQUENCE_OPEN','SEQUENCE_CLOSE','SEQUENCE'):
                    for txtlist in (seq.getParameter(),seq.getFunction(),seq.getReturn()):
                        for txt in txtlist.split(';'):
                            clen=lenfunc(txt)
                            maxlen=max(maxlen,clen)
        return maxlen
    def getHeight(self):
        height=0
        if self._sequence:
            for seq in self._sequence:
                pass
        return height
    def getTaskList(self):
        return tuple(self._tasklist)
    def setTaskList(self,tasklist):
        taskset=set(tasklist)
        if taskset>set(self._tasklist):
            newtasklist=[]
            for tname in tasklist:
                if tname not in newtasklist:
                    newtasklist.append(tname)
            self._tasklist=list(newtasklist)
            return True
        else:
            return False
    def getSequence(self):
        return tuple(self._sequence)
    def simpleLenFunc(self,txt):
        retlen=0
        for ch in txt:
            if len(bytes(ch,'utf-8'))>1:
                retlen+=2
            else:
                retlen+=1
        return retlen
    def _unpack(self):
        self._sequence=[]
        self._tasklist=[]
        tskstack=[]
        seqs=self._parser.sequence()
        for seq in seqs:
            if seq.getType() in ('SEQUENCE','SEQUENCE_OPEN','SEQUENCE_CLOSE'):
                tasksrc=seq.getTaskSrc()
                taskdst=seq.getTaskDst()
                if tasksrc not in self._tasklist:
                    self._tasklist.append(tasksrc)
                if taskdst not in self._tasklist:
                    self._tasklist.append(taskdst)
                if seq.getType()=='SEQUENCE':
                    seq1=copy.copy(seq)
                    seq2=copy.copy(seq)
                    seq1.setType('SEQUENCE_OPEN')
                    seq1.setReturn('')
                    seq2.setType('SEQUENCE_CLOSE')
                    seq2.setFunction('')
                    seq2.setParameter('')
                elif seq.getType()=='SEQUENCE_OPEN':
                    if seq.getCall().startswith('AsyncCall'):
                        # AsyncCall
                        seq2=copy.copy(seq)
                        seq2.setType('SEQUENCE_CLOSE')
                        seq2.setFunction('')
                        seq2.setParameter('')
                elif seq.getType()=='SEQUENCE_CLOSE':
                    pass
                si=len(tskstack)-1
                while si>=0:
                    if tskstack[si][0]==tasksrc:
                        break
                    si-=1
                else:
                    self._log.error('UnKnown trigger')
                    return
                popcnt=len(tskstack)-1-si
                while popcnt>0:
                    xseq=tskstack.pop(-1)
                    if xseq[1]:
                        self._sequence.append(xseq[1])
                    popcnt-=1
                if seq.getType()=='SEQUENCE':
                    self._sequence.append(seq1)
                    tskstack.append((taskdst,seq2))
                elif seq.getType()=='SEQUENCE_OPEN':
                    self._sequence.append(seq)
                    if seq.getCall().startswith('AsyncCall'):
                        # AsyncCall
                        tskstack.append((taskdst,seq2))
                    else:
                        # FuncCall or SyncCall
                        tskstack.append((taskdst,None))
                elif seq.getType()=='SEQUENCE_CLOSE':
                    self._sequence.append(seq)
            elif seq.getType()=='ACTIVATE':
                taskdst=seq.getTaskDst()
                tskstack.append((taskdst,seq))
                self._sequence.append(seq)
                if taskdst not in self._tasklist:
                    self._tasklist.append(taskdst)
        while len(tskstack)>1:
            xseq=tskstack.pop(-1)
            self._sequence.append(xseq[1])

def textSequence(seqfile,txtfile):
    ts=TxtSeqManager()
    ts.parse(seqfile)
    maxlen=ts.getSepLen()
    tasklist=[(x,ts.simpleLenFunc(x)) for x in ts.getTaskList()]
    print(tasklist)
    space=''
    for seq in ts.getSequence():
        stype=seq.getType()
        if stype=='SEQUENCE_OPEN':
            space=space+'    '
            print('%s[%s]->[%s]'%(space,seq.getTaskSrc(),seq.getTaskDst()))
        elif stype=='SEQUENCE_CLOSE':
            print('%s[%s]<-[%s]'%(space,seq.getTaskSrc(),seq.getTaskDst()))
            space=space[0:-4]
        elif stype=='ACTIVATE':
            print('%s[%s]'%(stype,seq.getTaskDst()))

if __name__ == '__main__':
    textSequence('test/test01.txt','test/out01.txt')
