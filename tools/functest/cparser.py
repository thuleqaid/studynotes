import sys
import os.path
import re
import shutil
sys.path.append('./plugins')
import ply.lex as lex
from logutil import LogUtil, IOLog, IOLog1, IOLog2, IOLog3, guessEncode

class SimpleToken(object):
    def __init__(self):
        self.type=''
        self.lineno=0
        self.value=''
    def __str__(self):
        return '%s:%d:%s'%(self.type,self.lineno,self.value)

class TokenManager(object):
    '''
    folder:
        findFunctionBySrc
        parseFolder
        findFunctionByTok
    file:
        genTokenFile
        getSourceFile
        getFileTokens
        hasFunction
        getFunctionList
        getFunctionDeclarationList
        getFunctionTokens
        getFunctionCalls
        getTokensByIdx
    '''
    D_EXT_TOK='.tok'
    D_VERSION='0001' # 'xxxx' for regenerate by force
    def __init__(self):
        self._log=LogUtil().logger('TokenManager')
        self._parser=CParser()
        self._encode=['cp932','cp936']
    def setupEncodings(self,*encodings):
        for en in encodings:
            if en not in self._encode:
                self._encode.append(en)
    def parseFolder(self,srcpath,tokpath):
        if os.path.exists(srcpath) and os.path.isdir(srcpath):
            inpath=os.path.abspath(srcpath)
            for root,dirs,files in os.walk(inpath):
                for f in files:
                    ext=os.path.splitext(f)[1].upper()
                    if ext in ('.C',):
                        fullname=os.path.join(root,f)
                        relname=os.path.join(tokpath,os.path.relpath(fullname,inpath))+self.D_EXT_TOK
                        self._restoreTokFile(fullname,relname,False)
    def findFunctionBySrc(self,srcpath,tokpath,*funclist):
        '''
        @ret:{funcname:
                [{'tokfile':"xxx",
                  'srcfile':"xxx",
                  'line':(start-line-no,stop-line-no),
                  'tok':(start-tok-no,stop-tok-no),
                  'decl':"xxx"},
                  ...
                ],
             }
        '''
        outdict={}
        for func in funclist:
            outdict[func]=[]
        if os.path.exists(srcpath) and os.path.isdir(srcpath):
            inpath=os.path.abspath(srcpath)
            for root,dirs,files in os.walk(inpath):
                for f in files:
                    ext=os.path.splitext(f)[1].upper()
                    if ext in ('.C',):
                        fullname=os.path.join(root,f)
                        relname=os.path.join(tokpath,os.path.relpath(fullname,inpath))+self.D_EXT_TOK
                        self._restoreTokFile(fullname,relname,False)

                        srcfile=os.path.abspath(fullname)
                        fullname=os.path.normpath(relname)
                        funclist=self.getFunctionList(fullname)
                        for funcname in outdict.keys():
                            funcstr=':FB:%s:'%(funcname,)
                            for funcitem in funclist:
                                if funcstr in funcitem:
                                    parts=funcitem.split(':')
                                    tmpitem={'tokfile':fullname,
                                             'srcfile':srcfile,
                                             'line':(int(parts[0]),int(parts[1])),
                                             'tok':(int(parts[2]),int(parts[3])),
                                             'decl':parts[6]}
                                    outdict[funcname].append(tmpitem)
        return outdict

    def findFunctionByTok(self,tokpath,*funclist):
        '''
        @ret:{funcname:
                [{'tokfile':"xxx",
                  'srcfile':"xxx",
                  'line':(start-line-no,stop-line-no),
                  'tok':(start-tok-no,stop-tok-no),
                  'decl':"xxx"},
                  ...
                ],
             }
        '''
        outdict={}
        for func in funclist:
            outdict[func]=[]
        for root,dirs,files in os.walk(tokpath):
            for f in files:
                if f.endswith(self.D_EXT_TOK):
                    fullname=os.path.normpath(os.path.join(root,f))
                    srcfile=self.getSourceFile(fullname)
                    funclist=self.getFunctionList(fullname)
                    for funcname in outdict.keys():
                        funcstr=':FB:%s:'%(funcname,)
                        for funcitem in funclist:
                            if funcstr in funcitem:
                                parts=funcitem.split(':')
                                tmpitem={'tokfile':fullname,
                                         'srcfile':srcfile,
                                         'line':(int(parts[0]),int(parts[1])),
                                         'tok':(int(parts[2]),int(parts[3])),
                                         'decl':parts[6]}
                                outdict[funcname].append(tmpitem)
        return outdict
    def getFileTokens(self,tokfile):
        outlist=[]
        for line in self._loadTokFile(tokfile,'Token'):
            parts=line.split(':',2)
            tok=SimpleToken()
            tok.type=parts[0]
            tok.lineno=int(parts[1])
            tok.value=parts[2]
            outlist.append(tok)
        return tuple(outlist)
    def hasFunction(self,tokfile,funcname):
        funclist=self.getFunctionList(tokfile)
        funcstr=':FB:%s:'%(funcname,)
        for func in funclist:
            if funcstr in func:
                return True
        return False
    def getFunctionList(self,tokfile):
        outlist=[]
        for line in self._loadTokFile(tokfile,'Structure'):
            if ':FB:' in line:
                outlist.append(line)
        return tuple(outlist)
    def getFunctionDeclarationList(self,tokfile):
        outlist=[]
        for line in self._loadTokFile(tokfile,'Structure'):
            if ':FD:' in line:
                outlist.append(line)
        return tuple(outlist)
    def getTokensByIdx(self,tokfile,startidx,stopidx):
        tokens=self.getFileTokens(tokfile)
        toklen=len(tokens)
        if 0<=startidx<toklen and 0<=stopidx<toklen and startidx<=stopidx:
            return tuple(tokens[startidx:stopidx+1])
        else:
            return ()
    def getFunctionTokens(self,tokfile,funcname,rmcmt=False,rmif0=False):
        '''
        @ret:((funcdecl,functokens),...)
        '''
        funclist=self.getFunctionList(tokfile)
        if len(funclist)>0:
            outlist=[]
            tokens=self.getFileTokens(tokfile)
            for func in funclist:
                parts=func.split(':')
                if parts[5]==funcname:
                    outlist.append((parts[6],self._filterTokens(tokens[int(parts[2]):int(parts[3])+1],rmcmt,rmif0)))
            return tuple(outlist)
        else:
            return ()
    def getFunctionCalls(self,tokfile,funcname,excl=('memset','memcpy')):
        '''
        @ret:([funcdecl,inner-func1:call-count1,...],...)
        '''
        functokens=self.getFunctionTokens(tokfile,funcname,True,True)
        if len(functokens)>0:
            outlist=[]
            for func in functokens:
                innerfuncs=self._parser.analyzeFunction(func[1])
                outlist.append([func[0],])
                outlist[-1].extend(['%s:%d'%(x,y) for x,y in innerfuncs.items() if x not in excl])
            return tuple(outlist)
        else:
            return ()
    def getSourceFile(self,tokfile):
        return self._loadTokFile(tokfile,'SrcInfo')[0]
    def genTokenFile(self,srcfile,tokfile):
        return self._restoreTokFile(srcfile,tokfile,False)
    def _filterTokens(self,toklist,flag_rmcmt,flag_rmif0):
        if not flag_rmcmt and not flag_rmif0:
            return tuple(toklist)
        dropset=set()
        if flag_rmif0:
            pplist=[]
            level=0
            i=0
            # extract #if/else/endif
            while i<len(toklist):
                tok=toklist[i]
                if tok.type=='PREPROCESSOR':
                    j=i+1
                    while toklist[j].type!='PREPROCESSOREND':
                        j+=1
                    nextvalue=toklist[i+1].value
                    if nextvalue.startswith('if'):
                        level+=1
                        pplist.append((i,j,level,nextvalue,toklist[i+2].value))
                    elif nextvalue.startswith('el'):
                        pplist.append((i,j,level,nextvalue,toklist[i+2].value))
                    elif nextvalue.startswith('en'):
                        pplist.append((i,j,level,nextvalue,toklist[i+2].value))
                        level-=1
                    i=j
                i+=1
            # remove unnecessary tokens in the case #if 0/1
            i=0
            while i<len(pplist):
                pp=pplist[i]
                if pp[3]=='if' and pp[4] in ('0','1'):
                    level=pp[2]
                    j=i+1
                    while j<len(pplist):
                        if pplist[j][3]=='else' and pplist[j][2]==level:
                            break
                        j+=1
                    else:
                        j=-1
                    k=i+1
                    while k<len(pplist):
                        if pplist[k][3]=='endif' and pplist[k][2]==level:
                            break
                        k+=1
                    else:
                        k=-1
                    if pp[4]=='0':
                        if j<0:
                            dropset.update(range(pplist[i][0],pplist[k][1]+1))
                        else:
                            dropset.update(range(pplist[i][0],pplist[j][1]+1))
                            dropset.update(range(pplist[k][0],pplist[k][1]+1))
                    elif pp[4]=='1':
                        if j<0:
                            dropset.update(range(pplist[i][0],pplist[i][1]+1))
                            dropset.update(range(pplist[k][0],pplist[k][1]+1))
                        else:
                            dropset.update(range(pplist[i][0],pplist[i][1]+1))
                            dropset.update(range(pplist[j][0],pplist[k][1]+1))
                i+=1
        retlist=[]
        for i,tok in enumerate(toklist):
            if i not in dropset:
                if flag_rmif0:
                    if tok.type=='COMMENT':
                        pass
                    else:
                        retlist.append(tok)
                else:
                    retlist.append(tok)
        return tuple(retlist)
    def _restoreTokFile(self,srcfile,tokfile,regenerate):
        if os.path.exists(srcfile) and os.path.isfile(srcfile):
            if regenerate:
                self._log.info('Generate Token File for Source File[%s]'%(srcfile,))
                self._genTokFile(srcfile,tokfile)
            else:
                if self._checkTokFile(srcfile,tokfile):
                    self._log.info('Token File for Source File[%s] is OK'%(srcfile,))
                    pass
                else:
                    self._log.info('Source File[%s] modified, re-generate Token File'%(srcfile,))
                    self._genTokFile(srcfile,tokfile)
            return True
        else:
            self._log.warning('Source File[%s] not exists'%(srcfile,))
            return False
    def _genTokFile(self,srcfile,tokfile):
        tokens=self._parser.parse(srcfile,*self._encode)
        if tokens:
            srcstruct=self._parser.analyzeFile(tokens)
            tokpath=os.path.dirname(tokfile)
            if not os.path.exists(tokpath) or not os.path.isdir(tokpath):
                os.makedirs(tokpath)
            fh=open(tokfile,'w',encoding='utf-8')
            fh.write('@SrcInfo:\n%s\n'%(self._genFileChecksum(srcfile),))
            fh.write('@Structure:\n%s\n'%('\n'.join(srcstruct),))
            fh.write('@Token:\n')
            for tok in tokens:
                fh.write('%s:%d:%s\n'%(tok.type,tok.lineno,tok.value))
            fh.close()
    def _checkTokFile(self,srcfile,tokfile):
        ret=False
        if self.D_VERSION=='xxxx':
            ret=False
        else:
            if os.path.exists(tokfile) and os.path.isfile(tokfile):
                checksum=self._genFileChecksum(srcfile)
                curchecksum='\n'.join(self._loadTokFile(tokfile,'SrcInfo'))
                ret=(checksum==curchecksum)
        return ret
    def _genFileChecksum(self,srcfile):
        infile=os.path.abspath(srcfile)
        mtime=os.path.getmtime(infile)
        outstr='%s\nParserVersion:%s\n%d'%(infile,self.D_VERSION,mtime)
        return outstr
    def _loadTokFile(self,tokfile,partname):
        outlist=[]
        if not os.path.exists(tokfile):
            return ()
        with open(tokfile,'rU',encoding='utf-8') as fh:
            flag=False
            for line in fh.readlines():
                if line.startswith('@'):
                    if flag:
                        flag=False
                    else:
                        curpart=line[1:line.rfind(':')]
                        if curpart==partname:
                            flag=True
                else:
                    if flag:
                        outlist.append(line.strip())
        return tuple(outlist)

class CParser(object):
    # Reserved words
    _reserved = (
        'AUTO', 'BREAK', 'CASE', 'CHAR', 'CONST', 'CONTINUE', 'DEFAULT', 'DO', 'DOUBLE',
        'ELSE', 'ENUM', 'EXTERN', 'FLOAT', 'FOR', 'GOTO', 'IF', 'INT', 'LONG', 'REGISTER',
        'RETURN', 'SHORT', 'SIGNED', 'SIZEOF', 'STATIC', 'STRUCT', 'SWITCH', 'TYPEDEF',
        'UNION', 'UNSIGNED', 'VOID', 'VOLATILE', 'WHILE',
        )

    states = (
            ('preprocessor','inclusive'),
            )
    tokens = _reserved + (
        # Literals (identifier, integer constant, float constant, string constant, char const)
        'ID', 'ICONST', 'FCONST', 'SCONST', 'CCONST',
        # Operators (+,-,*,/,%,|,&,~,^,<<,>>, ||, &&, !, <, <=, >, >=, ==, !=)
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
        'OR', 'AND', 'NOT', 'XOR', 'LSHIFT', 'RSHIFT',
        'LOR', 'LAND', 'LNOT',
        'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
        # Assignment (=, *=, /=, %=, +=, -=, <<=, >>=, &=, ^=, |=)
        'EQUALS', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL', 'PLUSEQUAL', 'MINUSEQUAL',
        'LSHIFTEQUAL','RSHIFTEQUAL', 'ANDEQUAL', 'XOREQUAL', 'OREQUAL',
        # Increment/decrement (++,--)
        'PLUSPLUS', 'MINUSMINUS',
        # Structure dereference (->)
        'ARROW',
        # Conditional operator (?)
        'CONDOP',
        # Delimeters ( ) [ ] { } , . ; :
        'LPAREN', 'RPAREN',
        'LBRACKET', 'RBRACKET',
        'LBRACE', 'RBRACE',
        'COMMA', 'PERIOD', 'SEMI', 'COLON',
        # Ellipsis (...)
        'ELLIPSIS',
        # Preprocessor
        'PREPROCESSOR','PREPROCESSOREND','MULTILINE',
        'COMMENT',
        )

    # Completely ignored characters
    t_ignore           = ' \t\x0c'

    # Newlines
    def t_NEWLINE(self,t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
    def t_preprocessor_NEWLINE(self,t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
        t.lexer.begin('INITIAL')
        t.type='PREPROCESSOREND'
        t.value='@'
        self._lexstat='INITIAL'
        return t

    # Operators
    t_PLUS             = r'\+'
    t_MINUS            = r'-'
    t_TIMES            = r'\*'
    t_DIVIDE           = r'/'
    t_MOD              = r'%'
    t_OR               = r'\|'
    t_AND              = r'&'
    t_NOT              = r'~'
    t_XOR              = r'\^'
    t_LSHIFT           = r'<<'
    t_RSHIFT           = r'>>'
    t_LOR              = r'\|\|'
    t_LAND             = r'&&'
    t_LNOT             = r'!'
    t_LT               = r'<'
    t_GT               = r'>'
    t_LE               = r'<='
    t_GE               = r'>='
    t_EQ               = r'=='
    t_NE               = r'!='

    # Assignment operators
    t_EQUALS           = r'='
    t_TIMESEQUAL       = r'\*='
    t_DIVEQUAL         = r'/='
    t_MODEQUAL         = r'%='
    t_PLUSEQUAL        = r'\+='
    t_MINUSEQUAL       = r'-='
    t_LSHIFTEQUAL      = r'<<='
    t_RSHIFTEQUAL      = r'>>='
    t_ANDEQUAL         = r'&='
    t_OREQUAL          = r'\|='
    t_XOREQUAL         = r'^='

    # Increment/decrement
    t_PLUSPLUS         = r'\+\+'
    t_MINUSMINUS       = r'--'

    # ->
    t_ARROW            = r'->'

    # ?
    t_CONDOP           = r'\?'

    # Delimeters
    t_LPAREN           = r'\('
    t_RPAREN           = r'\)'
    t_LBRACKET         = r'\['
    t_RBRACKET         = r'\]'
    t_LBRACE           = r'\{'
    t_RBRACE           = r'\}'
    t_COMMA            = r','
    t_PERIOD           = r'\.'
    t_SEMI             = r';'
    t_COLON            = r':'
    t_ELLIPSIS         = r'\.\.\.'

    # Identifiers and reserved words

    def t_ID(self,t):
        r'[A-Za-z_][\w_]*'
        t.type = self._reserved_map.get(t.value,"ID")
        return t

    # Integer literal
    t_ICONST = r'(0x)?\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'

    # Floating literal
    t_FCONST = r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'

    # String literal
    t_SCONST = r'\"([^\\\n]|(\\.))*?\"'

    # Character constant 'c' or L'c'
    t_CCONST = r'(L)?\'([^\\\n]|(\\.))*?\''

    # Comments
    def t_COMMENT(self,t):
        r'(/\*(.|\n)*?\*/|//.*)'
        lncnt = t.value.count('\n')
        t.lexer.lineno += lncnt
        if lncnt>0:
            t.value=t.value.replace('\n','\\n\\')
        return t

    def t_PREPROCESSOR(self,t):
        r'\#'
        t.lexer.begin('preprocessor')
        self._lexstat='preprocessor'
        return t
    def t_preprocessor_MULTILINE(self,t):
        r'\\[ \t\0c]*\n'
        t.lexer.lineno += 1

    def t_error(self,t):
        self._log.warning("Illegal character %s" % repr(t.value[0]))
        t.lexer.skip(1)

    def __init__(self):
        self._log=LogUtil().logger('cparse')
        self._reserved_map = { }
        for r in self._reserved:
            self._reserved_map[r.lower()] = r

    def parse(self,fname,*encode):
        # load source file
        enc,bomlen=guessEncode(fname,*encode)
        if not enc:
            self._log.critical('No Valid Encoding')
            return
        self._log.info('parse file: filename=%s encoding=%s'%(fname,enc))
        fh=open(fname,'rU',encoding=enc)
        data=fh.read()
        fh.close()
        # parse data
        return self._parse(data)

    def _parse(self,statements):
        self._lexer=lex.lex(module=self)
        self._lexer.input(statements)
        self._lexstat='INITIAL'
        tokens=[]
        while True:
            tok=self._lexer.token()
            if not tok:
                break
            tokens.append(tok)
        if self._lexstat=='preprocessor':
            tok=SimpleToken()
            tok.lineno = tokens[-1].lineno
            tok.type='PREPROCESSOREND'
            tok.value='@'
            tokens.append(tok)
        return tuple(tokens)

    def _nextTokenIdx(self,tokens,curidx):
        nextidx=curidx+1
        while nextidx<len(tokens):
            if tokens[nextidx].type!='COMMENT':
                break
            nextidx+=1
        return nextidx
    @IOLog2
    def analyzeFile(self,tokens):
        toklen=len(tokens)
        ifdef=[] # lineno:tokenno:#xxx:value / lineno:tokenno:sts:#level:{level:[level:(level
        idx=0
        headidx=0
        if tokens[headidx].type=='COMMENT':
            headidx=self._nextTokenIdx(tokens,headidx)
        self._log.debug('->head_token:%d'%(headidx,))
        sts_str=('Normal','VariableInitial','FunctionBody')
        sts,stslevel1=0,0 # sts:0-Normal,1-GlobalVarInit,2-FunctionBody
        level0,level1,level2,level3=0,0,0,0
        funcname=''
        oldheadidx=0
        funcline=0
        funcdecl=''
        varname=''
        varline=0
        outlist=[]
        while idx<toklen:
            if tokens[idx].type=='PREPROCESSOR':
                if headidx!=idx:
                    flag_instatement=True
                else:
                    flag_instatement=False
                idx2=self._nextTokenIdx(tokens,idx)
                while tokens[idx2].type!='PREPROCESSOREND':
                    idx2=self._nextTokenIdx(tokens,idx2)
                outlist.append('%d:%d:%d:%d:PP:%s'%(tokens[idx].lineno,tokens[idx2].lineno,idx,idx2,tokens[idx+1].value))
                self._log.debug('Token[%d-%d/%d]: lineno=%d-%d PP-type=%s InStatement=%s'%(idx,idx2,toklen,tokens[idx].lineno,tokens[idx2].lineno,tokens[idx+1].value,str(flag_instatement)))
                if tokens[self._nextTokenIdx(tokens,idx)].value.startswith('if'):
                    level0+=1
                    ifdef.append('%d:%d:#%s'%(tokens[idx].lineno,idx,':'.join([t.value for t in tokens[idx+1:idx2] if t.type!='COMMENT'])))
                    idx=idx2
                    ifdef.append('%d:%d:%d:%d:%d:%d:%d'%(tokens[idx].lineno,idx,sts,level0,level1,level2,level3))
                    self._log.debug('->#:%d {}:%d []:%d ():%d'%(level0,level1,level2,level3))
                elif tokens[self._nextTokenIdx(tokens,idx)].value.startswith('el'):
                    ifdef.append('%d:%d:#%s'%(tokens[idx].lineno,idx,':'.join([t.value for t in tokens[idx+1:idx2] if t.type!='COMMENT'])))
                    idx=idx2
                    idx2=len(ifdef)-2
                    cnt=1
                    while idx2>=0:
                        if ':#en' in ifdef[idx2]:
                            cnt+=1
                        elif ':#if' in ifdef[idx2]:
                            cnt-=1
                            if cnt<=0:
                                parts=ifdef[idx2+1].split(':')
                                sts=int(parts[2])
                                level1=int(parts[4])
                                level2=int(parts[5])
                                level3=int(parts[6])
                                break
                        idx2-=1
                    ifdef.append('%d:%d:%d:%d:%d:%d:%d'%(tokens[idx].lineno,idx,sts,level0,level1,level2,level3))
                    self._log.debug('->#:%d {}:%d []:%d ():%d'%(level0,level1,level2,level3))
                elif tokens[self._nextTokenIdx(tokens,idx)].value.startswith('end'):
                    level0-=1
                    ifdef.append('%d:%d:#%s'%(tokens[idx].lineno,idx,':'.join([t.value for t in tokens[idx+1:idx2] if t.type!='COMMENT'])))
                    idx=idx2
                    ifdef.append('%d:%d:%d:%d:%d:%d:%d'%(tokens[idx].lineno,idx,sts,level0,level1,level2,level3))
                    self._log.debug('->#:%d {}:%d []:%d ():%d'%(level0,level1,level2,level3))
                else:
                    idx=idx2
                if not flag_instatement:
                    # #xxx
                    headidx=self._nextTokenIdx(tokens,idx)
                    self._log.debug('->head_token:%d'%(headidx,))
            else:
                self._log.debug('Token[%d/%d]: type=%s lineno=%d value=%s status=%s'%(idx,toklen,tokens[idx].type,tokens[idx].lineno,tokens[idx].value,sts_str[sts]))
                if tokens[idx].type=='SEMI':
                    if level3>0:
                        # for(...;...;...)
                        self._log.debug('->for(...;...;...)')
                    else:
                        if sts==0:
                            idx2=headidx
                            while idx2<idx:
                                if tokens[idx2].type=='LPAREN':
                                    # function declare
                                    self._log.debug('->function declare')
                                    funcdecl=' '.join([x.value for x in tokens[headidx:idx] if x.type!='COMMENT'])
                                    while idx2>headidx:
                                        if tokens[idx2].type=='ID':
                                            outlist.append('%d:%d:%d:%d:FD:%s:%s'%(tokens[headidx].lineno,tokens[idx].lineno,headidx,idx,tokens[idx2].value,funcdecl))
                                            break
                                        idx2-=1
                                    break
                                idx2+=1
                            else:
                                # variable declare
                                self._log.debug('->variable declare')
                                cnt=0
                                idx2=idx
                                while idx2>headidx:
                                    if tokens[idx2].type in ('LPAREN','LBRACKET'):
                                        cnt-=1
                                    elif tokens[idx2].type in ('RPAREN','RBRACKET'):
                                        cnt+=1
                                    if cnt==0 and tokens[idx2].type=='ID':
                                        outlist.append('%d:%d:%d:%d:VD:%s'%(tokens[headidx].lineno,tokens[idx].lineno,headidx,idx,tokens[idx2].value))
                                        break
                                    idx2-=1
                        elif sts==1:
                            sts=0
                            ifdef.append('%d:%d:%d:%d:%d:%d:%d'%(tokens[idx].lineno,idx,sts,level0,level1,level2,level3))
                            outlist.append('%d:%d:%d:%d:VI:%s'%(tokens[varline].lineno,tokens[idx].lineno,varline,idx,varname))
                        # statement ends
                        headidx=self._nextTokenIdx(tokens,idx)
                        self._log.debug('->head_token:%d'%(headidx,))
                elif tokens[idx].type=='COLON':
                    # label: / case xxx:
                    headidx=self._nextTokenIdx(tokens,idx)
                    self._log.debug('->head_token:%d'%(headidx,))
                elif tokens[idx].type=='LBRACE':
                    if sts==0:
                        # left brace
                        oldheadidx=headidx
                        funcdecl=' '.join([x.value for x in tokens[oldheadidx:idx] if x.type!='COMMENT'])
                        headidx=self._nextTokenIdx(tokens,idx)
                        self._log.debug('->head_token:%d'%(headidx,))
                        sts=2
                        stslevel1=level1
                        cnt=0
                        idx2=idx-1
                        # find '(' besiding the function name
                        while idx2>=oldheadidx:
                            if tokens[idx2].type=='LPAREN':
                                cnt-=1
                                if cnt<=0:
                                    break
                            elif tokens[idx2].type=='RPAREN':
                                cnt+=1
                            idx2-=1
                        # find function name
                        while idx2>=oldheadidx:
                            if tokens[idx2].type=='ID':
                                funcname=tokens[idx2].value
                                break
                            idx2-=1
                        # find function start line, in case linenos of function type and function name are different
                        funcline=oldheadidx
                    elif sts==1:
                        # { in the var's initial
                        pass
                    elif sts==2:
                        # left brace
                        oldheadidx=headidx
                        headidx=self._nextTokenIdx(tokens,idx)
                        self._log.debug('->head_token:%d'%(headidx,))
                    level1+=1
                    ifdef.append('%d:%d:%d:%d:%d:%d:%d'%(tokens[idx].lineno,idx,sts,level0,level1,level2,level3))
                    self._log.debug('->#:%d {}:%d []:%d ():%d'%(level0,level1,level2,level3))
                elif tokens[idx].type=='RBRACE':
                    if sts==0:
                        self._log.error('Unexpected } at Line:%d'%(tokens[idx].lineno,))
                    elif sts==1:
                        # } in the var's initial
                        pass
                    elif sts==2:
                        # right brace
                        headidx=self._nextTokenIdx(tokens,idx)
                        self._log.debug('->head_token:%d'%(headidx,))
                        if level1-1==stslevel1:
                            sts=0
                            # function ends
                            outlist.append('%d:%d:%d:%d:FB:%s:%s'%(tokens[funcline].lineno,tokens[idx].lineno,funcline,idx,funcname,funcdecl))
                    level1-=1
                    ifdef.append('%d:%d:%d:%d:%d:%d:%d'%(tokens[idx].lineno,idx,sts,level0,level1,level2,level3))
                    self._log.debug('->#:%d {}:%d []:%d ():%d'%(level0,level1,level2,level3))
                elif tokens[idx].type=='LBRACKET':
                    level2+=1
                    ifdef.append('%d:%d:%d:%d:%d:%d:%d'%(tokens[idx].lineno,idx,sts,level0,level1,level2,level3))
                    self._log.debug('->#:%d {}:%d []:%d ():%d'%(level0,level1,level2,level3))
                elif tokens[idx].type=='RBRACKET':
                    level2-=1
                    ifdef.append('%d:%d:%d:%d:%d:%d:%d'%(tokens[idx].lineno,idx,sts,level0,level1,level2,level3))
                    self._log.debug('->#:%d {}:%d []:%d ():%d'%(level0,level1,level2,level3))
                elif tokens[idx].type=='LPAREN':
                    level3+=1
                    ifdef.append('%d:%d:%d:%d:%d:%d:%d'%(tokens[idx].lineno,idx,sts,level0,level1,level2,level3))
                    self._log.debug('->#:%d {}:%d []:%d ():%d'%(level0,level1,level2,level3))
                elif tokens[idx].type=='RPAREN':
                    level3-=1
                    ifdef.append('%d:%d:%d:%d:%d:%d:%d'%(tokens[idx].lineno,idx,sts,level0,level1,level2,level3))
                    self._log.debug('->#:%d {}:%d []:%d ():%d'%(level0,level1,level2,level3))
                else:
                    if sts==0:
                        if tokens[idx].type=='EQUALS':
                            sts=1
                            ifdef.append('%d:%d:%d:%d:%d:%d:%d'%(tokens[idx].lineno,idx,sts,level0,level1,level2,level3))
                            varline=headidx
                            idx2=idx-1
                            cnt=0
                            while idx2>headidx:
                                if tokens[idx2].type=='RBRACKET':
                                    cnt+=1
                                elif tokens[idx2].type=='LBRACKET':
                                    cnt-=1
                                if cnt==0 and tokens[idx2].type=='ID':
                                    varname=tokens[idx2].value
                                    break
                                idx2-=1
            idx=self._nextTokenIdx(tokens,idx)
        return tuple(outlist)
    @IOLog2
    def analyzeFunction(self,tokens):
        statements=self.splitFunction(0,tokens,0,len(tokens))
        funcs={}
        # analyze functions called by current function
        for x in statements:
            if x[0]>0:
                for yi in range(len(x[1])-1):
                    if x[1][yi].type=='ID' and x[1][yi+1].type=='LPAREN':
                        funcname=x[1][yi].value
                        if funcname not in funcs:
                            funcs[funcname]=0
                        funcs[funcname]+=1
        self._log.debug('inner function(s):%s'%(str(funcs),))
        return funcs
    def analyzeFunction2(self,tokens):
        statements=self.splitFunction(0,tokens,0,len(tokens))
        funcs={}
        paramdict={}
        autovardict={}
        varsset=set()
        typelist=( 'AUTO', 'CHAR', 'CONST', 'DOUBLE',
                   'ENUM', 'EXTERN', 'FLOAT', 'INT', 'LONG', 'REGISTER',
                   'SHORT', 'SIGNED', 'STATIC', 'STRUCT',
                   'UNION', 'UNSIGNED', 'VOID', 'VOLATILE',
                   'ID')
        assignlist=('EQUALS', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL', 'PLUSEQUAL', 'MINUSEQUAL',
                    'LSHIFTEQUAL','RSHIFTEQUAL', 'ANDEQUAL', 'XOREQUAL', 'OREQUAL')
        for statement in statements:
            # analyze functions called by current function
            if statement[0]>0:
                for yi in range(len(statement[1])-1):
                    if statement[1][yi].type=='ID' and statement[1][yi+1].type=='LPAREN':
                        funcname=statement[1][yi].value
                        if funcname not in funcs:
                            funcs[funcname]=0
                        funcs[funcname]+=1
            # analyze variables
            if statement[0]<1:
                # function declaration
                yi=2
                while yi<len(statement[1]) and statement[1][yi].type!='LPAREN':
                    yi+=1
                yj=len(statement[1])-1
                while yj>yi and statement[1][yj].type!='RPAREN':
                    yj-=1
                # function name and return type
                funcname=statement[1][yi-1].value
                functype=' '.join([t.value for t in statement[1][0:yi-1]])
                # function's parameters
                yi=yi+1
                while yi<yj:
                    yk=yi+1
                    while yk<yj and statement[1][yk].type!='COMMA':
                        yk+=1
                    if yi==yk-1:
                        # void
                        break
                    else:
                        yl=yi
                        while yl<yk and statement[1][yl].type in typelist:
                            yl+=1
                        if statement[1][yl].type=='TIMES':
                            paramtype=' '.join([t.value for t in statement[1][yi:yl]])
                        else:
                            yl-=1
                            paramtype=' '.join([t.value for t in statement[1][yi:yl]])
                        level1,level2,level3=0,0,0
                        varstart,varstop=yl,0
                        assignpos,pointlevel,arraylevel=0,0,0
                        while yl<yk:
                            if statement[1][yl].type=='LBRACE':
                                level1+=1
                            elif statement[1][yl].type=='RBRACE':
                                level1-=1
                            elif statement[1][yl].type=='LBRACKET':
                                if level1==0 and level2==0 and level3==0:
                                    arraylevel+=1
                                    if varstop<=0:
                                        varstop=yl
                                level2+=1
                            elif statement[1][yl].type=='RBRACKET':
                                level2-=1
                            elif statement[1][yl].type=='LPAREN':
                                level3+=1
                            elif statement[1][yl].type=='RPAREN':
                                level3-=1
                            elif statement[1][yl].type=='TIMES':
                                if level1==0 and level2==0 and level3==0:
                                    pointlevel+=1
                                    varstart=yl+1
                            yl+=1
                        if varstop<=0:
                            varstop=yk
                        paramname=' '.join([t.value for t in statement[1][varstart:varstop]])
                        paramdict[paramname]=(paramtype,pointlevel,arraylevel)
                    yi=yk+1
            else:
                # function body
                if len(statement[1])>1:
                    if statement[1][0].type=='PREPROCESSOR':
                        statetype=0 # pre-process
                    elif statement[1][0].type in typelist and (statement[1][1].type in typelist or statement[1][1].type=='TIMES'):
                        statetype=1 # variable definition
                    else:
                        statetype=2 # statement
                else:
                    statetype=2
                if statetype==1:
                    # variable's type
                    yi=0
                    while yi<len(statement[1])-1 and statement[1][yi].type in typelist:
                        yi+=1
                    if statement[1][yi].type=='TIMES':
                        vartype=' '.join([t.value for t in statement[1][0:yi]])
                    else:
                        vartype=' '.join([t.value for t in statement[1][0:yi-1]])
                        yi-=1
                    # variable's name
                    while yi<len(statement[1])-1:
                        level1,level2,level3=0,0,0
                        yj=yi
                        varstart,varstop=yi,0
                        assignpos,pointlevel,arraylevel=0,0,0
                        while yj<len(statement[1])-1:
                            if statement[1][yj].type=='LBRACE':
                                level1+=1
                            elif statement[1][yj].type=='RBRACE':
                                level1-=1
                            elif statement[1][yj].type=='LBRACKET':
                                if level1==0 and level2==0 and level3==0:
                                    arraylevel+=1
                                    if varstop<=0:
                                        varstop=yj
                                level2+=1
                            elif statement[1][yj].type=='RBRACKET':
                                level2-=1
                            elif statement[1][yj].type=='LPAREN':
                                level3+=1
                            elif statement[1][yj].type=='RPAREN':
                                level3-=1
                            elif statement[1][yj].type=='COMMA':
                                if level1==0 and level2==0 and level3==0:
                                    break
                            elif statement[1][yj].type=='TIMES':
                                if level1==0 and level2==0 and level3==0:
                                    pointlevel+=1
                                    if assignpos<=0:
                                        varstart=yj+1
                            elif statement[1][yj].type in assignlist:
                                assignpos=yj # initialize in the definition
                            yj+=1
                        if assignpos>0:
                            if varstop<=0:
                                varstop=assignpos
                            varname=' '.join([t.value for t in statement[1][varstart:varstop]])
                            varvalue=' '.join([t.value for t in statement[1][assignpos:yj]])
                        else:
                            if varstop<=0:
                                varstop=yj
                            varname=' '.join([t.value for t in statement[1][varstart:varstop]])
                            varvalue=None
                        autovardict[varname]=(vartype,pointlevel,arraylevel)
                        varsset.update(self._countVariable(statement[1][yi:yj+1]))
                        yi=yj+1
                elif statetype==2:
                    if statement[1][0].type=='GOTO':
                        # goto
                        pass
                    elif len(statement[1])>1 and statement[1][1].type=='COLON':
                        # label
                        pass
                    else:
                        varsset.update(self._countVariable(statement[1]))
                else:
                    # pre-processor
                    pass
        globalvars=set()
        globalmacros=set()
        for varname in tuple(varsset):
            if varname in funcs:
                pass
            elif varname in paramdict:
                pass
            elif varname in autovardict:
                pass
            elif varname.upper()==varname:
                globalmacros.add(varname)
            else:
                globalvars.add(varname)
        print(funcs)
        print(paramdict)
        print(autovardict)
        print(globalmacros)
        print(globalvars)
        return funcs
    def _countVariable(self,toklist):
        outset=set()
        idlen=0
        skiplen=0
        yi=0
        while yi<len(toklist):
            y=toklist[yi]
            if y.type=='ID':
                if idlen%2==0:
                    idlen+=1
                else:
                    idlen=1
                    skiplen=0
            elif y.type in ('ARROW','PERIOD'):
                if idlen%2==1:
                    idlen+=1
            elif y.type=='LBRACKET':
                level1,level2,level3=0,1,0
                yj=yi+1
                while yj<len(toklist) and toklist[yj].type!='RBRACKET':
                    yj+=1
                skiplen=yj-yi+1
                outset.update(self._countVariable(toklist[yi+1:yj]))
                yi=yj
            else:
                if idlen>0:
                    outset.add(toklist[yi-idlen-skiplen].value)
                idlen=0
                skiplen=0
            yi+=1
        if idlen>0:
            outset.add(toklist[yi-idlen-skiplen].value)
        return tuple(outset)
    @IOLog
    def splitFunction(self,level,toklist,startidx,count):
        if count<=0:
            return (level,())
        idx=startidx
        maxidx=startidx+count
        outlist=[]
        if level==0:
            # out of function
            level1,level2,level3=0,0,0
            idx21=-1
            while idx<maxidx:
                if toklist[idx].type=='LBRACE':
                    level1+=1
                    if idx21<0 and level1==1 and level2==0 and level3==0:
                        outlist.append((level,[t for t in toklist[startidx:idx] if t.type!='COMMENT']))
                        idx21=idx+1
                        while idx21<maxidx and toklist[idx21].type=='COMMENT':
                            idx21+=1
                elif toklist[idx].type=='RBRACE':
                    level1-=1
                    if level1==0 and level2==0 and level3==0 and idx21>0:
                        idx22=idx-1
                        while idx22>=startidx and toklist[idx22].type=='COMMENT':
                            idx22-=1
                        outlist.extend(self.splitFunction(level+1,toklist,idx21,idx22-idx21+1))
                        break
                elif toklist[idx].type=='LBRACKET':
                    level2+=1
                elif toklist[idx].type=='RBRACKET':
                    level2-=1
                elif toklist[idx].type=='LPAREN':
                    level3+=1
                elif toklist[idx].type=='RPAREN':
                    level3-=1
                idx+=1
        else:
            # in function
            while idx<maxidx:
                headidx=idx
                level1,level2,level3=0,0,0
                idx2=idx+1
                while idx2<maxidx and toklist[idx2].type=='COMMENT':
                    idx2+=1
                if toklist[idx].type=='PREPROCESSOR':
                    while idx<maxidx and toklist[idx].type!='PREPROCESSOREND':
                        idx+=1
                    outlist.append((level,[t for t in toklist[headidx:idx+1] if t.type!='COMMENT']))
                    pass
                elif toklist[idx].type in ('IF','FOR','WHILE','SWITCH','ELSE'):
                    # move idx after (condition)
                    if toklist[idx].type=='ELSE' and toklist[idx2].type!='IF':
                        # no need to move idx
                        pass
                    else:
                        while idx<maxidx:
                            if toklist[idx].type=='LBRACE':
                                level1+=1
                            elif toklist[idx].type=='RBRACE':
                                level1-=1
                            elif toklist[idx].type=='LBRACKET':
                                level2+=1
                            elif toklist[idx].type=='RBRACKET':
                                level2-=1
                            elif toklist[idx].type=='LPAREN':
                                level3+=1
                            elif toklist[idx].type=='RPAREN':
                                level3-=1
                                if level1==0 and level2==0 and level3==0:
                                    break
                            idx+=1
                    outlist.append((level,[t for t in toklist[headidx:idx+1] if t.type!='COMMENT']))

                    idx2=idx+1
                    while idx2<maxidx and toklist[idx2].type=='COMMENT':
                        idx2+=1
                    if toklist[idx2].type=='LBRACE':
                        # statements block
                        idx21=idx2+1
                        while idx21<maxidx and toklist[idx21].type=='COMMENT':
                            idx21+=1
                        while idx2<maxidx:
                            if toklist[idx2].type=='LBRACE':
                                level1+=1
                            elif toklist[idx2].type=='RBRACE':
                                level1-=1
                                if level1==0 and level2==0 and level3==0:
                                    idx=idx2
                                    idx22=idx2-1
                                    while idx22>=0 and toklist[idx22].type=='COMMENT':
                                        idx22-=1
                                    break
                            elif toklist[idx2].type=='LBRACKET':
                                level2+=1
                            elif toklist[idx2].type=='RBRACKET':
                                level2-=1
                            elif toklist[idx2].type=='LPAREN':
                                level3+=1
                            elif toklist[idx2].type=='RPAREN':
                                level3-=1
                            idx2+=1
                    else:
                        # one statement line
                        idx21=idx2
                        while idx2<maxidx:
                            if toklist[idx2].type=='LBRACE':
                                level1+=1
                            elif toklist[idx2].type=='RBRACE':
                                level1-=1
                            elif toklist[idx2].type=='LBRACKET':
                                level2+=1
                            elif toklist[idx2].type=='RBRACKET':
                                level2-=1
                            elif toklist[idx2].type=='LPAREN':
                                level3+=1
                            elif toklist[idx2].type=='RPAREN':
                                level3-=1
                            elif toklist[idx2].type=='SEMI':
                                if level1==0 and level2==0 and level3==0:
                                    idx=idx2
                                    idx22=idx2
                                    break
                            idx2+=1
                    outlist.extend(self.splitFunction(level+1,toklist,idx21,idx22-idx21+1))
                else:
                    while idx<maxidx:
                        if toklist[idx].type=='LBRACE':
                            level1+=1
                        elif toklist[idx].type=='RBRACE':
                            level1-=1
                        elif toklist[idx].type=='LBRACKET':
                            level2+=1
                        elif toklist[idx].type=='RBRACKET':
                            level2-=1
                        elif toklist[idx].type=='LPAREN':
                            level3+=1
                        elif toklist[idx].type=='RPAREN':
                            level3-=1
                        elif toklist[idx].type in ('SEMI','COLON'):
                            if level1==0 and level2==0 and level3==0:
                                outlist.append((level,[t for t in toklist[headidx:idx+1] if t.type!='COMMENT']))
                                break
                        idx+=1
                idx+=1
        return tuple(outlist)

def getFuncInfo(srcpath,tokpath,*funclist):
    fdict=tokenmanager.findFunctionBySrc(srcpath,tokpath,*funclist)
    for funcname in list(fdict.keys()):
        for finfo in fdict[funcname]:
            fcalls=tokenmanager.getFunctionCalls(finfo['tokfile'],funcname)
            for fc in fcalls:
                fdecl=fc.pop(0)
                if fdecl==finfo['decl']:
                    finfo['calls']=tuple(fc)
    return fdict

def getTestFuncInfo(srcpath,tokpath,funcname):
    fdict=getFuncInfo(srcpath,tokpath,funcname)
    for finfo in fdict[funcname]:
        finfo['calldecl']=[]
        calllist=[]
        for funccall in finfo['calls']:
            cfunc=funccall[0:funccall.find(':')]
            calllist.append(cfunc)
        cfdict=getFuncInfo(srcpath,tokpath,*calllist)
        for cfuncname in cfdict.keys():
            if len(cfdict[cfuncname])>0:
                finfo['calldecl'].extend([x['decl'] for x in cfdict[cfuncname]])
    return fdict

def dummyFile(tokfile,info):
    '''
    @param info:{'FB':'target_func_name',
                 'DMY':(('funcname','dmy1funcname','dmy2funcname',...),
                        ('funcname','dmy1funcname','dmy2funcname',...),
                       ),
                }
    '''
    if not os.path.exists(tokfile):
        return
    log=LogUtil().logger('TokenManager')
    fblines=[]
    for line in tokenmanager._loadTokFile(tokfile,'Structure'):
        parts=line.split(':')
        if parts[4]=='FB':
            if parts[5]==info.get('FB',''):
                fblines.append((int(parts[0]),int(parts[1]),parts[5],int(parts[2]),int(parts[3])))
    log.debug('fblines:%s'%(str(sorted(fblines)),))

    # find dummy functions in the function body
    dmyinfo={}
    dmylines=set()
    if 'DMY' in info:
        for fb in fblines:
            tokens=tokenmanager.getTokensByIdx(tokfile,fb[3],fb[4])
            for tok in tokens:
                if tok.type=='ID':
                    for didx,dmy in enumerate(info['DMY']):
                        if len(dmy)>1 and dmy[0]==tok.value:
                            if dmy[0] not in dmyinfo:
                                dmyinfo[dmy[0]]=[0,didx]
                            dmyinfo[dmy[0]].append(tok.lineno)
                            dmylines.add(tok.lineno)
        log.debug('dummy function replace lines:%s'%(str(dmylines),))

    srcfile=tokenmanager.getSourceFile(tokfile)
    if not os.path.exists(srcfile):
        return
    enc,bomlen=guessEncode(srcfile,'cp932','cp936')
    fh=open(srcfile,'rU',encoding=enc)
    fidx=0
    fflag=True # used for the case #if ABC function-body{} #else function-body{} #endif
    outline=''
    for idx,line in enumerate(fh.readlines()):
        while fidx<len(fblines) and fblines[fidx][1]<idx+1:
            fidx+=1
            fflag=True
        if fidx<len(fblines) and fblines[fidx][0]<=idx+1<=fblines[fidx][1]:
            if fflag:
                # reset dummy functions' count
                fflag=False
                for dk in dmyinfo.keys():
                    dmyinfo[dk][0]=0
            if idx+1 in dmylines:
                # replace dummy function
                for dk in dmyinfo.keys():
                    repcnt=dmyinfo[dk][2:].count(idx+1)
                    while repcnt>0:
                        oldstr=dk
                        if dmyinfo[dk][0]>=len(info['DMY'][dmyinfo[dk][1]])-1:
                            newstr=info['DMY'][dmyinfo[dk][1]][-1]
                        else:
                            newstr=info['DMY'][dmyinfo[dk][1]][dmyinfo[dk][0]+1]
                            dmyinfo[dk][0]+=1
                        line=re.sub(r'\b%s\b'%(oldstr,),newstr,line,1)
                        repcnt-=1
        outline+=line
    fh.close()
    newfile=srcfile+'.org'
    if not os.path.exists(newfile):
        os.rename(srcfile,newfile)
    fout=open(srcfile,'w',encoding=enc)
    fout.write(outline)
    fout.close()
    return ''

def unDummyFolder(srcpath):
    for root,dirs,files in os.walk(srcpath):
        for fname in files:
            if fname.upper().endswith('.ORG'):
                orgname=os.path.splitext(fname)[0]
                orgfullname=os.path.join(root,orgname)
                if os.path.exists(orgfullname) and os.path.isfile(orgfullname):
                    os.remove(orgfullname)
                os.rename(os.path.join(root,fname),orgfullname)

def copyFile(tokfile,info):
    '''
    @param info:{'VI':(),
                 'VD':(),
                 'FD':(),
                 'FB':(),
                 'DMY':(('funcname','dmy1funcname','dmy2funcname',...),
                        ('funcname','dmy1funcname','dmy2funcname',...),
                       ),
                 'OF':"out file path", # if not set, return a list of lines
                }
    '''
    log=LogUtil().logger('TokenManager')
    lines=set()
    pplines=[]
    fblines=[]
    for line in tokenmanager._loadTokFile(tokfile,'Structure'):
        parts=line.split(':')
        if parts[4]=='PP':
            if parts[5]!='define':
                if 'if' in parts[5] or 'el' in parts[5] or 'end' in parts[5]:
                    pplines.append((int(parts[0]),int(parts[1]),parts[5]))
                else:
                    lines.update(list(range(int(parts[0]),int(parts[1])+1)))
        else:
            if parts[5] in info.get(parts[4],()):
                lines.update(list(range(int(parts[0]),int(parts[1])+1)))
                if parts[4]=='FB':
                    fblines.append((int(parts[0]),int(parts[1]),parts[5],int(parts[2]),int(parts[3])))
    lines=list(lines)
    log.debug('source:%s'%(str(sorted(lines)),))
    log.debug('fblines:%s'%(str(sorted(fblines)),))
    log.debug('pplines:%s'%(str(sorted(pplines)),))

    # remove useless #if/else/endif
    levelstack=[]
    pairs=[]
    for idx,pitem in enumerate(pplines):
        if pitem[2].startswith('if'):
            levelstack.append(idx)
        elif pitem[2].startswith('end'):
            oidx=levelstack.pop(-1)
            pairs.append((oidx,idx))
    exset=set()
    for pair in pairs:
        for i in range(pplines[pair[0]][0],pplines[pair[1]][1]+1):
            if i in lines:
                break
        else:
            # no source in the range of if/else/endif
            for i in range(pair[0],pair[1]+1):
                exset.add(i)
    for ex in reversed(sorted(list(exset))):
        pplines.pop(ex)
    log.debug('modified pplines:%s'%(str(sorted(pplines)),))

    # find dummy functions in the function body
    dmyinfo={}
    dmylines=set()
    if 'DMY' in info:
        for fb in fblines:
            tokens=tokenmanager.getTokensByIdx(tokfile,fb[3],fb[4])
            for tok in tokens:
                if tok.type=='ID':
                    for didx,dmy in enumerate(info['DMY']):
                        if len(dmy)>1 and dmy[0]==tok.value:
                            if dmy[0] not in dmyinfo:
                                dmyinfo[dmy[0]]=[0,didx]
                            dmyinfo[dmy[0]].append(tok.lineno)
                            dmylines.add(tok.lineno)
        log.debug('dummy function replace lines:%s'%(str(dmylines),))

    srcfile=tokenmanager.getSourceFile(tokfile)
    enc,bomlen=guessEncode(srcfile,'cp932','cp936')
    fh=open(srcfile,'rU',encoding=enc)
    pidx=0
    fidx=0
    fflag=True # used for the case #if ABC function-body{} #else function-body{} #endif
    outline=''
    for idx,line in enumerate(fh.readlines()):
        while pidx<len(pplines) and pplines[pidx][1]<idx+1:
            pidx+=1
        while fidx<len(fblines) and fblines[fidx][1]<idx+1:
            fidx+=1
            fflag=True
        if pidx<len(pplines) and pplines[pidx][0]<=idx+1<=pplines[pidx][1]:
            outline+=line
        elif fidx<len(fblines) and fblines[fidx][0]<=idx+1<=fblines[fidx][1]:
            if fflag:
                # reset dummy functions' count
                fflag=False
                for dk in dmyinfo.keys():
                    dmyinfo[dk][0]=0
            if idx+1 in dmylines:
                # replace dummy function
                for dk in dmyinfo.keys():
                    repcnt=dmyinfo[dk][2:].count(idx+1)
                    while repcnt>0:
                        oldstr=dk
                        if dmyinfo[dk][0]>=len(info['DMY'][dmyinfo[dk][1]])-1:
                            newstr=info['DMY'][dmyinfo[dk][1]][-1]
                        else:
                            newstr=info['DMY'][dmyinfo[dk][1]][dmyinfo[dk][0]+1]
                            dmyinfo[dk][0]+=1
                        line=re.sub(r'\b%s\b'%(oldstr,),newstr,line,1)
                        repcnt-=1
            outline+=line
        elif idx+1 in lines:
            outline+=line
    fh.close()
    outfile=info.get('OF','')
    if outfile:
        fout=open(outfile,'w',encoding=enc)
        fout.write(outline)
        fout.close()
        return ''
    else:
        return tuple(outline)
tokenmanager=TokenManager()

if __name__ == '__main__':
    #srcpath='D:\\15CY_MU\\mu_1cpu\\modules'
    #srcpath='D:\\V23A0280\\module\\navi\\func_core\\mu\\modules'
    srcpath='ignore'
    tokpath='ignore/tokens'
    print(getTestFuncInfo(srcpath,tokpath,'mum_prgUpdCallback'))
