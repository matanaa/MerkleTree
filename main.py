import base64
import hashlib
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
class node:
    def __init__(self,saveData=True):
        self.hash_value=None
        self.right = None
        self.left =None
        self.data = None
        self.saveData = saveData
        self.father = None
        self.is_Leaf = True

    # def __eq__(self, other):
    #     if other == None:
    #         return False
    #     return self.hash_value == other.hash_value

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
            self.setHashValue(self.left.getHashValue() + self.right.getHashValue() )

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
        if self.right == None:
            return None
        return self.right


    def setLeft(self,left):
        self.left = left
        self.left.father = self
        self.is_Leaf = False
        self.updateHashValueForNode()

    def getLeft(self):
        if self.left == None :
            return None
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

    elif root.isNode() and root.getLeft() and root.getLeft().isNode() and __add_leaf_to_exsisting_node(root.getLeft(),data) == 1:
        return 1


    elif root.isNode() and root.getRight() and root.getRight().isNode() and __add_leaf_to_exsisting_node(root.getRight(),
                                                                                                       data) == 1:
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
        if curr is not None:
            return (id, curr)

    if root.getRight() is not None:
        id,curr  = __get_preorder_leaf_by_id(root.getRight(), id)

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

def Get_Brother_Hash(son):
    curr_bro_hash = ''
    if son.father.getLeft() == son:
        if son.father.getRight():
            curr_bro_hash = "1"+son.father.getRight().getHashValue()

    elif son.father.getLeft():
            curr_bro_hash  = "0"+son.father.getLeft().getHashValue()

    return curr_bro_hash


def create_Proof_of_Inclusion(root,id):
    id,curr  =__get_preorder_leaf_by_id(root, id)
    if curr is None or curr.father is None:
        return "not found"
    father = curr.father
    now = curr
    hashlist = ""

    while father.father !=None :
        hashlist += ","+Get_Brother_Hash(now)
        now = father
        father = father.father
    hashlist += "," + Get_Brother_Hash(now)

    #
    # if father.getLeft() == now :
    #     next_hash = "1"+father.getRight()
    # else:
    #     next_hash = "0"+father.getLeft()
    #
    # if curr.father.getLeft() == curr :
    #     curr_bro = "1"+curr.father.getRight()
    # else:
    #     curr_bro = "0"+curr.father.getLeft()
    #
    #     if curr_bro is '':
    #         curr_bro = node()
    #         curr_bro.hash_value = ''
    if hashlist is '':
        hashlist = Get_Brother_Hash(curr)

    return f"{hashlist},{root.getHashValue()}"

def verify_Proof_of_Inclusion(node_data,proof):
    proof = proof.split(',')
    node_hash = hashlib.sha224(node_data.encode()).hexdigest()
    hash_value = ''
    if proof[0] is not '':
        if proof[0].startswith('0'):
            hash_value = hashlib.sha224(proof[0][1:].encode()+node_hash.encode()).hexdigest()
        else:
            hash_value = hashlib.sha224( node_hash.encode() + proof[0][1:].encode() ).hexdigest()

    for i in range(1,len(proof)-1):
        p = proof[i]
        if p.startswith('0'):
            hash_value = hashlib.sha224(p[1:].encode()+hash_value.encode()).hexdigest()
        else:
            hash_value = hashlib.sha224( hash_value.encode() + p[1:].encode() ).hexdigest()

    return hash_value == proof[len(proof)-1]






def old_generate_RSA(bits=2048):
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


def generate_RSA(bits=2048):
    '''
    Generate an RSA keypair with an exponent of 65537 in PEM format
    param: bits The key length in bits
    Return private key and public key
    '''
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=bits,
        backend=default_backend()
    )

    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()

    )

    return  private_key_pem, public_key_pem


def sign_data(key_text, data):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    private_key = serialization.load_pem_private_key(key_text.encode(), None, backend=default_backend())

    signature = private_key.sign(
        data.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature)


def verify_data(key_text, signature,message):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    try:
        public_key = serialization.load_pem_public_key(key_text.encode(), backend=default_backend())

        decrtpyed = public_key.verify(
                        base64.b64decode(signature.encode()),
                        message.encode(),
                        padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                        )
        return True
    except:
        return False





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
root_node.is_Leaf = False
while True:
    action = input("Enter action :")
    if action.strip() == "1":
        data = input("Enter data :")
        add_leaf(root_node,data)

    elif action.strip() == "2":
        print(f"Root node key is : {root_node.getHashValue()}")

    elif action.strip() == "3":
        data = input("Enter row id :")
        print(f"proof for leaf {data} : {create_Proof_of_Inclusion(root_node,int(data.strip()))}")

    elif action.strip() == "4":
        data = input("Enter proof :")

        print(f"proof for leaf {data} : {verify_Proof_of_Inclusion(data.split(',', 1)[0],data.split(',', 1)[1])}")

    elif action.strip() == "5":
        private_key, public_key = generate_RSA()
        print(private_key.decode())
        print(public_key.decode())

    elif action.strip() == "6":
        key = multi_line_input("enter key: ")
        print(sign_data(key, root_node.getHashValue()).decode())

    elif action.strip() == "7":
        key_text = multi_line_input("enter key: ")
        signature = input("Enter signature:")
        message = input("Enter message:")

        print  (verify_data(key_text, signature, message))














