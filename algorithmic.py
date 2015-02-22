import re
import ast
import argparse


class Visitor(ast.NodeVisitor):
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
            ast.USub: '-',
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

    ## Top level

    def generic_visit(self, node):
        self.unhandled.add(type(node))
        print(r'%% a %s' % (type(node).__name__,))

    def visit_Module(self, node):
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

    def visit_Return(self, node):
        print(r'\RETURN')
        self.visit(node.value)

    def visit_Assign(self, node):
        print(r'\STATE $', end='')
        print(', '.join(self.tex_variable(name.id)
                        for name in node.targets))
        print(r'\gets', end=' ')
        self.visit(node.value)
        print(r'$')

    def visit_AugAssign(self, node):
        print(r'\STATE $', end='')
        self.visit(node.target)
        print(r'\mathbin{{%s}{=}}' % (self.operator(node.op),))
        self.visit(node.value)
        print('$')

    def visit_For(self, node):
        if node.iter.func.id == 'range':
            print(r'\FOR{$', end='')
            self.visit(node.target)
            print(r'=', end=' ')
            args = node.iter.args
            if len(args) == 0:
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

    def visit_Call(self, node):
        if node.func.id == 'len':
            print(r'\left|', end=' ')
            self.visit(node.args[0])
            print(r'\right|', end=' ')
        else:
            print(self.tex_function_name(node.func.id), end='')
            print('(')
            for i, arg in enumerate(node.args):
                if i > 0:
                    print(',')
                self.visit(arg)
            print('')
            print(')', end=' ')

    def visit_BinOp(self, node):
        self.visit(node.left)
        print(self.operator(node.op), end=' ')
        self.visit(node.right)

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

    def visit_Subscript(self, node):
        self.visit(node.value)
        print('[', end='')
        self.visit(node.slice)
        print(']', end=' ')

    def visit_Index(self, node):
        self.visit(node.value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    with open(args.filename) as fp:
        o = ast.parse(fp.read(), args.filename, 'exec')
    visitor = Visitor()
    visitor.visit(o)


if __name__ == "__main__":
    main()
