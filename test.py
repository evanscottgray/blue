import bluetooth
import json
from flask import Flask

app = Flask(__name__)

# [{'name': 'bob', 'devices': ['mac address']}]
people = []


def get_in():
    for person in people:
        for device in person.get('devices'):
            if bluetooth.lookup_name(device):
                person['in'] = True
            else:
                person['in'] = False
    return people


@app.route("/in")
def people():
    return json.dumps(get_in())


if __name__ == "__main__":
    app.run(host='0.0.0.0')
