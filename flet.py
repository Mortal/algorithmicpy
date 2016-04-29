def flet_table(x, y, z):
    F = [[None] * len(y) for _ in range(len(x))]
    for i in range(len(x)):
        for j in range(len(y)):
            F_x = (i == 0) or F[i-1][j]
            F_y = (j == 0) or F[i][j-1]
            # print(x[i], y[j], z[i+j], F_x, F_y)
            F[i][j] = (F_x and (x[i] == z[i+j])) or (F_y and (y[j] == z[i+j]))
    # print('\n'.join(''.join('.@'[v] for v in r) for r in F))
    return F


def flet(x, y, z):
    """
    >>> flet('a', 'ab', 'aba')
    True
    >>> flet('uro', 'gled', 'gulerod')
    True
    >>> flet('algoritmer', 'datastrukturer', 'dalgatorastritukturmerer')
    True
    """
    x = [None] + list(x)
    y = [None] + list(y)
    z = [None] + list(z)
    F = flet_table(x, y, z)
    return F[-1][-1]


def flet_x(x, y, z):
    """
    >>> x = 'algoritmer'
    >>> y = 'datastrukturer'
    >>> z = 'dalgatorastritukturmerer'
    >>> r = flet_x(x, y, z)
    >>> ''.join(c if i+1 in r else c.upper() for i, c in enumerate(z))
    'DalgATorASTRitUKTURmERer'
    """
    n = len(x)
    m = len(y)
    x = [None] + list(x)
    y = [None] + list(y)
    z = [None] + list(z)
    F = flet_table(x, y, z)
    i = n
    j = m
    r = []
    while (i, j) != (0, 0):
        if i > 0 and F[i-1][j]:
            r.append(i + j)
            i = i - 1
        else:
            j = j - 1
    r.reverse()
    return r
