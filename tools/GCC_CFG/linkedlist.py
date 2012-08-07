class ListNode(object):
    def __init__(self,data):
        self._data=data
        self._prev=[]
        self._next=[]
    def getData(self):
        return self._data
    def appendNext(self,other):
        if isinstance(other,ListNode):
            self._next.append(other)
    def appendPrev(self,other):
        if isinstance(other,ListNode):
            self._prev.append(other)
    def __cmp__(self,other):
        if isinstance(other,ListNode):
            return cmp(self.getData(),other.getData())
        else:
            return -1
class LinkedList(object):
    def __init__(self):
        self._nodes=[]
    def addNode(self,node):
        ret=0
        if isinstance(node,ListNode):
            ret=len(self._nodes)
            self._nodes.append(node)
        return ret
    def findNode(self,node):
        ret=-1
        if node in self._nodes:
            ret=self._nodes.index(node)
        return ret
    def addEdge(self,index1,index2):
        length=len(self._nodes)
        if index1<length and index2<length:
            self._nodes[index1].appendNext(self._nodes[index2])
            self._nodes[index2].appendPrev(self._nodes[index1])
    def getPath(self,startindex):
        length=len(self._nodes)
        retlist=[]
        if startindex<length:
            pass
        return tuple(retlist)

if __name__=='__main__':
    ll=LinkedList()
    n1=ListNode("axj")
    index=ll.addNode(n1)
    print("%s\t%d"%(n1.getData(),index))
    n1=ListNode("bon")
    index=ll.addNode(n1)
    print("%s\t%d"%(n1.getData(),index))
    n1=ListNode("gfc")
    index=ll.addNode(n1)
    print("%s\t%d"%(n1.getData(),index))
    n1=ListNode(",cb")
    index=ll.addNode(n1)
    print("%s\t%d"%(n1.getData(),index))
    n1=ListNode("feg")
    index=ll.addNode(n1)
    print("%s\t%d"%(n1.getData(),index))
    n1=ListNode("gfc")
    print(ll.findNode(n1))
