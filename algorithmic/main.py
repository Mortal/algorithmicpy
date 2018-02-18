import os
import ast
import argparse
import functools
import subprocess
import collections
from .visitor import Visitor


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
    parser.add_argument('-c', '--output-and-compile', action='store_true')
    parser.add_argument('-p', '--preamble', action='store_true')
    parser.add_argument('-3', '--new-style', action='store_true')
    parser.add_argument('filename', nargs='+')
    args = parser.parse_args()
    output_preamble = args.preamble or args.output_and_compile
    for filename in args.filename:
        with open(filename) as fp:
            source = fp.read()
        o = ast.parse(source, filename, 'exec')
        if args.output_and_compile:
            base, ext = os.path.splitext(filename)
            output_filename = base + '.tex'
            ofp = open(output_filename, 'w')
            out_print = functools.partial(print, file=ofp)
        else:
            out_print = print
        visitor = Visitor(source, print=out_print)
        if output_preamble:
            visitor.print(PREAMBLE)
        if args.new_style:
            visitor.print(r'\newcommand{\eq}{==}')
            visitor.print(r'\renewcommand{\gets}{=}')
            visitor.print(r'\renewcommand{\land}{\mathbin{\text{and}}}')
            visitor.print(r'\renewcommand{\lor}{\mathbin{\text{or}}}')
        visitor.visit(o)
        if output_preamble:
            visitor.print(POSTAMBLE)
        if args.output_and_compile:
            ofp.close()
            subprocess.check_call(
                ('latexmk', '-pdf', output_filename),
                stdin=subprocess.DEVNULL)


def pattern_stats():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='+')
    args = parser.parse_args()

    def noop(*args, **kwargs):
        pass

    pattern_usage = collections.defaultdict(list)

    for filename in args.filename:
        with open(filename) as fp:
            source = fp.read()
        o = ast.parse(source, filename, 'exec')
        p = collections.defaultdict(int)
        visitor = Visitor(source, print=noop, pattern_stats=p)
        visitor.visit(o)
        for i in p.keys():
            pattern_usage[i - len(visitor.patterns)].append(filename)

    for i, p in enumerate(visitor.patterns):
        print("%s\t%r" % (','.join(pattern_usage[i - len(visitor.patterns)]), p))
