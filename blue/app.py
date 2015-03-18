import bluetooth
import json
from flask import Flask

app = Flask(__name__)

people = [{'name': 'evan', 'devices': [{'desc': 'Evan\'s MBP', 'mac': '00:61:71:64:C1:3B', 'in': False}]}]


def get_in():
    for i, person in enumerate(people):
        for d, device in enumerate(person.get('devices')):
            if bluetooth.lookup_name(device['mac']):
                people[i]['devices'][d]['in'] = True
            else:
                people[i]['devices'][d]['in'] = False
    return people


@app.route("/in")
def people_in():
    status = get_in()
    resp = {'people': status}
    return json.dumps(resp)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1337)
