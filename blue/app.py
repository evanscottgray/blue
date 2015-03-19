import bluetooth
from flask import Flask
from flask import abort, request, jsonify
from celery import Celery
from lib.utils import RedisCache
import uuid
from datetime import timedelta
import redis

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_TIMEZONE'] = 'UTC'
app.config['CELERYBEAT_SCHEDULE'] = {
    'update_in': {
        'task': 'update_in',
        'schedule': timedelta(seconds=30)
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
DB = RedisCache(redis=r, default={'people': []})


@celery.task(name='update_in')
def update_in():
    people = [person for person in DB['people']]
    for i, person in enumerate(people):
        for d, device in enumerate(person.get('devices')):
            if bluetooth.lookup_name(device['mac'], timeout=10):
                people[i]['devices'][d]['in'] = True
            else:
                people[i]['devices'][d]['in'] = False
    DB.load_from_redis()
    updated_people = [person for person in people if person in DB['people']]
    DB['people'] = updated_people
    DB.save()
    return DB['people']


def get_nearby_devices():
    devices = []
    for d in bluetooth.discover_devices(duration=3, lookup_names=True):
        try:
            device = {'mac': d[0], 'name': d[1]}
        except IndexError:
            device = {'mac': d[-1], 'name': None}
        devices.append(device)
    return devices


def in_status():
    people = [person for person in DB.get('people')]
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
    DB.load_from_redis()
    if request.method == 'GET':
        return jsonify({'persons': DB['people']}), 200
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
            DB['people'].append(person)
            print DB
            DB.save()
            DB.load_from_redis()
            print DB
        return jsonify({'person': person}), 201


@app.route('/api/persons/<person_uuid>', methods=['GET', 'DELETE'])
def person(person_uuid):
    DB.load_from_redis()
    person = [x for x in DB['people'] if (unicode(person_uuid) == x['id'])]
    if len(person) == 0:
        abort(404)
    person = person[-1]
    if request.method == 'DELETE':
        DB['people'].remove(person)
        DB.save()
    return jsonify({'person': person}), 200


@app.route('/api/persons/<person_uuid>/devices', methods=['GET', 'POST'])
def person_devices(person_uuid):
    DB.load_from_redis()
    person = [x for x in DB['people'] if (unicode(person_uuid) == x['id'])]
    if len(person) == 0:
        abort(404)
    person = person[-1]
    if request.method == 'GET':
        return jsonify({'devices': person['devices']}), 200
    if request.method == 'POST':
        if not request.get_json() or 'mac' not in request.get_json():
            abort(401)
        device = {'id': str(uuid.uuid4()),
                  'mac': request.json['mac'],
                  'desc': request.json['desc'],
                  'in': True
                  }
        index = DB['people'].index(person)
        person['devices'].append(device)
        DB['people'][index] = person
        DB.save()
        return jsonify({'device': device}), 201


@app.route('/api/persons/<person_uuid>/devices/<device_uuid>',
           methods=['GET', 'DELETE'])
def person_device(person_uuid, device_uuid):
    DB.load_from_redis()
    person = [x for x in DB['people'] if (unicode(person_uuid) == x['id'])]
    if len(person) == 0:
        abort(404)
    person = person[-1]
    device = [x for x in person['devices']
              if (unicode(device_uuid) == x['id'])]
    if len(device) == 0:
        abort(404)
    device = device[-1]
    if request.method == 'DELETE':
        idx = DB['people'].index(person)
        DB['people'][idx]['devices'].remove(device)
        DB.save()
    return jsonify({'device': device}), 200


@app.route("/api/in")
def people_in():
    DB.load_from_redis()
    status = in_status()
    return jsonify({'status': status}), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1337)
