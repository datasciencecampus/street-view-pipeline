from flask import Flask, render_template, jsonify, request
from flask_mysqldb import MySQL
import shapely.wkt

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'streetview'

mysql = MySQL()
mysql.init_app(app)

def sanitise(db_job):
    """convert WKT point to shapely geom."""
    wkt_point = db_job.pop('geom')
    point = shapely.wkt.loads(wkt_point.decode('utf-8'))
    db_job['latitude'] = point.y
    db_job['longitude'] = point.x
    return db_job


@app.route('/')
def index():
    """for humans."""
    cur = mysql.connection.cursor()
    cur.execute("""select count(1)
                   from sample_points
                   where predicted = true""")
    rv = cur.fetchone()
    return render_template('index.html', summary={'jobs': rv[0]})


@app.route('/api/jobs/<city>', defaults={'sample_order': None})
@app.route('/api/jobs/<city>/<sample_order>')
def jobs(city, sample_order):
    """gets pending jobs for a city based on sample_order/batch."""
    sql = """select id,
                    city, 
                    road_name, 
                    osm_way_id,
                    lpad(sequence, 6, 0) as sequence,
                    ST_AsText(geom) as geom,
                    bearing,
                    cam_dir
             from sample_points
             where city = %s 
               and predicted = true"""
    cur = mysql.connection.cursor()
    if sample_order is not None:
        sql += """ and sample_order = %s"""
        v = (city, int(sample_order))
    else:
        v = (city, )
    
    sql += """ order by sample_order,
                        osm_way_id,
                        cam_dir asc""" 
    cur.execute(sql, v)
    rv = cur.fetchall()

    cols = [x[0] for x in cur.description]
    jobs = [sanitise(dict(zip(cols, row))) for row in rv]
 
    return jsonify(jobs)

@app.route('/api/all_jobs', defaults={'limit': 25000})
@app.route('/api/all_jobs/<limit>')
def all_jobs(limit):
    """get next batch of jobs prioritised by sampling order and evenly 
    distributed among cities.
    """
    sql = """select id,
                    city, 
                    road_name, 
                    osm_way_id,
                    lpad(sequence, 6, 0) as sequence,
                    ST_AsText(geom) as geom,
                    bearing,
                    cam_dir
             from sample_points
             where predicted = true
             order by sample_priority,
                      sample_order,
                      city
             limit %s"""
    cur = mysql.connection.cursor()
    cur.execute(sql, (int(limit), ))

    rv = cur.fetchall()
    cols = [x[0] for x in cur.description]
    jobs = [sanitise(dict(zip(cols, row))) for row in rv]
 
    return jsonify(jobs)


@app.route('/api/sample/<sample_id>', methods=['GET', 'POST'])
def sample(sample_id):
    """get/update a sample."""
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        v = request.form['value']
        cur.execute("""update sample_points
                         set predicted = false,
                                 value = %s
                       where id = %s""", (v, sample_id))
        return "ok", 200 
    else:
        cur.execute("""select id,
                              city, 
                              road_name, 
                              osm_way_id,
                              lpad(sequence, 6, 0) as sequence,
                              ST_AsText(geom) as geom,
                              bearing,
                              cam_dir,
                              sample_order,
                              sample_priority,
                              ts,
                              predicted,
                              value
                       from sample_points
                       where id = %s""", (sample_id, ))
        rv = cur.fetchone()

        cols = [x[0] for x in cur.description]
        sample = sanitise(dict(zip(cols, rv)))

        return jsonify(sample)


@app.route('/api/samples/<city>')
def samples(city):
    """get all samples for a city."""
    def seq(cam_dir):
        sql = """select id,
                        osm_way_id,
                        sequence,
                        value,
                        predicted
                 from sample_points
                 where city = %s
                       and cam_dir = %s
                 order by osm_way_id,
                          sequence asc"""
        print("samples({})".format(city))
        cur = mysql.connection.cursor()
        cur.execute(sql, (city, cam_dir))
        rv = cur.fetchall()
        print("got samples.")
        cols = [x[0] for x in cur.description]
        # this just packs rows into:
        # {"way_id": [{"id":x, "sequence": y, "value": z, "predicted": true},
        # ..], "way..."}
        ways = {}
        for dict_row in (dict(zip(cols, row)) for row in rv):
            key = dict_row['osm_way_id']
            way = ways.get(key, [])
            way.append({k: v for k, v in dict_row.items() if k != 'osm_way_id'})
            ways[key] = way        

        print("got ways")
        return ways

    return jsonify({'left': seq('left'), 'right': seq('right')})


@app.route('/api/interpolate', methods=['POST'])
def interpolate():
    """update interpolated points."""
    samples = request.get_json()
    try:
        for sample in samples:
            cur = mysql.connection.cursor()
            argv = (sample['value'], sample['id'])
            cur.execute("""update sample_points
                           set value = %s
                           where id = %s""", argv) 
            cur.close()
        return "ok", 200
    except:
        return "nok", 500


@app.route('/api/summary')
def summary():
    """just a city summary.."""
    print("summary()")
    cur = mysql.connection.cursor()
    cur.execute("""select city,
                          count(1) as points,
                          avg(nullif(value, -1)) as green
                   from sample_points
                   group by city""")
    rv = cur.fetchall()
    cols = [x[0] for x in cur.description]
    cities = [dict(zip(cols, row)) for row in rv]
    return jsonify(cities)


@app.route('/api/geojson/<city>')
def export(city):
    """export city as geojson.

    feature properties are based on simplestyle spec:
    https://github.com/mapbox/simplestyle-spec/tree/master/1.1.0

    and each left/right feature property as an associated id so that the 
    original image + complete sample data can be obtained later.

    like so:
    
    {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": {
            "type": "Point",
            "coordinates": [
              -3.2615161,
              51.5393021
            ]
          },
          "properties": {
            "road": "London Road",
            "left" {
              "green": 0.5,
              "id": 123,
              "predicted": false,
              "sample_ts": "2012-04-23T18:25:43.511Z"
            },
            "right": {
              "green": 0.25,
              "id": 555,
              "predicted": true,
              "sample_ts": "2012-04-23T18:25:43.511Z"
            },
            "marker-color": "#00ff00",
            "marker-size": "small"
          }
        }
      ]
    }
    """
    def seq(cam_dir):
        sql = """select osm_way_id,
                        sequence,
                        road_name,
                        ts,
                        ST_AsText(geom) as geom,                
                        value,
                        id,
                        predicted
                 from sample_points
                 where city = %s
                       and cam_dir = %s
                 order by osm_way_id,
                          sequence asc"""
        cur = mysql.connection.cursor()
        cur.execute(sql, (city, cam_dir))
        rv = cur.fetchall()
        cols = [x[0] for x in cur.description]
        for row in rv:
            yield dict(zip(cols, row))

    def marker_colour(left, right):
        """scale marker colour according to level of green."""
        green = 0.5 * (left['value'] + right['value'])
        g = int(green * 255)
        return "#00{:02x}00".format(g)

    def zipem(left, right):
        """combine 2 results."""
        def props(x):
            """left or right feature props."""
            return {
                'green': round(x['value'], 4),
                'id': x['id'],
                'predicted': x['predicted'],
                'sample_ts': x['ts'].isoformat()
            }
        
        for left, right in zip(left, right):
            point = shapely.wkt.loads(left['geom'].decode('utf-8'))
            assert left['osm_way_id'] == right['osm_way_id'] and \
                   left['sequence'] == right['sequence']
            yield {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [point.x, point.y]
                },
                'properties': {
                    'road': left['road_name'],
                    'left': props(left), 
                    'right': props(right),
                    # simplestyle spec. properties.
                    'marker-color': marker_colour(left, right), 
                    'marker-size': 'small'
                }
            }
         
    features = list(zipem(seq('left'), seq('right')))
    return jsonify({'type': 'FeatureCollection', 'features': features}) 
