from collections import deque


def fold(x):
    """fold a list x into equal parts.

    returns a list of the same input length containing the index visit order.

    01 02 03 04 05 06 07 08 09 10 11 12 13 14 15
                         01
             02                      03
       04          05          06          07
    08    09    10    11    12    13    14    15
    =
    08 04 12 02 06 10 14 01 03 05 07 09 11 13 15


    1 2 3 4 5 6 7
          1
      2       3
    4   5   6   7
    =
    4 2 6 1 3 5 7
    """
    def pivot(x):
        p = len(x) // 2
        l = x[:p]
        r = x[p+1:]
        return x[p], l, r
    q = deque([(x, 0)])
    while q:
        x = q.popleft()
        p, l, r = pivot(x[0])
        depth = x[1] + 1
        if l: q.append((l, depth))
        if r: q.append((r, depth))

        yield p, depth 


def schedule(x):
    """in-place index visit order."""
    ind = [0] * len(x)
    depth = [0] * len(x)
    for order, (i, d) in enumerate(fold(range(len(x)))):
        ind[i] = order
        depth[i] = d
    return ind, depth


def pp(x):
    """just vis."""
    ind, depth = schedule(x)
    md = max(depth) + 1
    for ind, depth in zip(ind, depth):
        print("{:003d} {}".format(ind, "*" * ((md - depth) ** 2)))
