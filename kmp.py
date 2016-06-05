def compute_prefix(P):
    """
    >>> compute_prefix('abcababcabc')
    [-1, -1, -1, 0, 1, 0, 1, 2, 3, 4, 2]
    """
    pi = [-1]
    for i in range(1, len(P)):
        # Compute k = pi[i] such that k < i and P[:k+1] is a suffix of P[:i+1]
        k = pi[i-1]
        assert k+1 < i and P[:k+1] == P[i-(k+1):i]
        while k > -1 and P[k+1] != P[i]:
            k = pi[k]
        assert k+1 < i and P[:k+1] == P[i-(k+1):i]
        assert k == -1 or P[k+1] == P[i]
        if P[k+1] == P[i]:
            pi.append(k + 1)
            assert k + 1 < i and P[:k+2] == P[i+1-(k+2):i+1], (i, k, P)
        else:
            pi.append(-1)
        assert pi[i] < i and P[:pi[i]+1] == P[i+1-(pi[i]+1):i+1]
    return pi


def find_matches(T, P, pi, report):
    i = 0
    k = -1
    while i < len(T):
        assert P[:k+1] == T[i-(k+1):i]
        while k > -1 and T[i] != P[k+1]:
            k = pi[k]
        if T[i] == P[k+1]:
            k = k + 1
        assert P[:k+1] == T[i-k:i+1]
        if k+1 == len(P):
            report(i - k)
            k = pi[k]
        i = i + 1


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
