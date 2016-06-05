def compute_prefix(P):
    """
    >>> compute_prefix('abcababcabc')
    [-1, -1, -1, 0, 1, 0, 1, 2, 3, 4, 2]
    """
    pi = [-1]
    for i in range(1, len(P)):
        # Compute k = pi[i] such that k < i and P[:k+1] is a suffix of P[:i+1]
        k = pi[i-1]
        assert -1 <= k < i-1 and P[:i].endswith(P[:k+1])
        while k > -1 and P[i] != P[k+1]:
            k = pi[k]
        assert -1 <= k < i-1 and P[:i].endswith(P[:k+1])
        assert k == -1 or P[i] == P[k+1]
        if P[k+1] == P[i]:
            pi.append(k + 1)
            assert k + 1 < i and P[:i+1].endswith(P[:k+2])
        else:
            pi.append(-1)
        assert -1 <= pi[i] < i and P[:i+1].endswith(P[:pi[i]+1])
    return pi


def find_matches(T, P, pi, report):
    k = -1
    for i in range(len(T)):
        assert T[:i].endswith(P[:k+1])
        while k > -1 and T[i] != P[k+1]:
            k = pi[k]
        if T[i] == P[k+1]:
            k = k + 1
        assert T[:i+1].endswith(P[:k+1])
        if k+1 == len(P):
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
