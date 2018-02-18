import re
import ast


def node_eq(a, b):
    """
    >>> e = ast.parse('i+1 == i+1', mode='eval').body
    >>> isinstance(e, ast.Compare)
    True
    >>> left, (right,) = e.left, e.comparators
    >>> node_eq(left, right)
    True

    >>> e, = ast.parse('i = i', mode='single').body
    >>> isinstance(e, ast.Assign)
    True
    >>> (left,), right = e.targets, e.value
    >>> node_eq(left, right)
    True
    """
    return bool(pattern_match_rec(a, b))


def pattern_match(a, b, globals=None):
    """
    Return a dict mapping each ast.Name in `a` to an ast.AST node in `b`,
    or None if `b` does not have the same shape as `a`.

    Example of positive match where `x` is matched by `(2+4)`:

    >>> print(pattern_match(ast.parse('x / 2'), ast.parse('(2+4) / 2')))
    ... # doctest: +ELLIPSIS
    {'x': <_ast.BinOp object at 0x...>}

    Example of negative match:

    >>> print(pattern_match(ast.parse('2 + 2'), ast.parse('4')))
    None

    Some more examples, using a helper function to dump the ASTs:

    >>> def pattern_match_help(a, b, globals):
    ...     m = pattern_match(ast.parse(a), ast.parse(b), globals)
    ...     if m is None:
    ...         return print("No match")
    ...     for k in sorted(m.keys()):
    ...         print("%s: %s" % (k, ast.dump(m[k], annotate_fields=False)))

    >>> pattern_match_help('a // 42', 'len(foo) // 42', [])
    a: Call(Name('len', Load()), [Name('foo', Load())], [])
    >>> pattern_match_help('len(a)', 'len([1, 2, 3])', ['len'])
    a: List([Num(1), Num(2), Num(3)], Load())
    >>> pattern_match_help('[][i:j]', '[][i+1:-i]', [])
    i: BinOp(Name('i', Load()), Add(), Num(1))
    j: UnaryOp(USub(), Name('i', Load()))
    >>> pattern_match_help('i < j', '1 < 2 < 3', [])
    No match
    >>> pattern_match_help('a == a == a', 'a == a == a', [])
    a: Name('a', Load())
    """

    if globals is None:
        globals = []
    bindings = {}

    def unify(name, value):
        if name.id in globals:
            binding = name
        else:
            binding = bindings.setdefault(name.id, value)
        return node_eq(binding, value)

    result = pattern_match_rec(a, b, unify)
    if result:
        return bindings


def pattern_match_rec(a, b, unify=None):
    if unify and isinstance(a, ast.Name):
        return unify(a, b)
    if type(a) != type(b):
        return False
    if isinstance(a, (int, str, bool)) or a is None:
        return a == b
    if isinstance(a, list):
        return (len(a) == len(b) and
                all(pattern_match_rec(c, d, unify) for c, d in zip(a, b)))
    assert isinstance(a, ast.AST) and isinstance(b, ast.AST)
    try:
        a_lit = ast.literal_eval(a)
    except ValueError:
        pass
    else:
        try:
            return a_lit == ast.literal_eval(b)
        except ValueError:
            return False
    for f in a._fields:
        if f == 'ctx':
            continue
        x = getattr(a, f)
        y = getattr(b, f)
        if f == 'body':
            assert isinstance(x, list)
            assert isinstance(y, list)
            assert len(x) >= 1
            assert len(y) >= 1
        is_name = (f == 'body' and isinstance(x[0], ast.Expr) and
                   isinstance(x[0].value, ast.Name))
        if f == 'body' and unify and is_name:
            if not unify(x[0].value, y):
                return False
        else:
            if not pattern_match_rec(x, y, unify):
                return False
    return True


def _str_sub(repl, expr, matches, print, visit):
    i = 0
    for mo in re.finditer('#(\w+)', repl):
        j = mo.start(0)
        if i != j:
            print(repl[i:j], end='')
        i = mo.end(0)
        visit(matches[mo.group(1)])
    j = len(repl)
    if i != j:
        print(repl[i:j], end='')
    if not expr:
        print('')
    return True


class Pattern:
    def __init__(self, node, is_expr, globals):
        assert isinstance(node, ast.AST)
        assert isinstance(is_expr, bool)
        self.node = node
        self.is_expr = is_expr
        self.globals = globals
        self.source = None

    @classmethod
    def compile(cls, pattern, *, globals=None):
        node = ast.parse(pattern, mode='single').body[0]
        if isinstance(node, ast.Expr):
            node = node.value
            is_expr = True
        else:
            is_expr = False
        po = cls(node, is_expr, globals)
        po.source = pattern
        return po

    def __repr__(self):
        if self.source is not None:
            return ('Pattern.compile(%r, globals=%r)' %
                    (self.source, self.globals))
        else:
            return '<Pattern>'

    def match(self, target):
        return pattern_match(self.node, target, globals=self.globals)

    def sub(self, target, repl, **kwargs):
        mo = self.match(target)
        if mo is not None:
            if isinstance(repl, str):
                return _str_sub(repl, self.is_expr, mo, **kwargs)
            else:
                return repl(**kwargs)
