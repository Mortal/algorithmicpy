A = [[-9,  5,  7,  7,  3, -9,  3,  2],
     [ 8, -9,  2,  4,  9, -7,  4,  0],
     [-2, -1,  6,  9, -3, -9,  9, -9],
     [ 8, -9,  2,  5, -1,  5,  7,  9],
     [-3,  9,  7, -1,  6,  7,  3,  5],
     [-4,  9,  4, -8,  4, -8,  9, -7],
     [ 9,  8,  6,  1,  3,  3,  1, -5],
     [-6, -5, -1,  5,  3, -1, -8, -2]]

def zeros(n, m):
    return [[0] * m for i in range(n)]

def maxdelsum_kadane(A):
    n = len(A)
    maxsofar = 0
    maxendinghere = 0
    for i in range(0, n):
        maxendinghere = max(maxendinghere + A[i], 0)
        maxsofar = max(maxsofar, maxendinghere)
    return maxsofar

def maxdelsum_2d(A):
    n = len(A)
    m = len(A[0])
    maxsofar = 0
    for i1 in range(0, n):
        s = [0] * m
        for i2 in range(i1, n):
            for j in range(0, m):
                s[j] += A[i2][j]
            # s[j] == A[i1][j] + A[i1 + 1][j] + ... + A[i2][j]
            r"bla"
            # Solve 1d subproblem [s[0], s[1], ..., s[m-1]]
            max1d = maxdelsum_kadane(s)
            maxsofar = max(maxsofar, max1d)
    return maxsofar

print(maxdelsum_2d(A))
