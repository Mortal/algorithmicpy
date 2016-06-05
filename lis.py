GLOBALS = 'inf'.split()
PATTERNS = [('inf', r'\infty')]


def lower_bound(L, v):
    """
    >>> lower_bound([1, 2, 3, 4], 3)
    2
    >>> lower_bound([0, 0, 0], 0)
    0
    >>> lower_bound([0, 0, 0], 1)
    3
    """
    i = 0
    j = len(L)
    while i < j:
        k = i + (j - i) // 2
        if L[k] < v:
            i = k + 1
        else:
            j = k
    return i


inf = float('inf')


def lis(x):
    """
    >>> lis([9, 44, 32, 12, 7, 42, 34, 92, 35, 37, 41, 8, 20, 27, 83, 64, 61,
    ...      28, 39, 93, 29, 17, 13, 14, 55, 21, 66, 72, 23, 73, 99, 1, 2, 88,
    ...      77, 3, 65, 83, 84, 62, 5, 11, 74, 68, 76, 78, 67, 75, 69, 70, 22])
    7
    8
    20
    27
    28
    29
    55
    66
    72
    73
    74
    76
    78
    """
    L = []
    old = []
    for i in range(len(x)):
        j = lower_bound(L, x[i] + 1)
        if j == len(L):
            old.append(inf)
            L.append(x[i])
        else:
            old.append(L[j])
            L[j] = x[i]
    result = [0] * len(L)
    n = len(L)
    while n > 0:
        result[n - 1] = L[n - 1]
        j = lower_bound(L, old[-1]) - 1
        if old[-1] == inf:
            L[-1:] = []
        else:
            L[j] = old[-1]
        old[-1:] = []
        if j == n - 1:
            n = n - 1
    for i in range(len(result)):
        print(result[i])
