import re
import ast
import sys
import argparse


class Visitor(ast.NodeVisitor):
    def __init__(self, source):
        self._source_lines = source.split('\n')

    @staticmethod
    def tex_function_name(name):
        if name in 'max'.split():
            return r'\mathrm{%s}' % (name,)
        else:
            tex = name.replace('_', ' ').title().replace(' ', '-')
            return r'\textsc{%s}' % (tex,)

    @staticmethod
    def tex_variable(v):
        o = re.fullmatch(r'(.*?)(\d+)', v)
        if o:
            vv = Visitor.tex_variable(o.group(1))
            if len(o.group(2)) == 1:
                return r'%s_%s' % (vv, o.group(2))
            else:
                return r'%s_{%s}' % (vv, o.group(2))
        if len(v) == 1:
            return v
        else:
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
            ast.Sub: '-',
            ast.USub: '-',
            ast.NotEq: r'\ne',
            ast.Eq: r'\eq',
            ast.Gt: '>',
            ast.And: r'\land',
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
    def name_eq(node, name):
        try:
            return node.id == name
        except AttributeError:
            return False

    ## Top level

    def visit(self, node):
        try:
            return super(Visitor, self).visit(node)
        except:
            try:
                lineno = node.lineno
                col_offset = node.col_offset
            except AttributeError:
                lineno = col_offset = None
            print('At node %s' % node, file=sys.stderr)
            if lineno is not None and lineno > 0:
                print(self._source_lines[lineno - 1], file=sys.stderr)
                print(' ' * col_offset + '^', file=sys.stderr)
            raise

    def generic_visit(self, node):
        self.unhandled.add(type(node))
        print(r'%% a %s' % (type(node).__name__,))

    def visit_Module(self, node):
        print(r'\providecommand{\eq}{=}')
        print(r'\providecommand{\emptystring}{\text{empty string}}')
        self.unhandled = set()
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                self.visit(child)
            else:
                print(r'\begin{algorithmic}[1]')
                self.visit(child)
                print(r'\end{algorithmic}')
        if self.unhandled:
            print("% Not handled:")
            for n in sorted(t.__name__ for t in self.unhandled):
                print("%% %s" % (n,))

    def visit_FunctionDef(self, node):
        print(r"\begin{algorithm}")
        print(r"\caption{$%s(%s)$}" %
              (self.tex_function_name(node.name),
               self.tex_arguments(node.args)))
        print(r'\begin{algorithmic}[1]')
        for child in node.body:
            self.visit(child)
        print(r'\end{algorithmic}')
        print(r'\end{algorithm}')

    ## Statements

    def visit_Expr(self, node):
        print(r'\STATE')
        print('$', end='')
        self.visit(node.value)
        print('$')

    def visit_Return(self, node):
        print(r'\RETURN')
        print('$', end='')
        self.visit(node.value)
        print('$')

    def visit_Assign(self, node):
        print(r'\STATE $', end='')
        for i, arg in enumerate(node.targets):
            if i > 0:
                print(',')
            self.visit(arg)
        print(r'\gets', end=' ')
        self.visit(node.value)
        print(r'$')

    def visit_AugAssign(self, node):
        print(r'\STATE $', end='')
        self.visit(node.target)
        print(r'\mathbin{{%s}{=}}' % (self.operator(node.op),))
        self.visit(node.value)
        print('$')

    def visit_If(self, node, macro='IF'):
        print(r'\%s{$' % macro, end='')
        self.visit(node.test)
        print('$}')
        for child in node.body:
            self.visit(child)
        if node.orelse:
            if len(node.orelse) == 1 and type(node.orelse[0]) == type(node):
                self.visit_If(node.orelse[0], macro='ELSIF')
                # Recursion prints ENDIF; return here
                return
            else:
                print(r'\ELSE')
                for child in node.orelse:
                    self.visit(child)
        print(r'\ENDIF')

    def visit_While(self, node, macro='IF'):
        print(r'\WHILE{$', end='')
        self.visit(node.test)
        print('$}')
        for child in node.body:
            self.visit(child)
        print(r'\ENDWHILE')

    def visit_For(self, node):
        if self.name_eq(node.iter.func, 'range'):
            print(r'\FOR{$', end='')
            self.visit(node.target)
            print(r'=', end=' ')
            args = node.iter.args
            if len(args) == 1:
                print(r'0$ \TO $', end='')
                self.visit(args[0])
                print(r'- 1', end='')
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
            print(r'\FOR{$')
            self.visit(node.target)
            print(r'\in')
            self.visit(node.iter)
            print('$}')
        for child in node.body:
            self.visit(child)
        print(r'\ENDFOR')

    ## Expressions

    def visit_Name(self, node):
        print(self.tex_variable(node.id), end=' ')

    def visit_Num(self, node):
        print(node.n, end=' ')

    def visit_Str(self, node):
        if node.s:
            print("\\verb+%s+" % node.s, end=' ')
        else:
            print("\\emptystring", end=' ')

    def visit_Attribute(self, node):
        self.visit(node.value)
        print('.', end=' ')
        print(self.tex_variable(node.attr), end=' ')

    def visit_Call(self, node):
        if self.name_eq(node.func, 'len'):
            print(r'\left|', end=' ')
            self.visit(node.args[0])
            print(r'\right|', end=' ')
        else:
            self.visit(node.func)
            if node.args:
                print('(')
                for i, arg in enumerate(node.args):
                    if i > 0:
                        print(',')
                    self.visit(arg)
                print('')
                print(')', end=' ')
            else:
                print('()')

    def visit_Compare(self, node):
        self.visit(node.left)
        for op, right in zip(node.ops, node.comparators):
            print(self.operator(op), end=' ')
            self.visit(right)

    def visit_BinOp(self, node):
        self.visit(node.left)
        print(self.operator(node.op), end=' ')
        self.visit(node.right)

    def visit_BoolOp(self, node):
        self.visit(node.values[0])
        for v in node.values[1:]:
            print(self.operator(node.op), end=' ')
            self.visit(v)

    def visit_UnaryOp(self, node):
        print(self.operator(node.op), end='')
        self.visit(node.operand)

    def visit_List(self, node):
        matrix = self.matrix_entries(node)
        if matrix:
            print(r'\begin{pmatrix}')
            for row in matrix:
                for j, cell in enumerate(row):
                    if j > 0:
                        print('&', end=' ')
                    if isinstance(cell, ast.Num):
                        print(r'\phantom{-}', end='')
                    self.visit(cell)
                print(r'\\')
            print(r'\end{pmatrix}')
        else:
            print(r'\langle')
            for i, child in enumerate(node.elts):
                if i > 0:
                    print(',', end=' ')
                self.visit(child)
            print('')
            print(r'\rangle', end=' ')

    def visit_Tuple(self, node):
        print(r'(')
        for i, child in enumerate(node.elts):
            if i > 0:
                print(',', end=' ')
            self.visit(child)
        print('')
        print(r')', end=' ')

    def visit_Subscript(self, node):
        self.visit(node.value)
        print('[', end='')
        if isinstance(node.slice, ast.Index) and isinstance(node.slice.value, ast.Tuple):
            for i, child in enumerate(node.slice.value.elts):
                if i > 0:
                    print(',', end=' ')
                self.visit(child)
        else:
            self.visit(node.slice)
        print(']', end=' ')

    def visit_Index(self, node):
        self.visit(node.value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    with open(args.filename) as fp:
        source = fp.read()
    o = ast.parse(source, args.filename, 'exec')
    visitor = Visitor(source)
    visitor.visit(o)


if __name__ == "__main__":
    main()
