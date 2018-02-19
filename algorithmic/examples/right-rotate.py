def right_rotate(x):
    y = x.left
    x.left = y.right
    if y.right != T.nil:
        y.right.p = x
    y.p = x.p
    if x.p != T.nil:
        x = y
    elif x == x.p.right:
        x.p.right = y
    else:
        x.p.left = y
    y.right = x
    x.p = y
