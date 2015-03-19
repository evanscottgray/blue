import json


class FileCache(dict):
    def __init__(self, *args, **kwargs):
        self._filename = kwargs.pop('filename', None)
        dict.__init__(self, *args, **kwargs)
        if self._filename:
            with open(self._filename, 'r') as f:
                self.update(json.load(f))

    def __missing__(self, key):
        if self._filename:
            with open(self._filename, 'r') as f:
                self.update(json.load(f))

            self._filename = None

            if key in self:
                return self[key]

        raise KeyError(key)

    def load_from_disk(self):
        if self._filename:
            with open(self._filename, 'r') as f:
                self.update(json.load(f))

    def save(self, filename=None):
        if self._filename:
            with open(self._filename, 'w') as f:
                json.dump(self, f)
        else:
            with open(filename, 'w') as f:
                json.dump(self, f)


class RedisCache(dict):
    def __init__(self, *args, **kwargs):
        self._redis = kwargs.pop('redis', None)
        self._default = kwargs.pop('default', None)
        self._redis_key = 'redis_cache'
        dict.__init__(self, *args, **kwargs)
        if self._redis:
            d = self._redis.hgetall(self._redis_key)
            for k, v in d.iteritems():
                d[k] = json.loads(v)
            self.update(d)

    def __missing__(self, key):
        if self._redis:
            d = self._redis.hgetall(self._redis_key)
            self.update(d)
            if key in self:
                return self[key]
            else:
                if self._default:
                    if key in self._default:
                        return self._default[key]

        raise KeyError(key)

    def load_from_redis(self):
        if self._redis:
            d = self._redis.hgetall(self._redis_key)
            for k, v in d.iteritems():
                d[k] = json.loads(v)
            self.update(d)

    def save(self):
        if self._redis:
            p = self._redis.pipeline()
            for key in self.keys():
                p.hset(self._redis_key, key, json.dumps(self[key]))
            p.execute()
