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
        self.is_Leaf = False
        self.updateHashValueForNode()

    def getRight(self):
        return self.right


    def setLeft(self,left):
        self.left = left
        self.left.father = self
        self.is_Leaf = False
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


def __find_smallest_path_to_leaf(root, count=0):
    if root.isLeaf():
        return (0, root)

    left_size , left_node = __find_smallest_path_to_leaf(root.getLeft(),count+1)
    right_size , right_node = __find_smallest_path_to_leaf(root.getRight(),count+1)
    if left_size<= right_size :
        return (left_size+1 , left_node)
    else:
        return (right_size +1 , right_node)


def __add_leaf_to_exsisting_node(root,data):

    if root.isNode() and root.getLeft() is None:
        leaf = node()
        leaf.setLeaf(data)

        root.setLeft(leaf)
        leaf.father(root)
        return 1

    elif root.isNode() and root.getRight() is None:
        leaf = node()
        leaf.setLeaf(data)

        root.setRight(leaf)
        leaf.father(root)
        return 1

    elif root.isNode() and root.getLeft().isNode() and __add_leaf_to_exsisting_node(root.getLeft(),data) == 1:
        return 1

    elif root.isNode() and root.getLeft().isNode() and __add_leaf_to_exsisting_node(root.getLeft(), data) == 1:
        return 1
    return 0

def __get_preorder_leaf_array(root,leaflist=[]):
    if root.isLeaf():
        leaflist.append(root)
        return leaflist

    if root.getLeft() is not None:
        leaflist = __get_preorder_leaf_array(root.getLeft(), leaflist)

    if root.getRight() is not None:
        leaflist = __get_preorder_leaf_array(root.getRight(), leaflist)

    return leaflist


def __get_preorder_leaf_by_id(root,id):
    if root.isLeaf():
        if id == 0:
            return (0,root)
        else:
            return id-1,None


    if root.getLeft() is not None:
        id,curr  = __get_preorder_leaf_by_id(root.getLeft(), id)

    if root.getRight() is not None:
        id,curr  = __get_preorder_leaf_by_id(root.getLeft(), id)

    return (id,curr)


def add_leaf(root,data):
    if __add_leaf_to_exsisting_node(root,data) == 1:
        return 1
    else:
        size, found_node = __find_smallest_path_to_leaf(root)
        leaf = node()
        leaf.setLeaf(data)
        left = found_node

        found_node.setLeft(left)
        left.father(found_node)

        found_node.setRight(leaf)
        leaf.father(found_node)
        return 1

# def create_Proof_of_Inclusion(root,id):
#     id,curr  =__get_preorder_leaf_by_id(root, id)
#     father = curr.father
#     while father.father !=None and father.father.father !=None:
#         father = father.father
#
#
#
#     print (f"{root.getHashValue()} {curr.getHashValue()},{curr.father.getHashValue()},{}")









