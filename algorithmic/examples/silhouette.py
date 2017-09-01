GLOBALS = 'inf'.split()
PATTERNS = [
    ('inf', r'\infty'),
    ("a[:i]", r"#a[0\dots #i)"),
    ("a[i:]", r"#a[#i \dots \text{end})"),
    ("a[-1]", r"#a[\text{end}]"),
    ("a[0:0] = b", r"\STATE insert $#b$ at the beginning of $#a$"),
    ("a[i:i] = b", r"\STATE insert $#b$ just before $#a[#i]$"),
    ("a[0:1] = []", r"\STATE remove first element of $#a$"),
    ("a[-1:] = []", r"\STATE remove last element of $#a$"),
    ("a[-2:] = []", r"\STATE remove last two elements of $#a$"),
    ("a.extend([b[-1]])",
     r"\text{insert the last element of $#b$ at the end of $#a$}"),
    ("a.extend(b)", r"\text{insert $#b$ at the end of $#a$}"),
]


inf = float('inf')

def insert(S, b):
    """
    >>> insert([1, 10, 3], [2, 20, 3])
    [1, 10, 2, 20, 3]
    >>> insert([1, 10, 3], [1, 20, 2])
    [1, 20, 2, 10, 3]
    >>> insert([1, 10, 3], [4, 20, 5])
    [1, 10, 3, 0, 4, 20, 5]
    >>> insert([4, 20, 5], [1, 10, 3])
    [1, 10, 3, 0, 4, 20, 5]
    """
    l, h, r = b
    S[0:0] = [0]
    S.extend([0, +inf])
    i = 1
    while S[i] < l:
        i += 2
    if l < S[i]:
        S[i:i] = [l, S[i-1]]
    while S[i+2] < r:
        S[i+1] = max(S[i+1], h)
        i += 2
    if r < S[i+2]:
        S[i+2:i+2] = [r, S[i+1]]
    S[i+1] = max(S[i+1], h)

    S[0:1] = []
    S[-2:] = []
    return S

def merge(A, B):
    """
    >>> merge([1, 10, 3], [2, 20, 3])
    [1, 10, 2, 20, 3]
    >>> merge([1, 10, 3], [1, 20, 2])
    [1, 20, 2, 10, 3]
    >>> merge([1, 10, 3], [4, 20, 5])
    [1, 10, 3, 0, 4, 20, 5]
    >>> merge([4, 20, 5], [1, 10, 3])
    [1, 10, 3, 0, 4, 20, 5]
    """
    A[0:0] = [0]
    A.extend([0, +inf])
    B[0:0] = [0]
    B.extend([0, +inf])
    S = []
    i = 1
    j = 1
    while A[i] != +inf or B[j] != +inf:
        if A[i] < B[j]:
            S.extend([A[i], max(A[i+1], B[j-1])])
            i += 2
        elif B[j] < A[i]:
            S.extend([B[j], max(A[i-1], B[j+1])])
            j += 2
        elif A[i] == B[j]:
            S.extend([B[j], max(A[i+1], B[j+1])])
            i += 2
            j += 2
    S[-1:] = []
    return S

def cleanup(S):
    R = S[:2]
    i = 2
    while i < len(S) - 1:
        if S[i+1] != R[-1]:
            R.extend([S[i], S[i+1]])
        i += 2
    R.extend([S[-1]])
    return R

def silhouette(B):
    """
    >>> silhouette([[1, 10, 2]])
    [1, 10, 2]
    >>> S = silhouette([
    ...     [1, 11, 5], [2, 6, 7], [3, 13, 9], [12, 7, 16],
    ...     [14, 3, 25], [19, 18, 22], [23, 13, 29], [24, 4, 28],
    ... ])
    >>> cleanup(S) == [1, 11, 3, 13, 9, 0, 12, 7, 16, 3, 19, 18, 22, 3, 23, 13, 29]
    True
    """

    if len(B) == 1:
        return B[0]
    else:
        m = len(B) // 2
        return merge(silhouette(B[:m]), silhouette(B[m:]))


if __name__ == '__main__':
    for t in range(int(input())):
        n = int(input())
        buildings = [list(map(int, input().split()))
                     for i in range(n)]
        print(' '.join(map(str, cleanup(silhouette(buildings)))))
