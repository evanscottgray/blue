import bluetooth
from flask import Flask
from flask import abort, request, jsonify
from celery import Celery
import uuid
from datetime import timedelta
import redis
import json
from flask.ext.cors import CORS

app = Flask(__name__)
cors = CORS(app)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_TIMEZONE'] = 'UTC'
app.config['CELERYBEAT_SCHEDULE'] = {
    'update_in': {
        'task': 'update_in',
        'schedule': timedelta(seconds=45)
        },
    'update_nearby_devices': {
        'task': 'update_nearby_devices',
        'schedule': timedelta(seconds=15)
        }
}


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
celery = make_celery(app)
r = redis.StrictRedis(host='localhost', port=6379, db=1)


@celery.task(name='update_in')
def update_in():
    persons = {person['id']: person for person in get_redis_persons()}
    for _, person in persons.iteritems():
        for device in person['devices']:
            device = search_for_device(device)

    _persons = get_redis_persons()
    p = r.pipeline()
    for _person in _persons:
        try:
            update_person = persons[_person['id']]
            update_devices = {d['id']: d for d in update_person['devices']}
            for i, _device in enumerate(_person['devices']):
                try:
                    _person['devices'][i] = update_devices[_device['id']]
                except KeyError or IndexError:
                    pass
        except KeyError:
            pass
        for key in _person.keys():
            redis_key = 'person.%s' % _person['id']
            p.hset(redis_key, key, json.dumps(_person[key]))
    p.execute()
    return _persons


@celery.task(name='update_nearby_devices')
def update_nearby_devices():
    devices = []
    for d in bluetooth.discover_devices(duration=5, lookup_names=True):
        try:
            device = {'mac': d[0], 'name': d[1]}
        except IndexError:
            device = {'mac': d[-1], 'name': None}
        devices.append(device)
    r.hset('devices', 'nearby', json.dumps(devices))
    return devices


def get_nearby_devices():
    redis_data = r.hget('devices', 'nearby')
    return json.loads(redis_data)


def search_for_device(device):
    if bluetooth.lookup_name(device.get('mac'), timeout=10):
        device['in'] = True
    else:
        device['in'] = False
    return device


def get_redis_persons():
    person_keys = r.keys('person.*')
    p = r.pipeline()
    for key in person_keys:
        p.hgetall(key)
    redis_data = p.execute()
    persons = []
    for person in redis_data:
        for k, v in person.iteritems():
            try:
                person[k] = json.loads(v)
            except:
                pass
        persons.append(person)
    return persons


def get_redis_person(person_uuid):
    redis_key = 'person.%s' % person_uuid
    redis_data = r.hgetall(redis_key)
    for k, v in redis_data.iteritems():
        try:
            redis_data[k] = json.loads(v)
        except:
            pass
    return redis_data


def set_redis_person(person):
    key_uuid = person['id']
    redis_key = 'person.%s' % key_uuid
    p = r.pipeline()
    for key in person.keys():
        p.hset(redis_key, key, json.dumps(person[key]))
    p.execute()
    return person


def delete_redis_person(person_uuid):
    redis_key = 'person.%s' % person_uuid
    r.delete(redis_key)


def in_status():
    people = get_redis_persons()
    for i, person in enumerate(people):
        if True in map(lambda x: True in x.values(), person['devices']):
            people[i] = {'name': person['name'],
                         'in': True,
                         'id': person['id']}
        else:
            people[i] = {'name': person['name'],
                         'in': False,
                         'id': person['id']}
    return people


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/api/devices/nearby', methods=['GET'])
def list_nearby_devices():
    return jsonify({'nearby_devices': get_nearby_devices()}), 200


@app.route('/api/persons', methods=['GET', 'POST'])
def persons():
    if request.method == 'GET':
        d = get_redis_persons()
        return jsonify({'persons': d}), 200
    if request.method == 'POST':
        if not request.get_json() or 'name' not in request.get_json():
            abort(401)
        person = {'id': str(uuid.uuid4()),
                  'name': request.json['name'],
                  'devices': []}
        for d in request.json['devices']:
            device = {'id': str(uuid.uuid4()),
                      'mac': d['mac'],
                      'desc': d['desc']
                      }
            person['devices'].append(device)
        set_redis_person(person)
        return jsonify({'person': person}), 201


@app.route('/api/persons/<person_uuid>', methods=['GET', 'DELETE'])
def person(person_uuid):
    person = get_redis_person(person_uuid)
    if len(person) == 0:
        abort(404)
    if request.method == 'DELETE':
        delete_redis_person(person_uuid)
    return jsonify({'person': person}), 200


@app.route('/api/persons/<person_uuid>/devices', methods=['GET', 'POST'])
def person_devices(person_uuid):
    person = get_redis_person(person_uuid)
    if len(person) == 0:
        abort(404)
    if request.method == 'GET':
        return jsonify({'devices': person['devices']}), 200
    if request.method == 'POST':
        if not request.get_json() or 'mac' not in request.get_json():
            abort(401)
        device = {'id': str(uuid.uuid4()),
                  'mac': request.json['mac'],
                  'desc': request.json['desc'],
                  }
        person['devices'].append(device)
        set_redis_person(person)
        return jsonify({'device': device}), 201


@app.route('/api/persons/<person_uuid>/devices/<device_uuid>',
           methods=['GET', 'DELETE'])
def person_device(person_uuid, device_uuid):
    person = get_redis_person(person_uuid)
    if len(person) == 0:
        abort(404)
    device = [x for x in person['devices']
              if (unicode(device_uuid) == x['id'])]
    if len(device) == 0:
        abort(404)
    device = device[-1]
    if request.method == 'DELETE':
        person['devices'].remove(device)
        set_redis_person(person)
    return jsonify({'device': device}), 200


@app.route("/api/in")
def people_in():
    status = in_status()
    return jsonify({'status': status}), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1337)
