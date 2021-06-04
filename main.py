import hashlib

class node:
    def __init__(self,saveData=True):
        self.hash_value=None
        self.right = None
        self.left =None
        self.data = None
        self.saveData = saveData
        self.father = None
        self.is_Leaf = False

    def getHashValue(self):
        return self.hash_value

    def setHashValue(self,data):
        self.hash_value = hashlib.sha224(data).hexdigest()

    def updateHashValueForNode(self):
        if self.right != None and self.left != None:
            self.setHashValue(self.right.getHashValue() + self.left.getHashValue())

        elif self.left != None:
            self.setHashValue(self.left.getHashValue())

        elif self.right != None:
            self.setHashValue(self.right.getHashValue())
        else:
            return 0
        self.father.updateHashValueForNode()
        return 1

    def setRight(self,right):

        self.right = right
        self.right.father = self
        self.updateHashValueForNode()

    def getRight(self):
        return self.right


    def setLeft(self,left):
        self.left = left
        self.left.father = self
        self.updateHashValueForNode()

    def getLeft(self):
        return self.left

    def setLeaf(self,data):
        self.is_Leaf = True
        self.setHashValue(data)
        if self.saveData:
            self.data = data

    def isLeaf(self):
        return self.is_Leaf

    def isNode(self):
        return not self.isLeaf()

    def setFather(self, node):
        self.father = node

    def getFather(self):
        return  self.father


def find_smallest_path_to_leaf(root, count=0):
    if root.isLeaf():
        return (0, root)

    left_size , left_node = find_smallest_path_to_leaf(root.getLeft(),count+1)
    right_size , right_node = find_smallest_path_to_leaf(root.getRight(),count+1)
    if left_size<= right_size :
        return (left_size+1 , left_node)
    else:
        return (right_size +1 , right_node)


def add_leaf(root,data):
    leaf = node()
    leaf.setLeaf(data)
    if root.isNode() and root.getLeft() is None :
        root.setLeft(leaf)
        leaf.father(root)
        return 1

    elif root.isNode() and root.getRight() is None:
        root.setRight(leaf)
        leaf.father(root)
        return 1

    elif root.isNode() and root.getLeft().isNode() and add_leaf(root.getLeft(),data) == 1:
        return 1

    elif root.isNode() and root.getLeft().isNode() and add_leaf(root.getLeft(), data) == 1:
        return 1










