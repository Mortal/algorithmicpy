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


x = 'minimize minime'
print('digraph {')
print('graph [pad="0", ranksep="0.0", nodesep="0.0", splines=line];')
_print_trie(suffix_trie(x), x)
print('}')
