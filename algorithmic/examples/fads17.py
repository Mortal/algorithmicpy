"""
Solution to the FADS 2017 exam held in January 2018.

To run the embedded unit tests, run `python -m doctest fads17.py`.

To compile into LaTeX, run `python algorithmic.py -c3 fads.py`
and open `fads.pdf`.
"""

GLOBALS = "kmeans _bt _print_cluster".split()
PATTERNS = [
    (
        "n, x = len(x), [None]+list(x)",
        r"% \STATE $#n \gets {}$number of entries in $#x$",
    ),
    ("[None] * (n+1)", r"\text{array of length $#n$}"),
    ("[[None] * (m+1) for i in range(n+1)]", r"\text{table of size $#n \times #m$}"),
    ("(x-y)**z", r"({#x}-{#y})^{#z}"),
    ("x**y", r"{#x}^{#y}"),
    ("(x/y)*(z-w)", r"\frac{#x}{#y}(#z-#w)"),
    ("(x/y)*z", r"\frac{#x}{#y}#z"),
    ("kmeans(x, K, n)", r"\text{table from \textsc{Kmeans}$(#x, #K)$}"),
    (r"[result, a][_bt]", r"#result"),
    (r"_print_cluster(x[i:j+1])", r"\text{print ``cluster ${#x}_{#i..#j}$''}"),
    (r"a or b", r"#a \mathrel{\textbf{or}} #b"),
]


def kmeans(x, K, _bt=0):
    r"""
    >>> from pprint import pprint
    >>> def kmeans_print(x, K):
    ...     dp = kmeans(x, K, 1)
    ...     print('\n'.join(' '.join('%g' % v for v in row[1:]) for row in dp[1:]))
    >>> kmeans_print([1, 2, 6, 7], 2)
    0 0
    0.5 0
    14 0.5
    26 1
    >>> kmeans_print([1, 2, 6, 7, 21], 3)
    0 0 0
    0.5 0 0
    14 0.5 0
    26 1 0.5
    257.2 26 1
    """
    n, x = len(x), [None] + list(x)
    dp = [[None] * (K + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for k in range(1, K + 1):
            if k >= i:
                dp[i][k] = 0
            elif k == 1:
                dp[i][k] = 0
                s = 0
                for j in range(1, i + 1):
                    s = s + x[j]
                for j in range(1, i + 1):
                    dp[i][k] = dp[i][k] + (x[j] - (1 / i) * s) ** 2
            else:
                for j in range(1, i):
                    v = dp[j][k - 1]
                    s = 0
                    for h in range(j + 1, i + 1):
                        s = s + x[h]
                    for h in range(j + 1, i + 1):
                        v = v + (x[h] - (1 / (i - j)) * s) ** 2
                    if j == 1 or v < dp[i][k]:
                        dp[i][k] = v
    return [dp[n][K], dp][_bt]


def backtrack(x, K, _print_cluster=print):
    """
    >>> backtrack([1, 2, 6, 7], 2)
    [6, 7]
    [1, 2]
    >>> backtrack([1, 2, 6, 7, 21], 3)
    [21]
    [6, 7]
    [1, 2]
    """
    dp = kmeans(x, K, 1)
    n, x = len(x), [None] + list(x)
    i = n
    k = K
    while k > 1:
        j = i - 1
        while dp[j][k - 1] > dp[j + 1][k]:
            j = j - 1
        _print_cluster(x[j + 1 : i + 1])
        i = j
        k = k - 1
    _print_cluster(x[1 : i + 1])
