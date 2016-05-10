import itertools


def reachable_states(Q, Sigma, q0, delta):
    """
    >>> Q = {1, 2, 3}
    >>> Sigma = {'a'}
    >>> q0 = 1
    >>> delta = {(1, 'a'): 2, (2, 'a'): 2, (3, 'a'): 3}
    >>> Q_prime, delta_prime = reachable_states(Q, Sigma, q0, delta)
    >>> sorted(Q_prime)
    [1, 2]
    >>> sorted(delta_prime.keys())
    [(1, 'a'), (2, 'a')]
    """
    next = [q0]
    Q_prime = {q0}
    while len(next) > 0:
        p = next[0]
        next[0:1] = []
        for sigma in Sigma:
            q = delta[p, sigma]
            if q not in Q_prime:
                Q_prime.add(q)
                next.append(q)
    delta_prime = {}
    for q in Q_prime:
        for sigma in Sigma:
            delta_prime[q, sigma] = delta[q, sigma]
    return Q_prime, delta_prime


def distinguishable_states(Q, Sigma, delta, A):
    different = {}
    for p in Q:
        for q in Q:
            if (p in A and q not in A) or (p not in A and q in A):
                different[Set(p, q)] = True
            else:
                different[Set(p, q)] = False
    done = False
    while not done:
        done = True
        for p in Q:
            for q in Q:
                if not different[Set(p, q)]:
                    for sigma in Sigma:
                        if different[Set(delta[p, sigma], delta[q, sigma])]:
                            different[Set(p, q)] = True
                            done = False
    return different


def minimize(Q, Sigma, q0, delta, A):
    """
    >>> Q = {1, 2, 3, 4, 5}
    >>> Sigma = {'a', 'b'}
    >>> q0 = 1
    >>> delta = {
    ...     (1, 'a'): 2,
    ...     (1, 'b'): 3,
    ...     (2, 'a'): 1,
    ...     (2, 'b'): 2,
    ...     (3, 'a'): 4,
    ...     (3, 'b'): 3,
    ...     (4, 'a'): 3,
    ...     (4, 'b'): 4,
    ...     (5, 'a'): 5,
    ...     (5, 'b'): 5,
    ... }
    >>> A = {3, 4}
    >>> _print_machine((Q, Sigma, q0, delta, A))
    I  1 a-> 2 b-> 3
       2 a-> 1 b-> 2
     A 3 a-> 4 b-> 3
     A 4 a-> 3 b-> 4
       5 a-> 5 b-> 5
    >>> _print_machine(minimize(Q, Sigma, q0, delta, A))
    I  1 a-> 2 b-> 3
       2 a-> 1 b-> 2
     A 3 a-> 3 b-> 3
    """
    Q, delta = reachable_states(Q, Sigma, q0, delta)
    different = distinguishable_states(Q, Sigma, delta, A)
    rep = {}
    Q_prime = set()
    A_prime = set()
    for p in Q:
        if p not in rep:
            Q_prime.add(p)
            if p in A:
                A_prime.add(p)
            for q in Q:
                if not different[Set(p, q)]:
                    rep[q] = p
    q0_prime = rep[q0]
    delta_prime = {}
    for p in Q_prime:
        for sigma in Sigma:
            delta_prime[p, sigma] = rep[delta[p, sigma]]
    return Q_prime, Sigma, q0_prime, delta_prime, A_prime


def product(Sigma, Q1, q1, delta1, A1, Q2, q2, delta2, A2):
    """
    >>> Sigma = {'a', 'b'}
    >>> Q1 = {1, 2}
    >>> q1 = 1
    >>> A1 = {2}
    >>> Q2 = {3, 4}
    >>> q2 = 3
    >>> A2 = {4}
    >>> delta1 = {
    ...     (1, 'a'): 2,
    ...     (1, 'b'): 1,
    ...     (2, 'a'): 1,
    ...     (2, 'b'): 2,
    ... }
    >>> delta2 = {
    ...     (3, 'a'): 3,
    ...     (3, 'b'): 4,
    ...     (4, 'a'): 4,
    ...     (4, 'b'): 3,
    ... }
    >>> _print_machine((Q1, Sigma, q1, delta1, A1))
    I  1 a-> 2 b-> 1
     A 2 a-> 1 b-> 2
    >>> _print_machine((Q2, Sigma, q2, delta2, A2))
    I  3 a-> 3 b-> 4
     A 4 a-> 4 b-> 3
    >>> _print_machine(product(Sigma, Q1, q1, delta1, A1, Q2, q2, delta2, A2))
    I  (1, 3) a-> (2, 3) b-> (1, 4)
     A (1, 4) a-> (2, 4) b-> (1, 3)
     A (2, 3) a-> (1, 3) b-> (2, 4)
     A (2, 4) a-> (1, 4) b-> (2, 3)
    """
    Q = set()
    A = set()
    q0 = (q1, q2)
    delta = {}
    for p in Q1:
        for q in Q2:
            Q.add((p, q))
            if p in A1 or q in A2:
                A.add((p, q))
            for sigma in Sigma:
                delta[(p, q), sigma] = (delta1[p, sigma], delta2[q, sigma])
    return Q, Sigma, q0, delta, A


def shortest_paths(Q, Sigma, q0, delta, A):
    """
    >>> Q = {1, 2, 3, 4}
    >>> Sigma = {'a', 'b'}
    >>> q0 = 1
    >>> delta = {
    ...     (1, 'a'): 2,
    ...     (1, 'b'): 3,
    ...     (2, 'a'): 1,
    ...     (2, 'b'): 2,
    ...     (3, 'a'): 4,
    ...     (3, 'b'): 3,
    ...     (4, 'a'): 3,
    ...     (4, 'b'): 4,
    ... }
    >>> A = {3, 4}
    >>> shortest_paths(Q, Sigma, q0, delta, A)
    {1: '', 2: 'a', 3: 'b', 4: 'ba'}
    """
    paths = {}
    paths[q0] = ""
    queue = [q0]
    while len(queue) > 0:
        p = queue[0]
        queue[0:1] = []
        for sigma in Sigma:
            q = delta[p, sigma]
            if q not in paths:
                paths[q] = paths[p] + sigma
                queue.append(q)
    return paths


def shortest_accepted(Q, Sigma, q0, delta, A):
    paths = shortest_paths(Q, Sigma, q0, delta, A)
    x = None
    n = float('inf')
    for q in A:
        if len(paths[q]) < n:
            x = paths[q]
            n = len(paths[q])
    return x


def Set(*args):
    return frozenset(args)


def _print_machine(M):
    Q, Sigma, q0, delta, A = M
    for q in sorted(Q):
        init = 'I' if q == q0 else ' '
        acc = 'A' if q in A else ' '
        print('%s%s %s %s' %
              (init, acc, q,
               ' '.join('%s-> %s' % (sigma, delta[q, sigma])
                        for sigma in sorted(Sigma))))


def _print_nfa(M):
    Q, Sigma, q0, delta, A = M
    for q in sorted(Q):
        init = 'I' if q == q0 else ' '
        acc = 'A' if q in A else ' '
        print('%s%s %s %s' %
              (init, acc, q,
               ' '.join('%s-> %s' % (sigma, r)
                        for sigma in sorted(Sigma)
                        for r in delta.get((q, sigma), []))))


def _parse(s, empty, c, all, any, rep):
    """
    >>> rep = lambda s: {'': s}
    >>> p = lambda s: _parse(s, empty=str, c=str, all=list, any=tuple, rep=rep)
    >>> p("a")
    'a'
    >>> p("ab")
    ['a', 'b']
    >>> p("ab*")
    ['a', {'': 'b'}]
    >>> p("(ab)*")
    {'': ['a', 'b']}
    >>> p("(a|)*")
    {'': ('a', '')}
    """
    i = 0

    def peek():
        nonlocal i
        return '' if i >= len(s) else s[i]

    def take():
        nonlocal i
        c = peek()
        i += 1
        while i < len(s) and s[i] == ' ':
            i += 1
        return c

    def accept(c):
        if peek() == c:
            return take()

    def peek_notany(c):
        return c.find(peek()) == -1

    def peek_char():
        return peek_notany('()|*')

    def expect(c):
        if peek() != c:
            raise ValueError("At %d: Expected %r, got %r" % (i, c, peek()))
        take()

    def factor():
        if accept('('):
            r = expression()
            expect(')')
        elif peek_char():
            r = c(take())
        else:
            # Empty string
            return empty()
        while accept('*'):
            r = rep(r)
        return r

    def term():
        r = [factor()]
        while peek_char():
            r.append(factor())
        return r[0] if len(r) == 1 else all(r)

    def expression():
        r = [term()]
        while accept('|'):
            r.append(term())
        return r[0] if len(r) == 1 else any(r)

    def input():
        r = expression()
        expect('')
        return r

    return input()


def _parse_nfa(s):
    """
    >>> _print_nfa(_parse_nfa("(a|b)bc"))
     A 0 
       1 c-> 0
       2 b-> 1
    I  3 a-> 2 b-> 2
       4 a-> 2
       5 b-> 2
    >>> _print_nfa(_parse_nfa("(a*|b)"))
    """
    Q = []
    Sigma = set()
    A = set()
    delta = {}

    qa = len(Q)
    Q.append(qa)
    A.add(qa)

    def empty():
        return lambda next: next

    def character(c):
        def r(next):
            q = len(Q)
            Q.append(q)
            Sigma.add(c)
            delta[q, c] = [next]
            return q
        return r

    def all(ms):
        def r(next):
            for m in reversed(ms):
                next = m(next)
            return next
        return r

    def all(ms):
        def r(next):
            for m in reversed(ms):
                next = m(next)
            return next
        return r

    def any(ms):
        def r(next):
            q = len(Q)
            Q.append(q)
            qs = [m(next) for m in ms]
            for sigma in Sigma:
                delta[q, sigma] = [a for m in qs
                                   for a in delta.get((m, sigma), [])]
            for m in qs:
                if m in A:
                    A.add(q)
            return q
        return r

    def rep(m):
        def r(next):
            # TODO handle this properly...
            q = len(Q)
            Q.append(q)
            if next in A:
                A.add(q)
            p = m(next)
            for sigma in Sigma:
                delta[q, sigma] = (
                    delta.get((next, sigma), []) +
                    delta.get((p, sigma), []))
            return q
        return r

    q0 = _parse(s, empty, character, all, any, rep)(qa)
    delta = {(q, sigma): frozenset(delta.get((q, sigma), []))
             for q in Q for sigma in Sigma}
    return Q, Sigma, q0, delta, A


def determinize(Q, Sigma, q0, delta, A):
    Q_prime = {Set(q0)}
    delta_prime = {}

    next = [Set(q0)]
    while len(next) > 0:
        p = next[0]
        next[0:1] = []
        for sigma in Sigma:
            delta_prime[p, sigma] = Set()
            for q in p:
                delta_prime[p, sigma] = delta_prime[p, sigma].union(delta[q, sigma])
            if delta_prime[p, sigma] not in Q_prime:
                Q_prime.add(delta_prime[p, sigma])
                next.append(delta_prime[p, sigma])

    A_prime = set()
    for p in Q_prime:
        for q in p:
            if q in A:
                A_prime.add(p)

    return Q_prime, Sigma, Set(q0), delta_prime, A_prime


def rename(Q, Sigma, q0, delta, A):
    names = {}
    Q_prime = set()
    A_prime = set()
    n = 0
    for q in Q:
        n += 1
        names[q] = n
        Q_prime.add(n)
        if q in A:
            A_prime.add(n)
    delta_prime = {}
    for q in Q:
        for sigma in Sigma:
            delta_prime[names[q], sigma] = names[delta[q, sigma]]
    return Q_prime, Sigma, names[q0], delta_prime, A_prime


def _regex_fa(s):
    """
    >>> _print_machine(_regex_fa("(a|b)b*c"))
    """
    Q, Sigma, q0, delta, A = _parse_nfa(s)
    Q, Sigma, q0, delta, A = determinize(Q, Sigma, q0, delta, A)
    Q, Sigma, q0, delta, A = rename(Q, Sigma, q0, delta, A)
    Q, Sigma, q0, delta, A = minimize(Q, Sigma, q0, delta, A)
    return Q, Sigma, q0, delta, A
