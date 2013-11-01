# -- coding:UTF8 --
import logging
import sys

class Edge(object):
    def __init__(self,snode,enode,cost=1):
        self._snode=str(snode)
        self._enode=str(enode)
        self._cost=int(cost)
    @property
    def snode(self):
        return self._snode
    @property
    def enode(self):
        return self._enode
    @property
    def cost(self):
        return self._cost
    def __str__(self):
        outstr="Snode[%s] Enode[%s] Cost[%s]"%(self._snode,self._enode,self._cost)
        return outstr

class NodeMap(object):
    ## Usage:
    ## nm=NodeMap()
    ## nm.addEdge(snode,enode,cost)
    ## nm.getNodeList()
    ## nm.getMarkHash()
    ## nm.deleteNode(*nodelist)
    ## for e in nm.getEdges():
    ##   print "{snode} {enode} {cost}".format(**e)
    def __init__(self,loglevel=logging.CRITICAL,logfile=''):
        self._log=self._initLogger(loglevel,logfile)
        self._initData()
    def addEdge(self,snode,enode,cost=1):
        edge=Edge(snode,enode,cost)
        if edge.cost>0:
            self._log.debug("[AddEdge] Edge:%s"%(str(edge),))
            self._edgelist.append(edge)
            self._dirty=True
            return True
        else:
            self._log.warn("[AddEdge] Invalid Edge:%s"%(str(edge),))
            return False
    def getEdges(self):
        for edge in self._edgelist:
            yield {'snode':edge.snode,'enode':edge.enode,'cost':edge.cost}
    def getNodeList(self):
        self._updateStatus()
        return tuple(self._nodelist)
    def getMarkHash(self):
        self._updateStatus()
        return dict(self._markhash)
    def getMapHead(self):
        self._updateStatus()
        return self._getMapHead()
    def deleteNode(self,*nodelist):
        # Algorithm:
        #  1.remove edges connecting nodelist
        #  2.remove nodes donot connect to the root
        # create a virtual root
        self._updateStatus()
        rootnode='_#_'
        maphead=self._getMapHead()
        while rootnode in self._nodelist:
            rootnode=rootnode+rootnode
        for hnode in maphead:
            self.addEdge(rootnode,hnode,1)
        # create a virtual edge from root
        dmynode='#-#'
        while dmynode in self._nodelist:
            dmynode=dmynode+dmynode
        self.addEdge(rootnode,dmynode,1)
        # update nodelist
        self._updateStatus()
        # Algorithm-1
        deleteflg=self._deleteNode(nodelist)
        # Algorithm-2
        deletelist=[rootnode]
        if deleteflg:
            # edges are modified
            for node in self._nodelist:
                if 0<self._markhash[node][rootnode]<sys.maxint:
                    pass
                else:
                    if node not in deletelist:
                        deletelist.append(node)
        self._deleteNode(deletelist)
    def _updateStatus(self):
        if self._dirty:
            self._getNodeList()
            self._calculateMark()
            self._dirty=False
    def _getMapHead(self):
        s=set(self._nodelist)
        for edge in self._edgelist:
            s.discard(edge.enode)
        self._log.debug("[MapHead] Head:%s"%(str(s),))
        return tuple(s)
    def _deleteNode(self,nodelist):
        newlist=[]
        deleteflg=False
        self._log.debug("[DeleteNode] Nodes:%s"%(str(nodelist),))
        for edge in self._edgelist:
            for node in nodelist:
                if edge.snode==node or edge.enode==node:
                    self._log.debug("[DeleteNode] Edge:%s"%(str(edge),))
                    deleteflg=True
                    break
            else:
                newlist.append(edge)
        if deleteflg:
            self._dirty=True
            self._edgelist=list(newlist)
            self._updateStatus()
            return True
        else:
            return False
    def _getNodeList(self):
        s=set()
        for edge in self._edgelist:
            s.add(edge.snode)
            s.add(edge.enode)
        self._log.info("[NodeList] Nodes:%s"%(str(s),))
        self._nodelist=tuple(s)
    def _getNodeHead(self,node):
        s=set()
        for edge in self._edgelist:
            if edge.enode==node:
                s.add((edge.snode,edge.cost))
        self._log.debug("[NodeHead] Head for [%s]:%s"%(node,str(s)))
        return tuple(s)
    def _calculateMark(self):
        self._markhash={}
        for node in self._nodelist:
            self._markhash[node]={}
            self._markflg[node]=False
            for node2 in self._nodelist:
                if node==node2:
                    self._markhash[node][node2]=0
                else:
                    self._markhash[node][node2]=sys.maxint
        for node in self._nodelist:
            self._calculateMarkOne(node)
    def _calculateMarkOne(self,node):
        if self._markflg[node]:
            return
        self._log.debug("[CalculateMark] Start:%s"%(node,))
        heads=self._getNodeHead(node)
        for h in heads:
            self._calculateMarkOne(h[0])
            for node2 in self._nodelist:
                self._markhash[node][node2]=min(self._markhash[node][node2],self._markhash[h[0]][node2]+h[1])
        self._markflg[node]=True
        self._log.debug("[CalculateMark] End:%s=>%s"%(node,str(self._markhash[node])))
    def _initData(self):
        self._edgelist=[]
        self._dirty=False
        self._markhash={}
        self._markflg={}
        self._nodelist=()
    def _initLogger(self,level,logfile=''):
        log=logging.getLogger(self.__class__.__name__)
        log.setLevel(level)
        ch=self._getLogHandler(logfile)
        formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        log.addHandler(ch)
        return log
    def _getLogHandler(self,logfile=''):
        if logfile:
            ch=logging.FileHandler(logfile)
        else:
            ch=logging.StreamHandler()
        return ch

if __name__ == '__main__':
    import re
    nm=NodeMap(logfile='nmlog.txt')
    pat=re.compile(r'^\s*(?P<snode>\S+)\s*->\s*(?P<enode>\S+);')
    fh=open('test.dot','r')
    for line in fh.readlines():
        rpat=pat.search(line)
        if rpat:
            nm.addEdge(rpat.group('snode'),
                       rpat.group('enode'),
                       1)
    fh.close()
    nm.getNodeList()
    for node in nm._nodelist:
        for node2 in nm._nodelist:
            if 0<nm._markhash[node][node2]<sys.maxint:
                print node,node2,nm._markhash[node][node2]
    print
    nm.deleteNode(str('B'))
    nm.getNodeList()
    for node in nm._nodelist:
        for node2 in nm._nodelist:
            if 0<nm._markhash[node][node2]<sys.maxint:
                print node,node2,nm._markhash[node][node2]
    for edge in nm.getEdges():
        print "{snode} -> {enode} [{cost}]".format(**edge)
