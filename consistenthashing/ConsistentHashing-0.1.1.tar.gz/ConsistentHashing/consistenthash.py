import hashlib

# A simple implement of consistent hashing

class hash_ring(object):
    
    def __init__(self, nodes=[], slotSize=1000, virtualNode=0):
        self.nodes = {}
        self.nodeList = []
        self.slotSize = slotSize
        self.virtualNode = virtualNode
        for node in nodes:
            self.nodeList.append(node)
            hashValue = self._getHashValue(node)
            self.nodes[hashValue] = node
            if self.virtualNode: 
                self._addVirtualNodes(node)

    def addNode(self, node):
        self.nodeList.append(node)
        if node not in self.nodes.values():
            hashValue = self._getHashValue(node)
            self.nodes[hashValue] = node
            if self.virtualNode:
                self._addVirtualNodes(node)
        else:
            print 'Node %s alreday added' % node
        return True

    def _addVirtualNodes(self, node):
        for i in range(1, self.virtualNode+1):
            vnode = "%s_virtual%s" % (node,i)
            hashValue = self._getHashValue(vnode)
            self.nodes[hashValue] = node
        return True

    def removeNode(self, node):
        if node in self.nodes.values():
            self.nodeList.remove(node)
            hashValue = self._getHashValue(node)
            del self.nodes[hashValue]
            if self.virtualNode:
                self._removeVirtualNodes(node)
            return True
        else:
            print 'Node %s not exist' % node
            return False

    def _removeVirtualNodes(self, node):
        vnodes = ["%s_virtual%s" % (node,i) for i in range(1, self.virtualNode+1)]
        for vnode in vnodes:
            try:
                hashValue = self._getHashValue(vnode)
                del self.nodes[hashValue]
            except Exception, e:
                print 'Vnode %s not exist' % vnode

    def getNode(self, key):
        hashValue = self._getHashValue(key)
        l = [x for x in self.nodes.keys() if x - hashValue >= 0]
        return self.nodes[min(l)]

    def _getHashValue(self, key):
        hashFunction = hashlib.md5()
        hashFunction.update(key)
        return int(hashFunction.hexdigest(), 16) % self.slotSize

    def getAllNodes(self):
        return self.nodeList

    def getVirtualNodeNumber(self):
        return self.virtualNode

    def getVirtualNodes(self,node):
        return ["%s_virtual%s" % (node,i) for i in range(1, self.virtualNode+1)]
