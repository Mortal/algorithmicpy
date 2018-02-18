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


if __name__ == '__main__':
    unittest.main()
