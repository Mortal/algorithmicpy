def find_lcs(c, x, y):
    i = len(x)
    j = len(y)
    lcs = ""
    while i > 1 and j > 1:
        if x[i] == y[j]:
            lcs = x[i] + lcs
            i = i - 1
            j = j - 1
        elif c[i, j-1] > c[i-1, j]:
            j = j - 1
        else:
            i = i - 1
    return lcs
