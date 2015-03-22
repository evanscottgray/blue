# blue
a quick and easy way to see if people are near a location using bluetooth device lookups.

#### up and running
- have python
- have pip
- have bluetooh dongle thing
- have redis-server

in repo directory
```
pip install -r requirements.txt
redis-server &
celery worker -A blue.app.celery --loglevel=info --beat &
python run.py
```

Add some people:

```
# using your favorite http client.
POST /api/persons, Content-Type: application/json

{
    "name": "Cool Guy",
    "devices": [
        {
            "mac": "bluetooth mac here",
            "desc": "cool guy laptop"
        },
        {
            "mac": "6C:40:08:9D:21:41",
            "desc": "cool guy cell phone"
        }
    ]
}
```

List people:
```
# using your favorite http client.
GET /api/persons, Accept: application/json
{
    "persons": [
        {
            "devices": [
                {
                    "desc": "laserbeams",
                    "id": "630c1e35-711c-41b5-ae6a-ae0a6e649bd8",
                    "in": false,
                    "mac": "6C:40:08:9D:21:41"
                }
            ],
            "id": "b85c23ac-53be-4806-ae00-28142dddaa7d",
            "name": "Evan CoolGuy"
        }
    ]
}
```
It's kind of RESTful, you can do a GET /api/persons/<id>/ to view a person, 
a GET /api/persons/<id>/devices to view devices.

Getting devices works too.

Deletes work by doing a DELETE on /api/persons/<id>, they work on devices too.

You can create devices for a person with a post to /api/persons/<id>/devices.
