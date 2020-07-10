def merge_silhouette(A, B):
    inf = 1e9
    n = len(A)
    m = len(B)
    A[0] = 0
    B[0] = 0
    A[n + 1] = 0
    B[m + 1] = 0
    A[n + 2] = +inf
    B[m + 2] = +inf
    res = []
    res[0] = 0
    i = 1
    j = 1
    k = 1
    while i <= n or j <= m:
        if A[i] < B[j]:
            res[k] = A[i]
            res[k + 1] = max(A[i + 1], B[j - 1])
            i = i + 2
        elif A[i] > B[j]:
            res[k] = B[j]
            res[k + 1] = max(A[i - 1], B[j + 1])
            j = j + 2
        else:  # A[i] == B[j]
            res[k] = A[i]
            res[k + 1] = max(A[i + 1], B[j + 1])
            i = i + 2
            j = j + 2
        if res[k + 1] != res[k - 1]:
            k = k + 2
    return res
