import hashlib
from Crypto.PublicKey import RSA

class node:
    def __init__(self,saveData=True):
        self.hash_value=None
        self.right = None
        self.left =None
        self.data = None
        self.saveData = saveData
        self.father = None
        self.is_Leaf = False

    def __eq__(self, other):
        if other == None:
            return False
        return self.hash_value == other.hash_value

    def __copy__(self):
        copyObj = node()
        copyObj.hash_value = self.hash_value
        copyObj.right = self.right
        copyObj.left = self.left
        copyObj.data = self.data
        copyObj.saveData = self.saveData
        copyObj.father = self.father
        copyObj.is_Leaf = self.is_Leaf
        return copyObj

    def getHashValue(self):
        return self.hash_value

    def setHashValue(self,data):
        self.hash_value = hashlib.sha224(data.encode()).hexdigest()

    def updateHashValueForNode(self):
        if self.right is not None and self.left is not None:
            self.setHashValue(self.right.getHashValue() + self.left.getHashValue())

        elif self.left is not None:
            self.setHashValue(self.left.getHashValue())

        elif self.right is not None:
            self.setHashValue(self.right.getHashValue())
        else:
            return 0
        if self.father is not None:
            print(self,self.father)
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
        leaf.father=root
        return 1

    elif root.isNode() and root.getRight() is None:
        leaf = node()
        leaf.setLeaf(data)

        root.setRight(leaf)
        leaf.father =root
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
        size, found_node = __find_smallest_path_to_leaf(root) # this leaf will replace to node
        right_leaf = node()
        right_leaf.setLeaf(data)
        left_leaf =node()
        left_leaf.data = found_node.data
        left_leaf.hash_value = found_node.hash_value


        left_leaf.setFather(found_node)
        found_node.setLeft(left_leaf)


        right_leaf.setFather(found_node)
        found_node.setRight(right_leaf)

        return 1

def create_Proof_of_Inclusion(root,id):
    id,curr  =__get_preorder_leaf_by_id(root, id)
    if curr is None or curr.father is None:
        return "not found"
    father = curr.father
    now = curr

    while father.father !=None :
        now = father
        father = father.father


    if father.getLeft() == now :
        next_hash = father.getRight()
    else:
        next_hash = father.getLeft()
    return f"{root.getHashValue()} {curr.getHashValue()},{curr.father.getHashValue()},{next_hash.getHashValue()}"

def generate_RSA(bits=2048):
    '''
    Generate an RSA keypair with an exponent of 65537 in PEM format
    param: bits The key length in bits
    Return private key and public key
    '''
    from Crypto.PublicKey import RSA
    new_key = RSA.generate(bits, e=65537)
    public_key = new_key.publickey().exportKey("PEM")
    private_key = new_key.exportKey("PEM")
    return private_key, public_key

def multi_line_input(show=None):
    if show:
        print(show,end='')
    lines = []
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            break
    text = '\n'.join(lines)
    return text
root_node = node()
while True:
    action = input("Enter action :")
    if action.strip() == "1":
        data = input("Enter data :")
        add_leaf(root_node,data)

    if action.strip() == "2":
        print(f"Root node key is : {root_node.getHashValue()}")

    if action.strip() == "3":
        data = input("Enter row id :")
        print(f"proof for leaf {data} : {create_Proof_of_Inclusion(root_node,int(data.strip()))}")

    if action.strip() == "5":
        private_key, public_key = generate_RSA()
        print(private_key.decode())
        print(public_key.decode())

    if action.strip() == "6":
        data = multi_line_input("enter key: ")













