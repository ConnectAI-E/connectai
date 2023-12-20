from time import time

from .globals import current_broker


class BaseStorage(object):
    def set(self, key, value):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def delete(self, key):
        pass

    def has(self, key):
        return True


class DictStorage(BaseStorage):
    def __init__(self, items=dict()):
        super().__init__()
        self.data = items

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data[key]

    def delete(self, key):
        del self.data[key]

    def has(self, key):
        return key in self.data

    def __repr__(self):
        return repr(self.data)


class ExpiredDictStorage(DictStorage):
    def __init__(self, expire=3600, items=dict()):
        self.expire = expire
        super().__init__(items)

    def set(self, key, value):
        return super().set(key, [value, self.expire + time()])

    def get(self, key):
        if not self.has(key):
            raise KeyError
        value, _ = self.data[key]
        return value

    def has(self, key):
        if key in self.data:
            _, expire = self.data[key]
            if expire > time():
                return True
            else:
                del self.data[key]
        return False
