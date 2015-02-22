import ast
import argparse


class Visitor(ast.NodeVisitor):
    @staticmethod
    def tex_function_name(name):
        tex = name.replace('_', ' ').title().replace(' ', '-')
        return r'\textsc{%s}' % (tex,)

    @staticmethod
    def tex_variable(v):
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

    def visit_Return(self, node):
        print(r'\RETURN')
        self.visit(node.value)

    def generic_visit(self, node):
        print(r'%% a %s' % (type(node).__name__,))

    def visit_Module(self, node):
        for child in node.body:
            self.visit(child)

    def visit_Name(self, node):
        print(self.tex_variable(node.id))

    def visit_Assign(self, node):
        print(r'\STATE', end=' ')
        print(', '.join(self.tex_variable(name.id)
                        for name in node.targets))
        print(r'\gets')
        self.visit(node.value)

    def visit_AugAssign(self, node):
        print(r'\STATE', end=' ')
        self.visit(node.target)
        print(self.operator(node.op) + '=')
        self.visit(node.value)

    def visit_Call(self, node):
        if node.func.id == 'len':
            print(r'\left|')
            self.visit(node.args[0])
            print(r'\right|')
        else:
            self.visit(node.func)
            print('(')
            for i, arg in enumerate(node.args):
                if i > 0:
                    print(',')
                self.visit(arg)
            print(')')

    def visit_Num(self, node):
        print(node.n)

    @staticmethod
    def operator(operator):
        ops = {
            ast.Mult: '*',
            ast.Add: '+',
            ast.USub: '-',
        }
        return ops[type(operator)]

    def visit_BinOp(self, node):
        self.visit(node.left)
        print(self.operator(node.op))
        self.visit(node.right)

    def visit_UnaryOp(self, node):
        print(self.operator(node.op))
        self.visit(node.operand)

    def visit_List(self, node):
        print(r'\larr')
        for i, child in enumerate(node.elts):
            if i > 0:
                print(',')
            self.visit(child)
        print(r'\rarr')

    def visit_Subscript(self, node):
        self.visit(node.value)
        print('[')
        self.visit(node.slice)
        print(']')

    def visit_Index(self, node):
        self.visit(node.value)

    def visit_For(self, node):
        if node.iter.func.id == 'range':
            print(r'\FOR{$')
            self.visit(node.target)
            print(r'=')
            args = node.iter.args
            if len(args) == 0:
                print(r'0 \TO')
                self.visit(args[0])
                print(r'- 1')
            else:
                self.visit(args[0])
                print(r'\TO')
                self.visit(args[1])
                print(r'- 1')
                if len(args) >= 3:
                    print(r'\text{skipping $')
                    self.visit(args[2])
                    print(r'$}')
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
