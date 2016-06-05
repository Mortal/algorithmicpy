import re
import ast
import sys
import argparse
import functools


class VisitorBase(ast.NodeVisitor):
    dump_unhandled = False

    def __init__(self, source):
        self._source_lines = source.split('\n')
        self.unhandled = set()

    def visit(self, node):
        if isinstance(node, list):
            for x in node:
                self.visit(x)
            return
        try:
            return super(VisitorBase, self).visit(node)
        except Exception:
            self.source_backtrace(node, sys.stderr)
            raise

    def source_backtrace(self, node, file):
        try:
            lineno = node.lineno
            col_offset = node.col_offset
        except AttributeError:
            lineno = col_offset = None
        print('At node %s' % node, file=file)
        if lineno is not None and lineno > 0:
            print(self._source_lines[lineno - 1], file=file)
            print(' ' * col_offset + '^', file=file)

    def generic_visit(self, node):
        if self.dump_unhandled and type(node) not in self.unhandled:
            self.source_backtrace(node, sys.stderr)
            print("%s unhandled" % (type(node).__name__,), file=sys.stderr)
        self.unhandled.add(type(node).__name__)

    def visit_children(self, node):
        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def visit_Module(self, node):
        self.visit_children(node)


def node_eq(a, b):
    """
    >>> e = ast.parse('i+1 == i+1', mode='eval').body
    >>> isinstance(e, ast.Compare)
    True
    >>> left, (right,) = e.left, e.comparators
    >>> node_eq(left, right)
    True
    """
    m = pattern_match(a, b)
    if m is None:
        return False
    return all(k == v.id for k, v in m.items())


def pattern_match(a, b, globals=None):
    """
    >>> def pattern_match_help(a, b, **kwargs):
    ...     m = pattern_match(ast.parse(a, mode='eval').body,
    ...                       ast.parse(b, mode='eval').body, **kwargs)
    ...     if m is None:
    ...         return
    ...     return [(k, type(m[k]).__name__) for k in sorted(m.keys())]
    >>> pattern_match_help('a // b', 'len(foo) // 42')
    [('a', 'Call'), ('b', 'Num')]
    >>> pattern_match_help('len(a)', 'len([1, 2, 3])', globals=['len'])
    [('a', 'List')]
    >>> pattern_match_help('[][i:i]', '[][i+1:i+1]', globals=['len'])
    [('i', 'BinOp')]
    """
    if globals is None:
        globals = []
    bindings = {}
    try:
        result = pattern_match_rec(a, b, globals, bindings)
    except Exception:
        print(ast.dump(a, annotate_fields=False),
              ast.dump(b, annotate_fields=False), file=sys.stderr)
        raise
    if not result:
        return None
    return bindings


def pattern_match_rec(a, b, globals, bindings):
    args = (globals, bindings)
    if isinstance(a, ast.Name) and a.id not in globals:
        try:
            ex = bindings[a.id]
        except KeyError:
            bindings[a.id] = b
        else:
            if not node_eq(b, ex):
                # print("Unification with %s failed" % a.id, file=sys.stderr)
                return False
        return True
    if type(a) != type(b):
        return False
    if isinstance(a, (int, str)):
        return a == b
    if isinstance(a, list):
        return (len(a) == len(b) and
                all(pattern_match_rec(c, d, *args) for c, d in zip(a, b)))
    if a is None:
        return True
    try:
        a_lit = [ast.literal_eval(a)]
    except ValueError:
        a_lit = None
    try:
        b_lit = [ast.literal_eval(b)]
    except ValueError:
        b_lit = None
    if a_lit == b_lit and a_lit is not None:
        return True
    for f in a._fields:
        try:
            if not pattern_match_rec(getattr(a, f), getattr(b, f), *args):
                return False
        except Exception:
            print(ast.dump(a, annotate_fields=False),
                  ast.dump(b, annotate_fields=False), file=sys.stderr)
            raise
    return True


PATTERNS = [
    ("inf = float('inf')",
     r"\STATE let ``$\infty$'' be positive infinity"),
    ("float('inf')", r"\infty"),
    ("None", r"\textsc{nil}"),
    ("a // b", r"\lfloor #a / #b \rfloor "),
    ("len(a)", r"|#a|"),
    ("min(a, b)", r"\min\{#a, #b\}"),
    ("max(a, b)", r"\max\{#a, #b\}"),
    ("inf", r'\infty '),
    ("a[0:0] = b", r"\STATE insert $#b$ at the beginning of $#a$"),
    ("a[i:i] = b", r"\STATE insert $#b$ just before $#a[#i]$"),
    ("a[0:1] = []", r"\STATE remove first element of $#a$"),
    ("a[-1:] = []", r"\STATE remove last element of $#a$"),
    ("a[-2:] = []", r"\STATE remove last two elements of $#a$"),
    ('a = [None] + list(a)', r'\STATE insert sentinel element $#a[0]$'),
    ("a.extend([b[-1]])",
     r"\text{insert the last element of $#b$ at the end of $#a$}"),
    ("a.extend(b)", r"\text{insert $#b$ at the end of $#a$}"),
    ("a.append(b)", r"\text{insert $#b$ at the end of $#a$}"),
    ("a[:i]", r"#a[0\dots #i)"),
    ("a[i:]", r"#a[#i \dots \text{end})"),
    ("a[-1]", r"#a[\text{end}]"),
    ("[[0] * m for i in range(n)]",
     r"\text{a $#n \times #m$ matrix of zeros}"),
    ("[[None] * m for i in range(n)]",
     r"\text{an empty $#n \times #m$ matrix}"),
    ("[0] * n",
     r"\text{an array of $#n$ zeros}"),
    ("print(v)", r"\text{output $#v$}"),
    ("{}", r"\text{empty dictionary}"),
    ("S - {x}", r"#S \setminus \{#x\}"),
    ("True", r"\top "),
    ("False", r"\bot "),
    ("(a and b) or (c and d)", r"(#a \land #b) \lor (#c \land #d)"),
    ('set()', r'\emptyset '),
    ('Set()', r'\emptyset '),
    ('Set(a)', r'\{#a\}'),
    ('Set(a, b)', r'\{#a, #b\}'),
    ('s.add(x)', r'#s = #s \cup \{#x\}'),
    ('s.union(t)', r'#s \cup #t'),
    ('set(itertools.product(x, y))', r'#x \times #y'),
    ('x.reverse()', r'\text{reverse $#x$}'),
]

GLOBALS = 'len min max inf float print set Set range'.split()

VARS = {
    'sigma': r'\sigma ',
    'Sigma': r'\Sigma ',
    'delta': r'\delta ',
    'pi': r'\pi ',
}


def str_sub(repl, expr, matches, print, visit):
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
                return str_sub(repl, self.is_expr, mo, **kwargs)
            else:
                return repl(**kwargs)


class Visitor(VisitorBase):
    def __init__(self, *args, **kwargs):
        self.print = kwargs.pop('print', print)
        super().__init__(*args, **kwargs)
        self.patterns = []
        self.globals = frozenset(GLOBALS)
        self.extend_patterns(PATTERNS)

    def extend_patterns(self, patterns):
        self.patterns = [
            (Pattern.compile(k, globals=self.globals), v)
            for k, v in patterns
        ] + self.patterns

    @staticmethod
    def tex_function_name(name):
        tex = name.replace('_', ' ').title().replace(' ', '-')
        return r'\textsc{%s}' % (tex,)

    @staticmethod
    def tex_variable(v):
        o = re.fullmatch(r'(.*?)(?:_(.)|(\d+))', v)
        if o:
            vv = Visitor.tex_variable(o.group(1))
            if o.group(2):
                return r'%s_%s' % (vv, o.group(2))
            else:
                return r'%s_{%s}' % (vv, o.group(3))
        if v.endswith('_prime'):
            return "%s'" % Visitor.tex_variable(v[:-6])
        if len(v) == 1:
            return v
        elif '_' in v:
            return Visitor.tex_function_name(v)
        else:
            try:
                return VARS[v]
            except KeyError:
                return r'\textit{%s}' % v

    @staticmethod
    def tex_arguments(args):
        return ', '.join(
            Visitor.tex_variable(arg.arg)
            for arg in args.args
        )

    @staticmethod
    def operator(operator):
        ops = {
            ast.Mult: '*',
            ast.Add: '+',
            ast.UAdd: '{+}',
            ast.Sub: '-',
            ast.Div: '/',
            ast.FloorDiv: '//',
            ast.Mod: r'\bmod',
            ast.USub: '{-}',
            ast.NotEq: r'\ne',
            ast.Eq: r'\eq',
            ast.Lt: '<',
            ast.Gt: '>',
            ast.LtE: r'\leq',
            ast.GtE: r'\geq',
            ast.And: r'\land',
            ast.Or: r'\lor',
            ast.Not: r'\text{not }',
            ast.In: r'\in',
            ast.NotIn: r'\not\in',
            ast.BitOr: r'\cup',
        }
        return ops[type(operator)]

    @staticmethod
    def matrix_entries(node):
        if not isinstance(node, ast.List):
            return
        if not all(isinstance(child, ast.List) for child in node.elts):
            return
        rows = [
            child.elts
            for child in node.elts
        ]
        if any(len(row) != len(rows[0]) for row in rows):
            return
        else:
            return rows

    @staticmethod
    def node_name(node):
        try:
            return node.id
        except AttributeError:
            return None

    @staticmethod
    def name_eq(node, name):
        return Visitor.node_name(node) == name

    def visit(self, node):
        for pattern, repl in self.patterns:
            if pattern.sub(node, repl, print=self.print, visit=self.visit):
                break
        else:
            super().visit(node)

    ## Top level

    def visit_Module(self, node):
        print = self.print
        print(r'\providecommand{\eq}{=}')
        print(r'\providecommand{\emptystring}{\text{empty string}}')
        po_pattern = Pattern.compile('PATTERNS = p', globals={'PATTERNS'})
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                self.visit(child)
            elif po_pattern.match(child):
                p = ast.literal_eval(po_pattern.match(child)['p'])
                self.extend_patterns(p)
            # else:
            #     print(r'\begin{algorithmic}[1]')
            #     self.visit(child)
            #     print(r'\end{algorithmic}')
        if self.unhandled:
            print("% Not handled:")
            for n in sorted(self.unhandled):
                print("%% %s" % (n,))

    def visit_FunctionDef(self, node):
        if node.name.startswith('_'):
            return
        print = self.print
        print(r"\begin{algorithm}")
        print(r"\caption{$%s(%s)$}" %
              (self.tex_function_name(node.name),
               self.tex_arguments(node.args)))
        print(r'\begin{algorithmic}[1]')
        for i, child in enumerate(node.body):
            if i == 0 and self.is_docstring(child):
                continue
            self.visit(child)
        print(r'\end{algorithmic}')
        print(r'\end{algorithm}')

    def is_docstring(self, node):
        return type(node) == ast.Expr and type(node.value) == ast.Str

    ## Statements

    def visit_Expr(self, node):
        print = self.print
        print(r'\STATE', end=' ')
        if isinstance(node.value, ast.Str):
            print(node.value.s)
        else:
            print('$', end='')
            self.visit(node.value)
            print('$')

    def visit_Assert(self, node):
        self.print(r'\STATE $\{', end='')
        self.visit(node.test)
        self.print('\}$')

    def visit_Return(self, node):
        self.print(r'\RETURN', end=' ')
        self.print('$', end='')
        self.visit(node.value)
        self.print('$')

    def visit_Assign(self, node):
        print = self.print
        print(r'\STATE $', end='')
        for i, arg in enumerate(node.targets):
            if i > 0:
                print(', ', end='')
            self.visit(arg)
        print(r' \gets ', end='')
        self.visit(node.value)
        print(r'$')

    def visit_AugAssign(self, node):
        self.print(r'\STATE $', end='')
        self.visit(node.target)
        self.print(r'\mathbin{{%s}{=}}' % (self.operator(node.op),))
        self.visit(node.value)
        self.print('$')

    def visit_If(self, node, macro='IF'):
        self.print(r'\%s{$' % macro, end='')
        self.visit(node.test)
        self.print('$}')
        for child in node.body:
            self.visit(child)
        if node.orelse:
            if len(node.orelse) == 1 and type(node.orelse[0]) == type(node):
                self.visit_If(node.orelse[0], macro='ELSIF')
                # Recursion prints ENDIF; return here
                return
            else:
                self.print(r'\ELSE')
                for child in node.orelse:
                    self.visit(child)
        self.print(r'\ENDIF')

    def visit_While(self, node):
        self.print(r'\WHILE{$', end='')
        self.visit(node.test)
        self.print('$}')
        for child in node.body:
            self.visit(child)
        self.print(r'\ENDWHILE')

    def visit_For(self, node):
        print = self.print
        if (isinstance(node.iter, ast.Call) and
                self.name_eq(node.iter.func, 'range')):
            print(r'\FOR{$', end='')
            self.visit(node.target)
            print(r' = ', end='')
            args = node.iter.args
            if len(args) == 1:
                print(r'0$ \TO $', end='')
                self.visit(args[0])
                print(r' - 1', end='')
            else:
                self.visit(args[0])
                print(r'$ \TO $', end='')
                self.visit(args[1])
                print(r'- 1', end='')
                if len(args) >= 3:
                    print(r'\text{skipping $', end='')
                    self.visit(args[2])
                    print(r'$}', end='')
            print('$}')
        else:
            print(r'\FOR{$', end='')
            self.visit(node.target)
            print(r'\in', end=' ')
            self.visit(node.iter)
            print('$}')
        for child in node.body:
            self.visit(child)
        print(r'\ENDFOR')

    def visit_Continue(self, node):
        self.print(r'\STATE \textbf{continue}')

    ## Expressions

    def visit_Name(self, node):
        self.print(self.tex_variable(node.id), end='')

    def visit_Num(self, node):
        self.print(node.n, end='')

    def visit_Str(self, node):
        if node.s:
            self.print("\\verb+%s+" % node.s, end='')
        else:
            self.print("\\emptystring ", end='')

    def visit_Attribute(self, node):
        self.visit(node.value)
        self.print('.', end=' ')
        self.print(self.tex_variable(node.attr), end=' ')

    def visit_Call(self, node):
        self.visit(node.func)
        if node.args:
            self.print('(', end='')
            for i, arg in enumerate(node.args):
                if i > 0:
                    self.print(',', end=' ')
                self.visit(arg)
            self.print(')', end='')
        else:
            self.print('()')

    def visit_Compare(self, node):
        self.visit(node.left)
        for op, right in zip(node.ops, node.comparators):
            self.print(' %s ' % (self.operator(op),), end='')
            self.visit(right)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.print(' %s ' % (self.operator(node.op),), end='')
        self.visit(node.right)

    def visit_BoolOp(self, node):
        self.visit(node.values[0])
        for v in node.values[1:]:
            self.print(self.operator(node.op), end=' ')
            self.visit(v)

    def visit_UnaryOp(self, node):
        self.print(self.operator(node.op), end='')
        self.visit(node.operand)

    def visit_List(self, node):
        matrix = self.matrix_entries(node)
        if matrix:
            self.print(r'\begin{pmatrix}')
            for row in matrix:
                for j, cell in enumerate(row):
                    if j > 0:
                        self.print('&', end=' ')
                    if isinstance(cell, ast.Num):
                        self.print(r'\phantom{-}', end='')
                    self.visit(cell)
                self.print(r'\\')
            self.print(r'\end{pmatrix}')
        else:
            self.visit_Tuple(node, r'\langle ', r'\rangle ')

    def visit_Set(self, node):
        self.visit_Tuple(node, r'\{', r'\}')

    def visit_Tuple(self, node, left='(', right=')'):
        self.print(left, end='')
        for i, child in enumerate(node.elts):
            if i > 0:
                self.print(',', end=' ')
            self.visit(child)
        self.print(right, end='')

    def visit_Subscript(self, node):
        self.visit(node.value)
        self.print('[', end='')
        if isinstance(node.slice, ast.Index) and isinstance(node.slice.value, ast.Tuple):
            for i, child in enumerate(node.slice.value.elts):
                if i > 0:
                    self.print(',', end=' ')
                self.visit(child)
        else:
            self.visit(node.slice)
        self.print(']', end='')

    def visit_Index(self, node):
        self.visit(node.value)


PREAMBLE = r"""
\documentclass[a4paper,oneside,article]{memoir}
\usepackage[T1]{fontenc}
\usepackage[noend]{algorithmic}
\usepackage{algorithm}
\usepackage{amsmath,amssymb}
\begin{document}
""".strip()

POSTAMBLE = r"""
\end{document}
""".strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--preamble', action='store_true')
    parser.add_argument('-3', '--new-style', action='store_true')
    parser.add_argument('filename')
    args = parser.parse_args()
    with open(args.filename) as fp:
        source = fp.read()
    o = ast.parse(source, args.filename, 'exec')
    visitor = Visitor(source)
    if args.preamble:
        print(PREAMBLE)
    if args.new_style:
        print(r'\newcommand{\eq}{==}')
        print(r'\renewcommand{\gets}{=}')
        print(r'\renewcommand{\land}{\mathbin{\text{and}}}')
        print(r'\renewcommand{\lor}{\mathbin{\text{or}}}')
    visitor.visit(o)
    if args.preamble:
        print(POSTAMBLE)


if __name__ == "__main__":
    main()
