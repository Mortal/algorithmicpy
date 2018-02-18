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
            self.assertEqual(value, ast.dump(mo[var], annotate_fields=False))
        return mo

    def test_basic(self):
        self.positive('x / 2', '(2+4) / 2',
                      x="BinOp(Num(2), Add(), Num(4))")


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
