import copy
import random
import re
import os
import subprocess
import csv
class DotNodeAttr(object):
    def __init__(self):
        self._info={}
    def setAttr(self,key,value):
        self._info[key]=value
    def __str__(self):
        outtext=[]
        for (key,value) in sorted(self._info.iteritems()):
            outtext.append("%s=\"%s\""%(key,value))
        if len(outtext)>0:
            outstr='['+','.join(outtext)+']'
        else:
            outstr=''
        return outstr
class DotNode(object):
    def __init__(self,key,label,memo,color='black',shape='ellipse'):
        self._key=key
        self._label=label
        self._memo=memo
        self.textlen8()
        self._attr=DotNodeAttr()
        self.setAttr('color',color)
        self.setAttr('shape',shape)
    def setFakeLabel(self,text):
        # dot cannot manipulate japanese characters
        # use random ascii characters instead.
        self._fakelabel=text
    def getFakeLabel(self):
        return self._fakelabel
    def getLabelLength(self):
        return self._labellength
    def setAttr(self,key,value):
        if key=='shape' and value.startswith(r'polygon'):
            if len(value)==len(r'polygon'):
                sides=6
            else:
                sides=int(value[len(r'polygon'):])
            value='polygon'
            self._attr.setAttr('sides',sides)
        self._attr.setAttr(key,value)
    def checkKey(self,key):
        return self._key==str(key)
    def getLabel(self):
        return self._label
    def getMemo(self):
        return self._memo
    def __str__(self):
        outtext="%s %s;" % (self._fakelabel,str(self._attr))
        return outtext
    def textlen8(self,code='cp932'):
        # calculate text length (one japanese character = two ascii characters)
        data=self._label.decode(code).encode('utf8')
        index=0
        ret=0
        length=len(data)
        while index<length:
            idata=ord(data[index])
            if idata<=0x7f:
                ret+=1
                index+=1
            elif 0xc0<=idata<=0xdf:
                # 2 bytes character
                ret+=2
                index+=2
            elif 0xe0<=idata<=0xef:
                # 3 bytes character
                ret+=2
                index+=3
            elif 0xf0<=idata<=0xf7:
                # 4 bytes character
                ret+=2
                index+=4
            elif 0xf8<=idata<=0xfb:
                # 5 bytes character
                ret+=2
                index+=5
            elif 0xfc<=idata<=0xfd:
                # 6 bytes character
                ret+=2
                index+=6
        self._fakelabel='_'*ret
        self._labellength=ret

class DotGraph(object):
    def __init__(self):
        self._dotexe=r'C:\Program Files\Graphviz2.26.3\bin\dot.exe'
        self.init()
    def init(self):
        self._nodes=[]
        self._fakelabels={} # random labels for substituting japanese labels
        self._edges=[]
        self._groups=[] # [{label:string,fakelabel:ascii_string,nodes:[index,...]},...]
        self._ungroup=[]
        self._currentg=-1
    def parse(self,filename):
        self.init()
        filepat=re.compile(r'^(?P<name>.+)\.(?P<ext>[^.]+)$')
        refilepat=filepat.search(filename)
        if refilepat:
            name=refilepat.group('name')
            ext=refilepat.group('ext')
            dotfile=name+r'.dot'
            svgfile=name+r'.svg'
            self.parseExcelTab(filename)
            self.outputDot(dotfile)
            self.generateSVG(dotfile,svgfile)
            self.modifySVG(svgfile)
    def parseExcelTab(self,filename):
        fh=open(filename,'rU')
        sreader=csv.reader(fh,'excel-tab')
        flag_header=False
        for parts in sreader:
            if not flag_header:
                if '#START#' in parts:
                    # group start
                    startindex=parts.index('#START#')+1
                    stopindex=parts.index('#STOP#')-1
                    labelindex=parts.index('#START#')
                    textindex=parts.index('#LABEL#')
                    memoindex=parts.index('#MEMO#')
                    if '#COLOR#' in parts:
                        colorindex=parts.index('#COLOR#')
                    else:
                        colorindex=-1
                    if '#SHAPE#' in parts:
                        shapeindex=parts.index('#SHAPE#')
                    else:
                        shapeindex=-1
                    flag_header=True
                    dstkeys=parts[startindex:(stopindex+1)]
                    if len(parts)>stopindex+2 and parts[stopindex+2]:
                        # group label exists
                        self.startGroup(parts[stopindex+2])
            else:
                if '#GROUPEND#' in parts:
                    # group end
                    flag_header=False
                    self.stopGroup()
                else:
                    # create a node
                    node=DotNode(parts[labelindex],parts[textindex],parts[memoindex])
                    if colorindex>=0 and parts[colorindex]:
                        node.setAttr('color',parts[colorindex])
                    if shapeindex>=0 and parts[shapeindex]:
                        node.setAttr('shape',parts[shapeindex])
                    nindex=self.addNode(node)
                    # create edes starting from the current node
                    for i in range(len(parts)-startindex):
                        if parts[i+startindex]:
                            self.addEdge(nindex,dstkeys[i],parts[i+startindex])
        fh.close()
    def startGroup(self,label=""):
        self._currentg=self.getGroupNum()
        self._groups.append({})
        self._groups[self._currentg]['label']=label
        self._groups[self._currentg]['nodes']=[]
        node=DotNode(str(self._currentg),label,'')
        llen=node.getLabelLength()
        # generate one uniq fake label
        flabel='N#'+self.randomtext(llen)
        while flabel in self._fakelabels:
            flabel='N#'+self.randomtext(llen)
        self._fakelabels[flabel]=self._currentg
        # add a fake label starting with "G#" so as to distinguish from a node
        flabel='G#'+flabel[2:]
        self._fakelabels[flabel]=self._currentg
        self._groups[self._currentg]['fakelabel']=flabel[2:]
    def stopGroup(self):
        self._currentg=-1
    def getGroupNum(self):
        return len(self._groups)
    def selectGroup(self,index):
        self._currentg=int(index)%self.getGroupNum()
    def addNode(self,node):
        nodeindex=len(self._nodes)
        self._nodes.append(copy.deepcopy(node))
        if self._currentg>=0:
            self._groups[self._currentg]['nodes'].append(nodeindex)
        else:
            self._ungroup.append(nodeindex)
        llen=self._nodes[nodeindex].getLabelLength()
        # generate one uniq fake label
        flabel='N#'+self.randomtext(llen)
        while flabel in self._fakelabels:
            flabel='N#'+self.randomtext(llen)
        self._fakelabels[flabel]=nodeindex
        self._nodes[nodeindex].setFakeLabel(flabel[2:])
        return nodeindex
    def getNodeIndex(self,key):
        ret=-1
        for i in range(len(self._nodes)):
            if self._nodes[i].checkKey(key):
                ret=i
                break
        return ret
    def addEdge(self,srcindex,dstkey,edgeattr):
        self._edges.append((int(srcindex),str(dstkey),str(edgeattr),))
    def outputDot(self,filename):
        outtext="digraph G {\n"
        for i in range(len(self._groups)):
            outtext+="\tsubgraph cluster%d {\n" % (i)
            outtext+="\t\tlabel=\"%s\";\n" % (self._groups[i]['fakelabel'])
            for ni in self._groups[i]['nodes']:
                outtext+="\t\t"+str(self._nodes[ni])+"\n"
            outtext+="\t}\n"
        for i in range(len(self._edges)):
            srctext=self._nodes[self._edges[i][0]].getFakeLabel()
            dsttext=self._nodes[self.getNodeIndex(self._edges[i][1])].getFakeLabel()
            outtext+="\t%s -> %s [%s];\n" % (srctext,dsttext,self._edges[i][2])
        outtext+="}\n"
        fh=open(filename,'w')
        fh.write(outtext)
        fh.close()
    def generateSVG(self,dotfile,svgfile):
        param=[self._dotexe,r'-Tsvg',dotfile,r'-o',svgfile]
        subprocess.check_call(param)
        return
    def modifySVG(self,filename):
        outtext=""
        pat=re.compile(r'^(?P<prefix>.+class="node"><title>)(?P<label>.+?)(?P<postfix></title>.*)') # pattern for node hint
        pat2=re.compile(r'^(?P<prefix>.+>)(?P<label>[a-zA-Z_]+)(?P<postfix></text>.*)') # pattern for node label and group label
        pat3=re.compile(r'^(?P<prefix>.+class="edge"><title>)(?P<label1>[a-zA-Z_]+)&#45;&gt;(?P<label2>[a-zA-Z_]+)(?P<postfix></title>.*)') # pattern for edge
        fh=open(filename,'rU')
        for line in fh.readlines():
            retpat=pat.search(line)
            retpat2=pat2.search(line)
            retpat3=pat3.search(line)
            if retpat:
                label='N#'+retpat.group('label')
                text=self._nodes[self._fakelabels[label]].getMemo()
                text=text.decode('cp932').encode('utf8')
                line=retpat.group('prefix')+text+retpat.group('postfix')+"\n"
            if retpat2:
                label='G#'+retpat2.group('label')
                if label in self._fakelabels:
                    # group label
                    text=self._groups[self._fakelabels[label]]['label']
                else:
                    # node label
                    text=self._nodes[self._fakelabels['N#'+label[2:]]].getLabel()
                text=text.decode('cp932').encode('utf8')
                line=retpat2.group('prefix')+text+retpat2.group('postfix')+"\n"
            if retpat3:
                label='N#'+retpat3.group('label1')
                label2='N#'+retpat3.group('label2')
                text=self._nodes[self._fakelabels[label]].getLabel()
                text2=self._nodes[self._fakelabels[label2]].getLabel()
                text=text.decode('cp932').encode('utf8')
                text2=text2.decode('cp932').encode('utf8')
                line=retpat3.group('prefix')+text+r'&#45;&gt;'+text2+retpat3.group('postfix')+"\n"
            outtext+=line
        fh.close()
        if os.path.exists(filename+".bak"):
            os.unlink(filename+".bak")
        os.rename(filename,filename+".bak")
        fh=open(filename,'w')
        fh.write(outtext)
        fh.close()
    def randomtext(self,length):
        allchar=r'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
        allchar=allchar*(1+length/len(allchar))
        return "".join(random.sample(allchar,length))

if __name__=='__main__':
    sob=DotGraph()
    sob.parse('svg.txt')
