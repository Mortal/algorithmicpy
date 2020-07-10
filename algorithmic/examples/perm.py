def apply_permutation(x, pi):
    """
    >>> x = [10, 20, 30, 40, 50]
    >>> pi = [2, 1, 4, 0, 3]
    >>> apply_permutation(x, pi)
    >>> print(pi, x)
    [0, 1, 2, 3, 4] [40, 20, 10, 50, 30]
    >>> x = [10, 20, 30, 40, 50]
    >>> pi = [1, 2, 3, 4, 0]
    >>> apply_permutation(x, pi)
    >>> print(pi, x)
    [0, 1, 2, 3, 4] [50, 10, 20, 30, 40]
    """
    for i in range(len(x)):
        while pi[i] != i:
            x[pi[i]], x[i] = x[i], x[pi[i]]
            pi[pi[i]], pi[i] = pi[i], pi[pi[i]]


if __name__ == "__main__":
    x = [10, 20, 30, 40, 50]
    pi = [1, 2, 3, 4, 0]
    apply_permutation(x, pi)
    print(x, pi)
