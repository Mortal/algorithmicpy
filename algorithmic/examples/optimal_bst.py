# SKIPTEST
def optimal_bst(p, q):
    n = len(p)
    assert len(q) == n + 1
    e = [["-"] * (n + 1) for _ in range(n + 1)]
    w = [["-"] * (n + 1) for _ in range(n + 1)]
    root = [[0] * n for _ in range(n)]
    for i in range(1, n + 2):
        e[i - 1][i - 1] = q[i - 1]
        w[i - 1][i - 1] = q[i - 1]
    for l in range(1, n + 1):
        for i in range(1, n - l + 2):
            j = i + l - 1
            e[i - 1][j] = float("inf")
            w[i - 1][j] = w[i - 1][j - 1] + p[j - 1] + q[j]
            for r in range(i, j + 1):
                t = e[i - 1][r - 1] + e[r][j] + w[i - 1][j]
                if t < e[i - 1][j]:
                    e[i - 1][j] = t
                    root[i - 1][j - 1] = r
    return e, root


def print_matrix(m):
    print(
        "\n".join(
            " ".join(
                v.ljust(4)
                if isinstance(v, str)
                else "%4.2f" % v
                if isinstance(v, float)
                else str(v)
                for v in row
            )
            for row in m
        )
        + "\n-----"
    )


e, root = optimal_bst(
    [0.04, 0.06, 0.08, 0.02, 0.10, 0.12, 0.14],
    [0.06, 0.06, 0.06, 0.06, 0.05, 0.05, 0.05, 0.05],
)

print("e =")
print_matrix(e)
print("root =")
print_matrix(root)
