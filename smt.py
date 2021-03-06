import base64
import copy
import hashlib
import json
import zlib

DEFAULT_HASH_FUNCTION = lambda x: hashlib.sha256(str(x).encode()).hexdigest()
MAX_DEPTH = 64
KNOWN_RANDOMNESS = "0122145a87e25335b71ee0562fc590e4b3754f1b8feb06a44ecdb22ec996cfa4"  # this value can't be inserted into the tree.


def int_to_binarray(x, d):
    """
    Finds the pathway for the X'th item in row D using zero based indexing.
    root to leaf
    """
    m = [int(s) for s in bin(x)[2:]]
    x = [0] * (d - len(m)) + m
    x.reverse()
    return x


def binarray_to_int(x):
    s = 0
    y = copy.copy(x)
    y.reverse()
    for k in y:
        s = s * 2 + k
    return s


# initialize known empty hashes
empty_hashes = dict()
empty_hashes[MAX_DEPTH] = DEFAULT_HASH_FUNCTION(str(MAX_DEPTH) + KNOWN_RANDOMNESS)
# cache empty hashes for all depths
for i in range(1, MAX_DEPTH + 1):
    j = MAX_DEPTH - i
    empty_hashes[j] = DEFAULT_HASH_FUNCTION(empty_hashes[j + 1] * 2)
empty_hash_values = set(empty_hashes.values())


def verify_path(path, root, hashfunction=DEFAULT_HASH_FUNCTION, max_depth=MAX_DEPTH):
    if not path[0] in path[1] and len(path[0]) == 1:
        return False
    # elif not (path[0][0] in empty_hash_values and path[0][1] in empty_hash_values):
    # 	return False

    for i in range(1, len(path) - 1):
        left = path[i][0]
        right = path[i][1]
        expected_parent = hashfunction(left + right)
        if expected_parent not in path[i + 1]:
            return False

    if not hashfunction(path[-1][0] + path[-1][1]) == root:
        return False

    return True


def infer_position(cpath, root, hashfunction=DEFAULT_HASH_FUNCTION):
    """
    For a given path, infer the depth and n positions of the path.
    returns (depth, n)
    """
    binarray = []
    path = copy.copy(cpath)
    lasthash = path.pop(0)
    while path:
        lhash, rhash = path.pop(0)
        if lhash == lasthash:
            binarray.append(0)
        elif rhash == lasthash:
            binarray.append(1)
        else:
            raise Exception("Invalid Path")

        lasthash = hashfunction(lhash + rhash)

    n = binarray_to_int(binarray)
    depth = len(cpath[1:])
    return depth, n


def verify_membership(value, path, root, depth=None, n=None, hashfunction=DEFAULT_HASH_FUNCTION):
    """
    For a given hashfunction, root of a merkle tree, and path
    return True False whether the value is a member of the tree with this root.
    If depth and n positions are specified, will also assert that these positions are correct.
    If they are not specified, will infer these from path.
    """
    verify_leaf = hashfunction(value) == path[0]
    path_valid = verify_path(path, root)

    # todo additional checks for position.

    return verify_leaf and path_valid


def verify_nonmembership(path, root, depth):
    goodpath = verify_path(path, root)
    not_a_member = len(path) != depth + 1

    # todo some kind of infer position, assure that path agrees with (n, depth)
    return goodpath and not_a_member


class SMT:
    def __init__(self, max_depth=MAX_DEPTH, hashfunction=DEFAULT_HASH_FUNCTION, dump=None):
        self.hashes = {}
        self.n_elements = 0
        self.max_depth = max_depth
        self.hash = hashfunction
        self.leaf_nodes = set()

        self.empty_hashes = dict()
        self.empty_hashes[max_depth] = self.hash(str(max_depth) + KNOWN_RANDOMNESS)

        # cache empty hashes for all depths
        for i in range(1, max_depth + 1):
            j = max_depth - i
            self.empty_hashes[j] = self.hash(self.empty_hashes[j + 1] * 2)

        self.empty_hash_values = set(self.empty_hashes.values())

        if dump is not None:
            self.from_string(dump)

    def coordinate_is_empty(self, coordinate):
        return tuple(coordinate) in self.hashes

    def read_hash(self, coordinate):
        return self.hashes.get(tuple(coordinate), self.empty_hashes[len(coordinate)])

    def add_node(self, n, depth, value, hash=True):
        """
        Adds to an arbitrary, not-necessarily leaf node at the N'th node at depth.
        Also performs hashes recurively upward.
        You are not allowed to modify a node that is the parent of another from the outside,
        otherwise you will break the relationship.  Existing hashes can only be overwritten
        when working upwards recursively.
        Returns the Merkle Path.
        """
        m = int_to_binarray(n, depth)
        if tuple(m) in self.hashes:
            raise Exception("Cannot directly modify occupied hashes.")

        self.hashes[tuple(m)] = self.hash(value) if hash else value
        self.leaf_nodes.add((n, depth))
        # path = [self.hashes[tuple(m)]]

        while len(m) > 0:
            m = m[:-1]
            left = m + [0]
            right = m + [1]
            lhash = self.read_hash(left)
            rhash = self.read_hash(right)
            self.hashes[tuple(m)] = self.hash(lhash + rhash)
        # path.append([lhash, rhash])

        self.n_elements += 1
        return self.path(n, depth)

    def add_to_next_leaf(self, value):
        self.add_node(self.n_elements, self.max_depth,
                      value)  # technically nodes added at non-leaves make this non-monotonic, but OK.

    def add_to_leaf(self, value, position):
        """
        Adds the hash of value X to leaf node position.
        """
        self.add_node(position, self.max_depth, value)

    def add_node_set(self, nodeset):
        """
        Adds a list of nodes and computes more efficiently.
        A list of nodes is composed of a list of [n, depth, value]
        """
        # TODO
        return

    def path(self, n, depth, full=False):
        """
        [root]
        left, right
        left, right
        left, right
        leaf
        Returns a merkle path from root, to n, depth coordinates.
        The format of the path is an array of [LEFT VALUE, RIGHT VALUE].
        Except the first value is the leaf hash since this is not clear otherwise.
        The root hash is ommitted because it is implied by final left-right pair.
        if FULL is False, as is default, path will be truncated if empty hashes are found.
        Full = True will print empty hashes as well.
        If N, depth is NULL, or any parents are NULL, provides whatever path is possible until default null values are hit.
        """
        m = int_to_binarray(n, depth)
        h = self.read_hash(m)
        if h not in self.empty_hash_values:
            path = [self.read_hash(m)]
        else:
            path = []

        # leaf to root
        while True:
            left = m[:-1] + [0]
            right = m[:-1] + [1]
            lefth = self.read_hash(left)
            righth = self.read_hash(right)
            if not (lefth in self.empty_hash_values and righth in self.empty_hash_values):
                path.append([lefth, righth])
            m = m[:-1]
            if len(m) == 0:
                break
        return path

    def root(self):
        return self.hashes[()]

    def sparse_dump(self):
        """
        Dump the minimal amount of data necessary to reconstruct the FULL tree.
        """
        d = {}
        for k in self.leaf_nodes:
            n, depth = k
            b = tuple(int_to_binarray(n, depth))
            d[str(k)] = self.hashes[b]
        return d

    def to_string(self):
        dump = self.sparse_dump()
        dump['max_depth'] = self.max_depth
        s = str(json.dumps(dump))
        zs = zlib.compress(s.encode())
        return base64.b64encode(zs)

    def from_string(self, dump):
        """
        Populates the tree from a sparse b64-encoded dump.
        Assumes all data is at leaf nodes.
        """
        # TODO
        j = base64.b64decode(dump)
        q = zlib.decompress(j)
        r = json.loads(q)

        self.hashes = {}
        self.n_elements = 0

        for k in r:
            if k == 'max_depth':
                self.max_depth = r[k]
            else:
                n, depth = eval(k)
                self.add_node(n, depth, r[k], hash=False)
            # w = int_to_binarray(int(k), self.max_depth)
            # self.hashes[tuple(w)] = r[k]
            # self.n_elements += 1