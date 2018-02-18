import io
import ast
import unittest
import functools
from algorithmic import Visitor, pattern_match


class PatternMatchTest(unittest.TestCase):
    def positive(self, pattern, text, **matches):
        mo = pattern_match(ast.parse(pattern), ast.parse(text))
        self.assertTrue(mo)
        for var, value in matches.items():
            self.assertIn(var, mo.keys())
            if isinstance(mo[var], list):
                rep = [ast.dump(v, annotate_fields=False)
                       for v in mo[var]]
            else:
                rep = ast.dump(mo[var], annotate_fields=False)
            self.assertEqual(value, rep)
        return mo

    def negative(self, pattern, text):
        mo = pattern_match(ast.parse(pattern), ast.parse(text))
        self.assertFalse(mo)

    def test_basic(self):
        self.positive('x / 2', '(2+4) / 2',
                      x="BinOp(Num(2), Add(), Num(4))")

    def test_match_call(self):
        self.positive('a // 42', 'len(foo) // 42',
                      a="Call(Name('len', Load()), [Name('foo', Load())], [])")

    def test_match_list_arg(self):
        self.positive('len(a)', 'len([1, 2, 3])',
                      a="List([Num(1), Num(2), Num(3)], Load())")

    def test_plus_minus(self):
        self.positive('[][i:j]', '[][i+1:-i]',
                      i="BinOp(Name('i', Load()), Add(), Num(1))",
                      j="UnaryOp(USub(), Name('i', Load()))")

    def test_chained(self):
        self.negative('i < j', '1 < 2 < 3')

    def test_same(self):
        self.positive('a == a == a', 'a == a == a',
                      a="Name('a', Load())")

    def test_for_single(self):
        self.positive('for a in b: c', 'for i in range(10):\n\t1',
                      c=["Expr(Num(1))"])

    def test_for_multi(self):
        self.positive('for a in b: c', 'for i in range(10):\n\t1\n\t2',
                      c=["Expr(Num(1))", "Expr(Num(2))"])


class AlgorithmicpyTest(unittest.TestCase):
    def runner(self, py, tex):
        buf = io.StringIO()
        visitor = Visitor(print=functools.partial(print, file=buf),
                          source=py)
        visitor.visit(ast.parse(py).body[0])
        self.assertEqual(buf.getvalue().rstrip('\n'), tex)

    def test_assert(self):
        self.runner('assert 42', r'\STATE $\{42\}$')

    def test_return(self):
        self.runner('return 42', r'\RETURN $42$')

    def test_continue(self):
        self.runner('continue', r'\STATE \textbf{continue}')


if __name__ == '__main__':
    unittest.main()
