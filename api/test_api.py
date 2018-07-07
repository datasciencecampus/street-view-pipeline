# todo: these are broked.
# need to intercept requests.Session class instance of API.
import mock
from api import API


@mock.patch('api.API.s.get')
def test_load_jobs(mock_get):
    d = [{
           "bearing": 250.43, 
           "cam_dir": "left", 
           "city": "Walsall", 
           "id": 17030922, 
           "latitude": 52.588931, 
           "longitude": -1.995204, 
           "osm_way_id": 358357784, 
           "road_name": "Birchills Street", 
           "sequence": "000002"
         }, 
         {
           "bearing": 36.69, 
           "cam_dir": "left", 
           "city": "Walsall", 
           "id": 17030930, 
           "latitude": 52.595853, 
           "longitude": -1.981861, 
           "osm_way_id": 51431273, 
           "road_name": "Coalpool Lane", 
           "sequence": "000008"
         }] 
    mock_resp = mock.Mock()
    mock_resp.json.return_value = d 
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp

    api = API()
    ok, jobs = api.jobs('Walsall', 0)
    assert ok and jobs == d

    mock_resp.json.return_value = None
    mock_resp.status_code = 500
    
    ok, jobs = api.jobs('Walsall', 0)
    assert not ok and jobs is None


@mock.patch('api.s.post')
def test_push_sample(mock_post):
    mock_resp = mock.Mock()
    mock_resp.text = "ok"
    mock_resp.status_code = 200
    mock_post.return_value = mock_resp

    api = API()

    ok = api.sample(123, 13.666)
    assert ok 

    mock_resp.text = "nok"
    ok = api.sample(123, 13.666)
    assert not ok

    mock_resp.text = None
    ok = api.sample(123, 13.666)
    assert not ok

    mock_resp.text = "ok"
    mock_resp.status_code = 500
    ok = api.sample(123, 13.666)
    assert not ok


@mock.patch('api.s.get')
def test_summary(mock_get):
    d = [{
           "city": "Barnsley", 
           "green": -1.0, 
           "points": 74278
         }, 
         {
           "city": "Basildon", 
           "green": -1.0, 
           "points": 74030
         }]
    mock_resp = mock.Mock()
    mock_resp.json.return_value = d
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp

    api = API()

    ok, summary = api.summary()
    assert ok and summary == d

    mock_resp.status_code = 500
    ok, _ = api.summary()
    assert not ok
