GLOBALS = "report".split()
PATTERNS = [
    ("P[:n]", "#P _{#n}"),
    ("s.endswith(t)", r"#t \sqsupset #s"),
    ("report(i)", r"\text{print ``Pattern occurs with shift'' }#i"),
    ("len(s)", r"#s.\mathit{length}"),
    ("pi = [None] * m", r"\STATE let $#pi[0..#m-1]$ be a new array"),
]


def compute_prefix(P):
    """
    >>> compute_prefix('abcababcabc')
    [-1, -1, -1, 0, 1, 0, 1, 2, 3, 4, 2]
    >>> compute_prefix('ababaca')
    [-1, -1, 0, 1, 2, -1, 0]
    >>> compute_prefix('aabaacaabaaa')
    [-1, 0, -1, 0, 1, -1, 0, 1, 2, 3, 4, 1]
    """
    m = len(P)
    pi = [None] * m
    pi[0] = -1
    k = -1
    for i in range(1, m):
        # Compute k = pi[i] such that k < i and P[:k+1] is a suffix of P[:i+1]
        assert k == pi[i - 1]
        assert -1 <= k < i - 1 and P[:i].endswith(P[: k + 1])
        while k > -1 and P[i] != P[k + 1]:
            k = pi[k]
        assert -1 <= k < i - 1 and P[:i].endswith(P[: k + 1])
        assert k == -1 or P[i] == P[k + 1]
        if P[k + 1] == P[i]:
            k = k + 1
        else:
            assert k == -1
        assert k < i and P[: i + 1].endswith(P[: k + 1])
        pi[i] = k
    return pi


def find_matches(T, P, pi, report):
    n = len(T)
    m = len(P)
    k = -1
    for i in range(n):
        assert T[:i].endswith(P[: k + 1])
        while k >= 0 and T[i] != P[k + 1]:
            k = pi[k]
        assert T[:i].endswith(P[: k + 1])
        if T[i] == P[k + 1]:
            k = k + 1
        else:
            assert k == -1
        assert T[: i + 1].endswith(P[: k + 1])
        if k + 1 == m:
            report(i - k)
            k = pi[k]


def kmp(T, P):
    """
    >>> kmp('fooobar', 'oo')
    [1, 2]
    >>> kmp('abcabcababcabcababcabc', 'abcababcabc')
    [3, 11]
    >>> kmp('aaa', 'a')
    [0, 1, 2]
    """
    pi = compute_prefix(P)
    positions = []
    find_matches(T, P, pi, positions.append)
    return positions
