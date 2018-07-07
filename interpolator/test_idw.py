import idw

def list_equal(l1, l2, tol=10**-8):
    """check floats in l1 = floats in l2."""
    return sum(abs(x-y) for x, y in zip(l1, l2)) < tol


def test_interpolate_segment():
    interpolated = idw.interpolate_segment(src=0.3, dst=0.1, n=0)
    assert interpolated == []

    interpolated = idw.interpolate_segment(src=0.3, dst=0.1, n=1)
    assert list_equal(interpolated, [0.2])

    interpolated = idw.interpolate_segment(src=0.3, dst=0.1, n=2)
    expected = [2/3*0.3 + 1/3*0.1, 
                1/3*0.3 + 2/3*0.1]
    assert list_equal(interpolated, expected)

    interpolated = idw.interpolate_segment(src=0.3, dst=0.1, n=3)
    expected = [3/4*0.3 + 1/4*0.1,
                (0.3+0.1)/2,
                1/4*0.3 + 3/4*0.1]
    assert list_equal(interpolated, expected)
 
    interpolated = idw.interpolate_segment(src=0.3, dst=0.1, n=4)
    expected = [4/5*0.3 + 1/5*0.1,
                3/5*0.3 + 2/5*0.1,
                2/5*0.3 + 3/5*0.1,
                1/5*0.3 + 4/5*0.1]
    assert list_equal(interpolated, expected)


def test_pairs_iterator():
    pairs = list(idw.pairs_iterator(list(range(1, 5))))
    assert pairs == [(None, 1), (1, 2), (2, 3), (3, 4), (4, None)]


def test_interpolate_road():

    samples = [
      {
        "predicted": 1, 
        "sequence": 1, 
        "value": -1.0
      }, 
      {
        "predicted": 1, 
        "sequence": 2, 
        "value": -1.0 
      }, 
      {
        "predicted": 0, 
        "sequence": 3, 
        "value": 0.0283
      }, 
      {
        "predicted": 0, 
        "sequence": 4, 
        "value": 0.0376
      }, 
      {
        "predicted": 1, 
        "sequence": 5, 
        "value": -1.0
      }, 
      {
        "predicted": 1, 
        "sequence": 6, 
        "value": -1.0
      }, 
      {
        "predicted": 0, 
        "sequence": 7, 
        "value": 0.5673
      }, 
      {
        "predicted": 1, 
        "sequence": 8, 
        "value": -1.0 
      }, 
      {
        "predicted": 1, 
        "sequence": 9, 
        "value": -1.0
      }
    ]
  
    expected = [0.0283, # <--
                0.0283, # <--
                0.0283,
                0.0376,
                idw.point_idw(0.0376, 0.5673, 1/3), # <--
                idw.point_idw(0.0376, 0.5673, 2/3), # <--
                0.5673,
                0.5673, # <--
                0.5673] # <--
    idw.interpolate_road(samples) 
    assert len(samples) == len(expected)

    values = [sample['value'] for sample in samples]  
    assert list_equal(values, expected) 
   
    samples = []
    idw.interpolate_road(samples)
    assert samples == []

    samples = [{'predicted': 1, 'sequence': 1, 'value': -1}]
    idw.interpolate_road(samples)
    assert len(samples) == 1
    assert list_equal([sample['value'] for sample in samples], [-1])

    samples += [{'predicted': 0, 'sequence': 2, 'value': 10}]
    idw.interpolate_road(samples)
    assert len(samples) == 2
    assert list_equal([sample['value'] for sample in samples], [10, 10])    

    samples += [{'predicted': 1, 'sequence': 3, 'value': -1}]
    idw.interpolate_road(samples)
    assert len(samples) == 3
    assert list_equal([sample['value'] for sample in samples], [10, 10, 10])

    samples[2]['predicted'] = 0
    samples += [{'predicted': 1, 'sequence': 4, 'value': -1}]
    samples += [{'predicted': 0, 'sequence': 5, 'value': 3}]
    idw.interpolate_road(samples)
    assert len(samples) == 5
    assert list_equal([sample['value'] for sample in samples], [10, 10, 10, 6.5, 3])

    samples = [{'predicted': 0, 'sequence': 1, 'value': 100}]
    idw.interpolate_road(samples)
    assert len(samples) == 1
    assert list_equal([sample['value'] for sample in samples], [100])

    # sequence bug
    samples = [{'predicted': 1, 'sequence': 3, 'value': -1}, {'predicted': 0, 'sequence': 99, 'value': 100}]
    idw.interpolate_road(samples)
    assert len(samples) == 2
    assert list_equal([sample['value'] for sample in samples], [100, 100])
