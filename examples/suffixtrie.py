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

    @property
    def length(self):
        if self.j is None:
            return float('inf')
        else:
            return self.j - self.i

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
    root = Node(0, 0)
    root.c[x[0]] = Node(0, None)
    suffixes = []

    for i in range(len(x) + 1):
        # We have constructed the suffix trie for x[0:i].
        for j, (v, a) in enumerate(suffixes):
            print("Suffix [%s:%s] " % (j, i) + ''.join(x[j:i]) +
                  " ends in node %s " % (v,) +
                  "which is at a distance %s from the root" % a)
            # a is the number of characters on the path from the root
            # to the beginning of the node v.
            prev_suffix_length = i - j
            # Where in x[v.i:v.j] does suffix x[j:i] end?
            prev_suffix_end = prev_suffix_length - a
            # Note, prev_suffix_end - 1 == v.length means that
            # the last character in x[j:i] is an edge out of v.
            # prev_suffix_end == 0 is not allowed.
            assert 0 < prev_suffix_end <= v.length + 1, (i, j, a, v.length)
            # Advance (v, a)
            if prev_suffix_end == v.length + 1:
                a += v.length
                next_suffix_end = 2
                v = v.c[x[i-1]]
                print("Advance to child", v, "at distance", a)
            else:
                assert x[v.i + prev_suffix_end - 1] == x[i-1]
                next_suffix_end = prev_suffix_end + 1

            assert 0 < next_suffix_end <= v.length + 1
            if next_suffix_end == v.length + 1:
                if x[i] in v.c:
                    print(i, j, "Outgoing edge exists")
                    exists = True
                else:
                    exists = False
                    v.c[x[i]] = Node(i, None)
                    print(i, j, "Create outgoing edge", v)
            else:
                if x[v.i + next_suffix_end - 1] == x[i]:
                    print(i, j, "Next character in current substring")
                    exists = True
                    # Leave v unchanged
                else:
                    # Split node
                    print(i, j, "Split node", v)
                    exists = False
                    child = Node(v.i + prev_suffix_end, v.j)
                    v.j = v.i + next_suffix_end - 1
                    child.c = v.c
                    v.c = {x[v.i + next_suffix_end - 1]: child,
                           x[i]: Node(i, None)}
                    print("Into", v, child)
            print("Root is", root, "update", j, "to", v, a)
            print('  '.join('%s %s' % (v, a) for v, a in suffixes))
            print(', '.join([str(id(v)) for v, a in suffixes]))
            suffixes[j] = (v, a)
            print(', '.join([str(id(v)) for v, a in suffixes]))
            # if exists:
            #     break
        suffixes.append((root, 0))
        root.c.setdefault(x[i], Node(i, None))
    return root


x = 'cacao'
print('digraph {')
print('graph [pad="0", ranksep="0.0", nodesep="0.0", splines=line];')
_print_trie(suffix_trie_2(x), x)
print('}')
