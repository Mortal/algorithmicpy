GLOBALS = 'Node'.split()
PATTERNS = [
    ('Node(i, i)', r'\text{node representing the empty suffix}'),
    ('Node(i, len(x))', r'\text{node representing $#x[#i \ldots end]$}'),
    ('Node(i, j)', r'\text{node representing $x[#i \ldots #j-1]$}'),
    ('x = list(x) + [None]', r"\STATE \text{add sentinel character ``\$'' to $#x$}"),
]

class Node:
    def __init__(self, i, j, c=None):
        self.i = i
        self.j = j
        self.suffix_link = None
        if c is None:
            self.c = {}
        else:
            self.c = c

    def __repr__(self):
        return "Node(%r, %r, c=%r)" % (self.i, self.j, self.c)

    def __str__(self):
        if self.c:
            return "(%s, %s, %s)" % (
                self.i, self.j,
                ', '.join('%s->%s' % (k, v) for k, v in self.c.items()))
        else:
            return "[%s, %s]" % (self.i, self.j)


def common_prefix(root, x, i):
    k = 0
    while root.i + k < root.j and i + k < len(x) and x[root.i + k] == x[i + k]:
        k += 1
    return k


def search(u, x, i, j, end):
    while True:
        if x[i] not in u.c:
            return u, i
        v = u.c[x[i]]
        v_j = end if v.j == len(x) else v.j
        k = 0
        while v.i + k < v.j and i + k < j and x[v.i + k] == x[i + k]:
            k += 1
        assert v.i + k == v.j or i + k == j or x[v.i + k] != x[i + k]
        if v.i + k == v.j and i + k < j:
            u = v
            i = i + k
        else:
            return u, i


# map from first char to path
def insert(root, x, i):
    # print("Insert %r into %s" % (x[i:], root))
    k = common_prefix(root, x, i)
    if k == 0 and x[i] not in root.c:
        # print("Add new child %r of root" % (x[i],))
        root.c[x[i]] = Node(i, len(x))
    elif k == root.j - root.i:
        if x[i + k] not in root.c:
            # print("Add new child %r of node" % (x[i + k],))
            root.c[x[i + k]] = Node(i + k, len(x))
        else:
            # print("Simply recurse")
            root.i = i
            root.j = i + k
            insert(root.c[x[i + k]], x, i + k)
    else:
        # print("Split %s %r %r" %
        #       (k, x[root.i:root.i+k], x[root.i+k:root.j]))
        old = Node(root.i + k, root.j)
        old.c = root.c
        root.i = i
        root.j = i + k
        root.c = {}
        root.c[x[old.i]] = old
        root.c[x[i + k]] = Node(i + k, len(x))
        # print(root)


def _node_name(x, n):
    return '%s,%s' % (_node_label(x, n), ''.join('$' if i == len(x) else x[i] for i in range(n.i, n.j)))


def _node_label(x, n):
    if n.i == n.j:
        return ''
    else:
        return '%s,%s' % (n.i, n.j - 1)


def _print_trie(root, x, path=''):
    # print("VISIT", root)
    # print('RECURSE', ' '.join(map(str, root.c.keys())))
    print("subgraph \"cluster_%s\" { color=white; " % (path,))
    if root.c:
        shape = 'ellipse'
    else:
        shape = 'box'
    print("\"%s%s\" [label=\"%s\", margin=0, shape=%s, fontsize=22];" %
          (path, _node_name(x, root), _node_label(x, root), shape))
    for k, c in root.c.items():
        # print("RECURSE", k)
        _print_trie(c, x, path + (k or '$'))
    # print('EDGE', ' '.join(map(str, root.c.keys())))
    for k, c in root.c.items():
        # print("EDGE", k)
        print("\"%s%s\" -> \"%s%s%s\" [arrowhead=none];" %
              (path, _node_name(x, root), path, k or '$', _node_name(x, c)))
    print("}")
    # print("DONE", root)


def suffix_trie(x):
    x = list(x) + [None]
    root = Node(len(x), len(x))
    for i in range(1, len(x)):
        insert(root, x, len(x) - 1 - i)
    return root


def suffix_trie_2(x):
    x = list(x) + [None]
    end = len(x)
    root = Node(0, 0)
    root.c[x[0]] = Node(0, end)
    j = k = 0
    y = root
    y_d = 0
    # y is the parent of the path corresponding to x[0:i].
    # y corresponds to the path x[0:y_d], and the child
    # y.c[x[y_d]]
    # "root" now represents an implicit suffix tree for x[0:1].
    for i in range(1, len(x) + 1):
        assert y.c[x[y_d]] is search(root, x, 0, i, i)[0]

        # Extend "root" to represent an implicit suffix tree for x[0:i+1].
        # Suffixes x[0:i],...,x[j-1:i] are leaves, so they are
        # implicitly extended to x[0:i+1],...,x[j-1:i+1].
        while j < i:
            if j == 0:
                # Add path x[0:i+1] implicitly.
                j = j + 1
            elif j == 1:
                # Add path x[1:i+1].
                if y is root:
                    v, v_i = search(root, x, j, i, i)
                else:
                    v, v_i = search(y.suffix_link, x, j + y_d, i, i)
                    v = y.suffix_link
                    v_i = y_d
        v = first_suffix_node
        # v is the path x[j:k].
        # v is the parent of the path with label x[j:i].
        # v is either the root (j == k) or it has a suffix link (j < k).
        assert (v is root or v.suffix_link is not None)
        if v is root:
            v = search(root, x, j, i+1)


x = 'minimize minime'
print('digraph {')
print('graph [pad="0", ranksep="0.0", nodesep="0.0", splines=line];')
_print_trie(suffix_trie(x), x)
print('}')
