def point_idw(src, dst, weight):
    """inverse distance weighting of src and dst where

    weight = 1 / (number of points to interpolate + 1).
    """
    return (1-weight)*(max(0, src) + weight*max(0, dst)


def interpolate_segment(src, dst, n):
    """interpolate n points on a segment between src and dst using idw.

    note that this assumes points are equidistant.
    """
    d = n+1
    return [point_idw(src, dst, i/d) for i in range(1, d)]


def pairs_iterator(l):
    """iterate through a list of objects yielding previous, next element."""
    it = iter(l)
    pre = None
    for x in it:
        yield pre, x
        pre = x
    yield pre, None


def interpolate_road(samples):
    """interpolate missing sample points.

    side-effect: in-place operation. 
    """
    def fix_seq(samples): 
        # <-- todo: work-around for bug.
        # <-- sequence should be set *after* cutting off points of road not in 
        #     city. assumption is that sequence_i = index_i+1. just use index of
        #     sample, ignore sequence..
        # note also that this also applies to sample_order + sample_priority.
        for i, sample in enumerate(samples):
            sample['sequence'] = i+1

    fix_seq(samples)

    for src, dst in pairs_iterator(x for x in samples if not x['predicted']):
        if src is None and dst is None:
            # nothing to do
            return
        if src is None:
            # first segment up until first reading should assume first reading
            to = dst['sequence'] - 1
            v = dst['value']
            for i in range(0, to):
                samples[i]['value'] = v
            continue
        if dst is None:
            # last segment
            src_seq = src['sequence']
            n = len(samples)
            if n - src_seq > 0:
                v = src['value']
                for i in range(src_seq, n): 
                    samples[i]['value'] = v
            return
        src_seq, src_val = src['sequence'], src['value']
        dst_seq, dst_val = dst['sequence'], dst['value']

        n = dst_seq - src_seq
        if n == 1:
            continue

        # things in-between
        ip = interpolate_segment(src_val, dst_val, n-1)
        for i, sample in enumerate(samples[src_seq:dst_seq - 1]):
            sample['value'] = ip[i]

