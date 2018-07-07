from sequence import fold, schedule

def test_fold():
    assert(list(fold(range(1, 8))) == [(4, 1), (2, 2), (6, 2), (1, 3), (3, 3), (5, 3), (7, 3)])


def test_schedule():
    x = range(1, 16)
    order, depth = schedule(x)
    print(order)
    assert order == [7, 3, 8, 1, 9, 4, 10, 0, 11, 5, 12, 2, 13, 6, 14] 
    assert depth == [4, 3, 4, 2, 4, 3, 4, 1, 4, 3, 4, 2, 4, 3, 4]

