import io
import ast
import unittest
import functools
from algorithmic import Visitor


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
