import sys
import os.path
import re
import codecs
sys.path.append('./plugins')
import ply.lex as lex
from logutil import LogUtil

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
    def __init__(self):
        self._log=LogUtil().logger('TokenManager')
        self._parser=CParser()
        self._encode=['utf-8','cp932','cp936']
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
    def getFunctionTokens(self,tokfile,funcname):
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
                    outlist.append((parts[6],tokens[int(parts[2]):int(parts[3])+1]))
            return tuple(outlist)
        else:
            return ()
    def getFunctionCalls(self,tokfile,funcname,excl=('memset','memcpy')):
        '''
        @ret:([funcdecl,inner-func1:call-count1,...],...)
        '''
        functokens=self.getFunctionTokens(tokfile,funcname)
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
        srcstruct=self._parser.analyzeFile(tokens)
        tokpath=os.path.dirname(tokfile)
        if not os.path.exists(tokpath) or not os.path.isdir(tokpath):
            os.makedirs(tokpath)
        fh=open(tokfile,'w')
        fh.write('@SrcInfo:\n%s\n'%(self._genFileChecksum(srcfile),))
        fh.write('@Structure:\n%s\n'%('\n'.join(srcstruct),))
        fh.write('@Token:\n')
        for tok in tokens:
            fh.write('%s:%d:%s\n'%(tok.type,tok.lineno,tok.value.encode('utf-8')))
        fh.close()
    def _checkTokFile(self,srcfile,tokfile):
        ret=False
        if os.path.exists(tokfile) and os.path.isfile(tokfile):
            checksum=self._genFileChecksum(srcfile)
            curchecksum='\n'.join(self._loadTokFile(tokfile,'SrcInfo'))
            ret=(checksum==curchecksum)
        return ret
    def _genFileChecksum(self,srcfile):
        infile=os.path.abspath(srcfile)
        mtime=os.path.getmtime(infile)
        outstr='%s\n%d'%(infile,mtime)
        return outstr
    def _loadTokFile(self,tokfile,partname):
        outlist=[]
        with open(tokfile,'rU') as fh:
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
    def t_comment(self,t):
        r'(/\*(.|\n)*?\*/|//.*)'
        t.lexer.lineno += t.value.count('\n')

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
        fh=open(fname,'rU')
        lines=fh.read()
        fh.close()
        for bom in (
                    codecs.BOM_UTF32,
                    codecs.BOM_UTF32_BE,
                    codecs.BOM_UTF32_LE,
                    codecs.BOM_UTF16,
                    codecs.BOM_UTF16_BE,
                    codecs.BOM_UTF16_LE,
                    codecs.BOM_UTF8):
            bomlen=len(bom)
            if lines[:bomlen]==bom:
                lines=lines[bomlen:]
                break
        for en in encode:
            data=lines
            try:
                data=lines.decode(en)
                break
            except:
                pass
        else:
            self._log.critical('No Valid Encoding')
            return
        self._log.info('parse file: filename=%s encoding=%s'%(fname,en))
        data.encode('utf-8')
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

    def _outputsrc(self,data):
        #print data
        pass
    def analyzeFile(self,tokens):
        toklen=len(tokens)
        ifdef=[] # lineno:tokenno:#xxx:value / lineno:tokenno:sts:#level:{level:[level:(level
        idx=0
        headidx=0
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
                idx2=idx+1
                while tokens[idx2].type!='PREPROCESSOREND':
                    idx2+=1
                outlist.append('%d:%d:%d:%d:PP:%s'%(tokens[idx].lineno,tokens[idx2].lineno,idx,idx2,tokens[idx+1].value))
                self._log.debug('Token[%d-%d/%d]: lineno=%d-%d PP-type=%s InStatement=%s'%(idx,idx2,toklen,tokens[idx].lineno,tokens[idx2].lineno,tokens[idx+1].value,str(flag_instatement)))
                if tokens[idx+1].value.startswith('if'):
                    level0+=1
                    ifdef.append('%d:%d:#%s'%(tokens[idx].lineno,idx,':'.join([t.value for t in tokens[idx+1:idx2]])))
                    idx=idx2
                    ifdef.append('%d:%d:%d:%d:%d:%d:%d'%(tokens[idx].lineno,idx,sts,level0,level1,level2,level3))
                    self._log.debug('->#:%d {}:%d []:%d ():%d'%(level0,level1,level2,level3))
                elif tokens[idx+1].value.startswith('el'):
                    ifdef.append('%d:%d:#%s'%(tokens[idx].lineno,idx,':'.join([t.value for t in tokens[idx+1:idx2]])))
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
                elif tokens[idx+1].value.startswith('end'):
                    level0-=1
                    ifdef.append('%d:%d:#%s'%(tokens[idx].lineno,idx,':'.join([t.value for t in tokens[idx+1:idx2]])))
                    idx=idx2
                    ifdef.append('%d:%d:%d:%d:%d:%d:%d'%(tokens[idx].lineno,idx,sts,level0,level1,level2,level3))
                    self._log.debug('->#:%d {}:%d []:%d ():%d'%(level0,level1,level2,level3))
                else:
                    idx=idx2
                if not flag_instatement:
                    # #xxx
                    self._outputsrc('%s%s'%(tokens[headidx].value,' '.join([t.value for t in tokens[headidx+1:idx]])))
                    headidx=idx+1
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
                                    funcdecl=' '.join([x.value for x in tokens[headidx:idx]])
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
                        self._outputsrc(' '.join([t.value for t in tokens[headidx:idx+1]]))
                        headidx=idx+1
                        self._log.debug('->head_token:%d'%(headidx,))
                elif tokens[idx].type=='COLON':
                    # label: / case xxx:
                    self._outputsrc(' '.join([t.value for t in tokens[headidx:idx+1]]))
                    headidx=idx+1
                    self._log.debug('->head_token:%d'%(headidx,))
                elif tokens[idx].type=='LBRACE':
                    if sts==0:
                        # left brace
                        self._outputsrc(' '.join([t.value for t in tokens[headidx:idx]]))
                        self._outputsrc(tokens[idx].value)
                        oldheadidx=headidx
                        funcdecl=' '.join([x.value for x in tokens[oldheadidx:idx]])
                        headidx=idx+1
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
                        self._outputsrc(' '.join([t.value for t in tokens[headidx:idx]]))
                        self._outputsrc(tokens[idx].value)
                        oldheadidx=headidx
                        headidx=idx+1
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
                        self._outputsrc(' '.join([t.value for t in tokens[headidx:idx]]))
                        self._outputsrc(tokens[idx].value)
                        headidx=idx+1
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
            idx+=1
        return tuple(outlist)
    def analyzeFunction(self,tokens):
        toklen=len(tokens)
        if toklen<6:
            # at least 6 tokens: void funcname ( ) { }
            self._log.warning('function tokens error')
        if tokens[-1].type!='RBRACE':
            self._log.warning('function tokens error')
        idx=0
        idxp1,idxp2=toklen,0
        while idx<toklen:
            if tokens[idx].type=='LPAREN':
                idxp1=min(idxp1,idx)
            elif tokens[idx].type=='RPAREN':
                idxp2=idx
            if tokens[idx].type=='LBRACE':
                break
            idx+=1
        else:
            self._log.warning('function tokens error')
        if idxp1>=idxp2:
            self._log.warning('function tokens error')
        idxmin=idx+1
        idxmax=toklen-2
        autovars=[]
        funcs={}
        # analyze function's parameter list
        if idxp2-idxp1<=2:
            # no parameter / void
            self._log.debug('no parameter')
            pass
        else:
            idx=idxp2-1
            cnt=0
            flag=True
            while idx>idxp1:
                if tokens[idx].type in ('LPAREN','LBRACKET'):
                    cnt-=1
                elif tokens[idx].type in ('RPAREN','RBRACKET'):
                    cnt+=1
                elif tokens[idx].type=='COMMA':
                    flag=True
                elif tokens[idx].type=='ID':
                    if flag and cnt==0:
                        flag=False
                        autovars.insert(0,tokens[idx].value)
                idx-=1
            self._log.debug('parameter(s):%s'%(','.join(autovars),))
        # analyze function's body
        # analyze functions called by current function
        idx=idxmin
        while idx<=idxmax:
            if tokens[idx].type=='LPAREN' and tokens[idx-1].type=='ID':
                funcname=tokens[idx-1].value
                if funcname not in funcs:
                    funcs[funcname]=0
                funcs[funcname]+=1
            idx+=1
        self._log.debug('inner function(s):%s'%(str(funcs),))
        return funcs

def getFuncInfo(srcpath,tokpath,*funclist):
    fdict=tokenmanager.findFunctionBySrc(srcpath,tokpath,*funclist)
    for funcname in fdict.keys():
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
                    map(lines.add,range(int(parts[0]),int(parts[1])+1))
        else:
            if parts[5] in info.get(parts[4],()):
                map(lines.add,range(int(parts[0]),int(parts[1])+1))
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
    fh=open(srcfile,'rU')
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
        fout=open(outfile,'w')
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
    print getTestFuncInfo(srcpath,tokpath,'mum_prgUpdCallback')
