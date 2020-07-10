import io
import os
import ast
import unittest
import functools
from algorithmic import Visitor, pattern_match, main


class PatternMatchTest(unittest.TestCase):
    def positive(self, pattern, text, **matches):
        mo = pattern_match(ast.parse(pattern), ast.parse(text))
        self.assertTrue(mo)
        for var, value in matches.items():
            self.assertIn(var, mo.keys())
            if isinstance(mo[var], list):
                rep = [ast.dump(v, annotate_fields=False) for v in mo[var]]
            else:
                rep = ast.dump(mo[var], annotate_fields=False)
            self.assertEqual(value, rep)
        return mo

    def negative(self, pattern, text):
        mo = pattern_match(ast.parse(pattern), ast.parse(text))
        self.assertFalse(mo)

    def test_basic(self):
        self.positive("x / 2", "(2+4) / 2", x="BinOp(Num(2), Add(), Num(4))")

    def test_match_call(self):
        self.positive(
            "a // 42",
            "len(foo) // 42",
            a="Call(Name('len', Load()), [Name('foo', Load())], [])",
        )

    def test_match_list_arg(self):
        self.positive(
            "len(a)", "len([1, 2, 3])", a="List([Num(1), Num(2), Num(3)], Load())"
        )

    def test_plus_minus(self):
        self.positive(
            "[][i:j]",
            "[][i+1:-i]",
            i="BinOp(Name('i', Load()), Add(), Num(1))",
            j="UnaryOp(USub(), Name('i', Load()))",
        )

    def test_chained(self):
        self.negative("i < j", "1 < 2 < 3")

    def test_same(self):
        self.positive("a == a == a", "a == a == a", a="Name('a', Load())")

    def test_for_single(self):
        self.positive("for a in b: c", "for i in range(10):\n\t1", c=["Expr(Num(1))"])

    def test_for_multi(self):
        self.positive(
            "for a in b: c",
            "for i in range(10):\n\t1\n\t2",
            c=["Expr(Num(1))", "Expr(Num(2))"],
        )

    def test_list_star_1(self):
        self.positive("[*c]", "[1, 2]", c=["Num(1)", "Num(2)"])

    def test_list_star_2(self):
        self.positive("[x, *c]", "[1, 2]", c=["Num(2)"])

    def test_list_star_3(self):
        self.positive("[*c, x]", "[1, 2]", c=["Num(1)"])

    def test_list_star_4(self):
        self.positive("[x, *c, y]", "[1, 2]", c=[])

    def test_call_args_star(self):
        self.positive("print(*x)", "print(1, 2)")


class AlgorithmicpyTest(unittest.TestCase):
    def runner(self, py, tex):
        with io.StringIO() as buf:
            visitor = Visitor(print=functools.partial(print, file=buf), source=py)
            visitor.visit(ast.parse(py).body[0])
            self.assertEqual(buf.getvalue().rstrip("\n"), tex)

    def test_assert(self):
        self.runner("assert 42", r"\STATE $\{42\}$")

    def test_return(self):
        self.runner("return 42", r"\RETURN $42$")

    def test_continue(self):
        self.runner("continue", r"\STATE \textbf{continue}")

    def test_for_range_n_plus_1(self):
        self.runner(
            "for x in range(n + 1): c", "\\FOR{$x = 0$ \\TO $n$}\n\\STATE $c$\n\\ENDFOR"
        )

    def test_for_range_n(self):
        self.runner(
            "for x in range(n): c", "\\FOR{$x = 0$ \\TO $n - 1$}\n\\STATE $c$\n\\ENDFOR"
        )

    def test_for_range_m_n_plus_1(self):
        self.runner(
            "for x in range(a, n + 1): c",
            "\\FOR{$x = a$ \\TO $n$}\n\\STATE $c$\n\\ENDFOR",
        )

    def test_for_range_m_n(self):
        self.runner(
            "for x in range(a, n): c",
            "\\FOR{$x = a$ \\TO $n - 1$}\n\\STATE $c$\n\\ENDFOR",
        )

    def test_for_range_m_n_skip_plus_1(self):
        self.runner(
            "for x in range(a, n + 1, s): c",
            "\\FOR{$x = a$ \\TO $n$ skipping $s$}\n\\STATE $c$\n\\ENDFOR",
        )

    def test_for_range_m_n_skip(self):
        self.runner(
            "for x in range(a, n, s): c",
            "\\FOR{$x = a$ \\TO $n - 1$ skipping $s$}\n\\STATE $c$\n\\ENDFOR",
        )

    def test_for_downto_minus_1(self):
        self.runner(
            "for x in range(10, n - 1, -1): c",
            "\\FOR{$x = 10$ \\DOWNTO $n$}\n\\STATE $c$\n\\ENDFOR",
        )

    def test_for_downto(self):
        self.runner(
            "for x in range(10, n, -1): c",
            "\\FOR{$x = 10$ \\DOWNTO $n + 1$}\n\\STATE $c$\n\\ENDFOR",
        )

    def test_for_in(self):
        self.runner("for a in b: c", "\\FOR{$a \\in b$}\n\\STATE $c$\n\\ENDFOR")

    def test_while(self):
        self.runner(
            "while n < 1: n = n + 1",
            "\\WHILE{$n < 1$}\n\\STATE $n \\gets n + 1$\n\\ENDWHILE",
        )


class ExampleTests(unittest.TestCase):
    def _init():
        def runner(path):
            method_name = os.path.splitext(os.path.basename(path))[0]
            method_name = method_name.replace("-", "_")
            method_name = "test_" + method_name

            def method(self):
                main(["-cp3", path], quiet=True)

            return method_name, method

        path = os.path.join(os.path.dirname(__file__), "examples")
        for root, dirs, files in os.walk(path):
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")
            for f in files:
                if f.endswith(".py"):
                    path = os.path.join(root, f)
                    with open(path) as fp:
                        skip = "SKIPTEST" in next(fp)
                    if not skip:
                        yield runner(path)

    locals().update(_init())


if __name__ == "__main__":
    unittest.main()
